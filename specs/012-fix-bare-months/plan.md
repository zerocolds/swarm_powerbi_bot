# Implementation Plan: Парсинг bare-months в extract_date_params

**Branch**: `012-fix-bare-months` | **Date**: 2026-04-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-fix-bare-months/spec.md`

## Summary

Исправить пропущенную ветку в `extract_date_params()` (`src/swarm_powerbi_bot/services/sql_client.py`): сейчас функция ищет только конструкцию «за <месяц>» (`_RE_MONTH`), игнорируя bare-months (`_RE_MONTH_BARE`), из-за чего запросы «выручка март», «итоги февраля» дают default last-30-days.

Технический подход:
1. Расширить `_RE_MONTH_BARE` падежными классами для «март» и «август» (по аналогии с остальными месяцами). Соблюдать ReDoS-инвариант: плоская альтернация, без вложенных квантификаторов с общим префиксом.
2. Добавить в `extract_date_params()` ветку bare-month, выполняющуюся **до** keyword-периодов («неделя», «месяц», «квартал», «год», «полугодие») и **после** явной конструкции «за <месяц>» / «с X по Y <месяц>» (сохранение обратной совместимости).
3. Добавить structured DEBUG-лог `period_extracted` с полем `strategy` (`bare_month | za_month | range | absolute | keyword | default`) для обеспечения SC-006.
4. Расширить набор юнит-тестов (`tests/test_period_detection.py`) bare-month сценариями: именительный/родительный/дательный/предложный/творительный падежи для всех 12 месяцев, приоритет над keyword-периодом, ≥15 negative-кейсов на составные слова, «сравни март и апрель» → март, regex-страж против ReDoS.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: стандартная библиотека (`re`, `datetime`). Функция изолирована, никаких новых пакетов.
**Storage**: N/A (чистая функция парсинга)
**Testing**: pytest (существующая раскладка `tests/test_period_detection.py` и `tests/test_period_hint.py`).
  - **Стабилизация времени**: все новые тесты, проверяющие конкретные даты, используют **явный год в запросе** («март 2026», «февраль 2025»). Это исключает flakiness на стыке лет и не требует новой dev-зависимости (`freezegun` не вводим). Для тестов, намеренно проверяющих поведение без указания года, используется `monkeypatch` на `swarm_powerbi_bot.services.sql_client.date` (или `date.today`) с фиксированной датой.
**Target Platform**: Linux (Docker), macOS dev
**Project Type**: Single project (Python-библиотека/Telegram-бот)
**Performance Goals**: не существенно; функция вызывается ≤1 раз на запрос пользователя, бюджет <1 мс
**Constraints**:
- Нулевая регрессия по сигнатуре и возвращаемой структуре `{"DateFrom": date, "DateTo": date}`.
- Нулевая регрессия по поведению `has_period_hint()`.
- Изменения только в `src/swarm_powerbi_bot/services/sql_client.py` + расширение тестов.
**Scale/Scope**: локальный фикс в одной функции (~30 строк изменений + ~15 новых тестов).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Принцип | Статус | Комментарий |
|---|---|---|
| I. Spec-Driven Development | PASS | Начали со `spec.md` → `clarify` → `plan`. |
| II. Agent-Only Code | PASS | Код пишется AI-агентом через SDD-пайплайн, прямых ручных правок нет. |
| III. Test-First | PASS | План включает расширение `test_period_detection.py` до реализации; все новые ветки покрыты тестами. SC-004 требует ≥80% ветвей. |
| IV. Multi-Agent Review Gate | PASS | После implement → `speckit.review.run`, `speckit.staff-review.run`, `speckit.verify.run`, `speckit.verify-tasks.run`. Metaswarm не используется. |
| V. Adversarial Review Gate | PASS | После всех speckit-ревью запустим `/speckit.adversarial-review` (DeepSeek ∥ Codex), максимум 3 раунда. |
| VI. Adversarial Diversity | PASS | Claude пишет, DeepSeek + Codex ревьюируют независимо. |
| VII. MAQA для параллельной реализации | N/A | Фича <3 независимых задач; MAQA не требуется. |
| VIII. Документация — часть DoD | PASS | При необходимости обновим `CLAUDE.md` (едва ли потребуется — структура не меняется). |
| IX. Типизация и качество кода | PASS | Сигнатура не меняется; добавляемые ветки используют существующие type hints. `ruff check && ruff format --check`. |
| X. Секреты и конфиденциальные данные | N/A | Секреты не затрагиваются. |

**Вердикт**: все NON-NEGOTIABLE принципы выполнимы без исключений. Complexity Tracking пустой (нарушений нет).

## Project Structure

### Documentation (this feature)

```text
specs/012-fix-bare-months/
├── plan.md                 # Этот файл (/speckit.plan)
├── spec.md                 # /speckit.specify + /speckit.clarify
├── research.md             # Phase 0 output (/speckit.plan)
├── data-model.md           # Phase 1 output (/speckit.plan)
├── quickstart.md           # Phase 1 output (/speckit.plan)
├── contracts/
│   └── extract_date_params.md  # Контракт функции (внутренний API)
├── checklists/
│   └── requirements.md     # Из /speckit.specify
└── tasks.md                # Phase 2 output (/speckit.tasks — будет создан позже)
```

### Source Code (repository root)

```text
src/
└── swarm_powerbi_bot/
    └── services/
        └── sql_client.py           # ← правки: _RE_MONTH_BARE и extract_date_params()

tests/
├── test_period_detection.py        # ← расширение: bare-month тесты
└── test_period_hint.py             # ← регрессионные проверки has_period_hint()
```

**Structure Decision**: Single Python project (`src/swarm_powerbi_bot/`) с плоскими тестами в `tests/`. Раскладка существующая, новых каталогов не создаём.

## Complexity Tracking

> Нарушений Constitution Check нет. Таблица не заполняется.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| —         | —          | —                                   |
