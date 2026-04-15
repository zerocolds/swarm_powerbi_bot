#!/usr/bin/env bash
# adversarial-review.sh — кросс-модельное adversarial ревью через Gemini и Codex
# Вызывается из SDD-пайплайна ПОСЛЕ speckit-ревью, ПЕРЕД мержем.
#
# Использование:
#   .specify/scripts/adversarial-review.sh [--round N]
#
# Выход:
#   0 — оба ревьюера PASS, мерж разрешён
#   1 — хотя бы один FAIL, замечания в .maqa/adversarial-findings.md
#   2 — ошибка окружения (нет gemini/codex, не на feature-ветке, и т.д.)

set -euo pipefail

# ── Конфигурация ─────────────────────────────────────────────────────────────
REPO_ROOT="$(git rev-parse --show-toplevel)"
FINDINGS_DIR="${REPO_ROOT}/.maqa"
FINDINGS_FILE="${FINDINGS_DIR}/adversarial-findings.md"
ROUND=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --round) ROUND="$2"; shift 2 ;;
    *) echo "Неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
done

# ── Проверка prerequisites ───────────────────────────────────────────────────
check_tool() {
  if ! command -v "$1" &>/dev/null; then
    echo "❌ $1 не найден в PATH. Установите перед запуском." >&2
    exit 2
  fi
}

check_tool gemini
check_tool codex

CURRENT_BRANCH="$(git branch --show-current)"
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
  echo "❌ Скрипт запускается только из feature-ветки, не из ${CURRENT_BRANCH}." >&2
  exit 2
fi

# ── Собираем контекст ────────────────────────────────────────────────────────
DIFF="$(git diff main...HEAD)"
if [[ -z "$DIFF" ]]; then
  echo "⚠️  Нет изменений относительно main. Нечего ревьюить." >&2
  exit 2
fi

# Находим спецификацию текущей фичи
SPEC_CONTENT=""
for spec_file in "${REPO_ROOT}"/.specify/specs/*/spec.md; do
  if [[ -f "$spec_file" ]]; then
    SPEC_CONTENT+="$(cat "$spec_file")"$'\n\n'
  fi
done

if [[ -z "$SPEC_CONTENT" ]]; then
  echo "⚠️  Спецификация не найдена в .specify/specs/*/spec.md" >&2
  exit 2
fi

# ── Подготовка директории результатов ────────────────────────────────────────
mkdir -p "$FINDINGS_DIR"

# ── Промпты ──────────────────────────────────────────────────────────────────
GEMINI_PROMPT="Ты adversarial ревьюер. Твоя задача — найти баги, edge cases, нарушения спецификации, проблемы безопасности и логические ошибки.

Правила ответа:
- Первая строка: PASS или FAIL
- Если FAIL — список замечаний, каждое на новой строке в формате: [SEVERITY] file:line — описание
- SEVERITY: CRITICAL / HIGH / MEDIUM
- Не хвали код. Ищи только проблемы.

Спецификация:
${SPEC_CONTENT}

Diff:
${DIFF}"

CODEX_PROMPT="Review this code for logic errors, security issues, edge cases, and spec violations. Be adversarial — assume bugs exist.

Response format:
- First line: PASS or FAIL
- If FAIL: list findings, each on a new line as: [SEVERITY] file:line — description
- SEVERITY: CRITICAL / HIGH / MEDIUM
- Do not praise. Only report problems.

Spec: see .specify/specs/*/spec.md
Changes: git diff main...HEAD"

# ── Запуск ревьюеров параллельно ─────────────────────────────────────────────
GEMINI_OUT="${FINDINGS_DIR}/.gemini-result.txt"
CODEX_OUT="${FINDINGS_DIR}/.codex-result.txt"

echo "🔍 Раунд ${ROUND}: запуск Gemini и Codex параллельно..."

# Gemini — получает контекст через stdin
echo "$GEMINI_PROMPT" | gemini > "$GEMINI_OUT" 2>/dev/null &
GEMINI_PID=$!

# Codex — получает инструкцию как аргумент, читает файлы сам
codex --approval-mode suggest --quiet "$CODEX_PROMPT" > "$CODEX_OUT" 2>/dev/null &
CODEX_PID=$!

# Ждём завершения обоих
GEMINI_EXIT=0
CODEX_EXIT=0
wait "$GEMINI_PID" || GEMINI_EXIT=$?
wait "$CODEX_PID" || CODEX_EXIT=$?

# ── Парсинг результатов ──────────────────────────────────────────────────────
parse_verdict() {
  local file="$1"
  local name="$2"

  if [[ ! -s "$file" ]]; then
    echo "ERROR"
    echo "  ${name}: пустой ответ или ошибка запуска" >&2
    return
  fi

  local first_line
  first_line="$(head -1 "$file" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')"

  if [[ "$first_line" == "PASS" ]]; then
    echo "PASS"
  else
    echo "FAIL"
  fi
}

GEMINI_VERDICT="$(parse_verdict "$GEMINI_OUT" "Gemini")"
CODEX_VERDICT="$(parse_verdict "$CODEX_OUT" "Codex")"

echo ""
echo "Результаты раунда ${ROUND}:"
echo "  Gemini: ${GEMINI_VERDICT}"
echo "  Codex:  ${CODEX_VERDICT}"

# ── Формируем отчёт ──────────────────────────────────────────────────────────
if [[ "$GEMINI_VERDICT" == "PASS" && "$CODEX_VERDICT" == "PASS" ]]; then
  echo ""
  echo "✅ MERGE ALLOWED — оба ревьюера дали PASS"

  # Записываем финальный статус
  cat > "$FINDINGS_FILE" <<EOF
# Adversarial Review — PASSED

**Раунд**: ${ROUND}
**Дата**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
**Ветка**: ${CURRENT_BRANCH}

Gemini: ✅ PASS
Codex:  ✅ PASS

Мерж разрешён.
EOF

  exit 0
else
  echo ""
  echo "❌ FAIL — замечания сохранены в ${FINDINGS_FILE}"

  # Собираем findings
  {
    echo "# Adversarial Review — FAIL"
    echo ""
    echo "**Раунд**: ${ROUND} / 3"
    echo "**Дата**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "**Ветка**: ${CURRENT_BRANCH}"
    echo ""

    if [[ "$GEMINI_VERDICT" != "PASS" ]]; then
      echo "## Gemini — ${GEMINI_VERDICT}"
      echo ""
      echo '```'
      cat "$GEMINI_OUT"
      echo '```'
      echo ""
    else
      echo "## Gemini — ✅ PASS"
      echo ""
    fi

    if [[ "$CODEX_VERDICT" != "PASS" ]]; then
      echo "## Codex — ${CODEX_VERDICT}"
      echo ""
      echo '```'
      cat "$CODEX_OUT"
      echo '```'
      echo ""
    else
      echo "## Codex — ✅ PASS"
      echo ""
    fi

    if [[ "$ROUND" -ge 3 ]]; then
      echo "---"
      echo "## ⚠️ Достигнут лимит раундов (3/3)"
      echo "Требуется эскалация на человека."
    fi
  } > "$FINDINGS_FILE"

  # Чистим временные файлы
  rm -f "$GEMINI_OUT" "$CODEX_OUT"

  exit 1
fi
