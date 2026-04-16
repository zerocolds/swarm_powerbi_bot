#!/usr/bin/env bash
# adversarial-review.sh — кросс-модельное adversarial ревью через DeepSeek и Codex
# Вызывается из SDD-пайплайна ПОСЛЕ speckit-ревью, ПЕРЕД мержем.
#
# Использование:
#   .specify/scripts/adversarial-review.sh [--round N]
#
# Выход:
#   0 — оба ревьюера PASS, мерж разрешён
#   1 — хотя бы один FAIL, замечания в .maqa/adversarial-findings.md
#   2 — ошибка окружения (нет ollama/codex, не на feature-ветке, и т.д.)

set -euo pipefail

# ── Конфигурация ─────────────────────────────────────────────────────────────
# Используем dirname скрипта для определения корня проекта (swarm_powerbi_bot),
# т.к. git rev-parse --show-toplevel возвращает родительский репозиторий.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
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

check_tool ollama
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

# Находим спецификацию текущей фичи по имени ветки
# Формат ветки: feature/NNN-slug → ищем specs/NNN-*/spec.md
FEATURE_ID=""
if [[ "$CURRENT_BRANCH" =~ ^feature/([0-9]+-[^/]+) ]]; then
  FEATURE_ID="${BASH_REMATCH[1]}"
elif [[ "$CURRENT_BRANCH" =~ ^feature/([0-9]+) ]]; then
  FEATURE_ID="${BASH_REMATCH[1]}"
fi

SPEC_FILE=""
if [[ -n "$FEATURE_ID" ]]; then
  # Точное совпадение по feature ID из имени ветки
  for candidate in "${REPO_ROOT}"/specs/${FEATURE_ID}*/spec.md "${REPO_ROOT}"/.specify/specs/${FEATURE_ID}*/spec.md; do
    if [[ -f "$candidate" ]]; then
      SPEC_FILE="$candidate"
      break
    fi
  done
fi

# Fallback: если по ветке не нашли, берём SPECIFY_FEATURE или единственный spec
if [[ -z "$SPEC_FILE" && -n "${SPECIFY_FEATURE:-}" ]]; then
  for candidate in "${REPO_ROOT}/specs/${SPECIFY_FEATURE}/spec.md" "${REPO_ROOT}/.specify/specs/${SPECIFY_FEATURE}/spec.md"; do
    if [[ -f "$candidate" ]]; then
      SPEC_FILE="$candidate"
      break
    fi
  done
fi

if [[ -z "$SPEC_FILE" ]]; then
  # Последний fallback: единственный spec в директории
  spec_files=("${REPO_ROOT}"/specs/*/spec.md "${REPO_ROOT}"/.specify/specs/*/spec.md)
  found=()
  for f in "${spec_files[@]}"; do
    [[ -f "$f" ]] && found+=("$f")
  done
  if [[ ${#found[@]} -eq 1 ]]; then
    SPEC_FILE="${found[0]}"
  elif [[ ${#found[@]} -gt 1 ]]; then
    echo "⚠️  Найдено ${#found[@]} спецификаций, но не удалось определить текущую фичу из ветки '${CURRENT_BRANCH}'." >&2
    echo "   Подсказка: ветка должна быть в формате feature/NNN-slug или задайте SPECIFY_FEATURE=NNN-slug." >&2
    exit 2
  fi
fi

if [[ -z "$SPEC_FILE" ]]; then
  echo "⚠️  Спецификация не найдена для ветки '${CURRENT_BRANCH}'." >&2
  exit 2
fi

SPEC_CONTENT="$(cat "$SPEC_FILE")"
echo "📋 Используется спецификация: ${SPEC_FILE}"

# ── Подготовка директории результатов ────────────────────────────────────────
mkdir -p "$FINDINGS_DIR"

# ── Промпты ──────────────────────────────────────────────────────────────────
DEEPSEEK_PROMPT="Ты adversarial ревьюер. Твоя задача — найти баги, edge cases, нарушения спецификации, проблемы безопасности и логические ошибки.

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

Spec: see ${SPEC_FILE}
Changes: git diff main...HEAD"

# ── Запуск ревьюеров параллельно ─────────────────────────────────────────────
DEEPSEEK_OUT="${FINDINGS_DIR}/.deepseek-result.txt"
CODEX_OUT="${FINDINGS_DIR}/.codex-result.txt"

echo "🔍 Раунд ${ROUND}: запуск DeepSeek V3.2 и Codex параллельно..."

# DeepSeek V3.2 — через Ollama REST API (chat endpoint, think=false)
# CLI pipe не работает: ANSI escape-коды + thinking mode → пустой response
python3 -c "
import json, sys, urllib.request
payload = json.dumps({
    'model': 'deepseek-v3.2:cloud',
    'messages': [{'role': 'user', 'content': sys.stdin.read()}],
    'stream': False,
    'think': False,
    'options': {'num_predict': 4096}
}).encode()
req = urllib.request.Request('http://localhost:11434/api/chat', data=payload,
                             headers={'Content-Type': 'application/json'})
resp = json.loads(urllib.request.urlopen(req, timeout=300).read())
print(resp.get('message', {}).get('content', ''))
" <<< "$DEEPSEEK_PROMPT" > "$DEEPSEEK_OUT" 2>/dev/null &
DEEPSEEK_PID=$!

# Codex — review mode анализирует diff от main автоматически
codex exec "$CODEX_PROMPT" > "$CODEX_OUT" 2>&1 &
CODEX_PID=$!

# Ждём завершения обоих
DEEPSEEK_EXIT=0
CODEX_EXIT=0
wait "$DEEPSEEK_PID" || DEEPSEEK_EXIT=$?
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

DEEPSEEK_VERDICT="$(parse_verdict "$DEEPSEEK_OUT" "DeepSeek")"
CODEX_VERDICT="$(parse_verdict "$CODEX_OUT" "Codex")"

echo ""
echo "Результаты раунда ${ROUND}:"
echo "  DeepSeek: ${DEEPSEEK_VERDICT}"
echo "  Codex:    ${CODEX_VERDICT}"

# ── Формируем отчёт ──────────────────────────────────────────────────────────
if [[ "$DEEPSEEK_VERDICT" == "PASS" && "$CODEX_VERDICT" == "PASS" ]]; then
  echo ""
  echo "✅ MERGE ALLOWED — оба ревьюера дали PASS"

  # Записываем финальный статус
  cat > "$FINDINGS_FILE" <<EOF
# Adversarial Review — PASSED

**Раунд**: ${ROUND}
**Дата**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
**Ветка**: ${CURRENT_BRANCH}

DeepSeek V3.2: ✅ PASS
Codex:         ✅ PASS

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

    if [[ "$DEEPSEEK_VERDICT" != "PASS" ]]; then
      echo "## DeepSeek V3.2 — ${DEEPSEEK_VERDICT}"
      echo ""
      echo '```'
      cat "$DEEPSEEK_OUT"
      echo '```'
      echo ""
    else
      echo "## DeepSeek V3.2 — ✅ PASS"
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
  rm -f "$DEEPSEEK_OUT" "$CODEX_OUT"

  exit 1
fi
