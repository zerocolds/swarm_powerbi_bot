---
description: "Task list for 012-fix-bare-months"
---

# Tasks: Парсинг bare-months в extract_date_params

**Input**: Design documents from `/specs/012-fix-bare-months/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/extract_date_params.md](./contracts/extract_date_params.md)

**Tests**: Tests включены и обязательны по Constitution Principle III (Test-First, NON-NEGOTIABLE). Целевое покрытие — ≥60% / цель 80%; для новой логики — по SC-004 ≥80% ветвей.

**Organization**: Tasks сгруппированы по user story (US1 → US2 → US3) с обязательным разделом Foundational (общий код правок) перед ними, т.к. исправление локально в одной функции и атомарно. После всех US — Polish с negative-тестами, ReDoS-стражем и проверкой логирования.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Можно запускать в параллель (разные файлы или независимые тестовые функции).
- **[Story]**: К какой user story относится задача (US1, US2, US3). Setup/Foundational/Polish — без тега.
- Каждая задача содержит точный путь к файлу.

## Path Conventions

- **Single project** (Python): `src/swarm_powerbi_bot/`, `tests/` в корне репозитория.
- Все пути относительны `swarm_powerbi_bot/` (Python-package root — см. plan.md → Project Structure).

---

## Phase 1: Setup

**Purpose**: Зафиксировать исходное состояние тестов перед правками.

- [X] T001 Запустить baseline-пайплайн: `uv run pytest tests/test_period_detection.py tests/test_period_hint.py -v` и сохранить вывод. Убедиться, что текущие тесты проходят; заметить, что нет покрытия bare-month.

---

## Phase 2: Foundational (Shared Code Changes)

**Purpose**: Атомарные изменения в `src/swarm_powerbi_bot/services/sql_client.py`, от которых зависят все три user story. После этой фазы существующий набор регрессионных тестов должен продолжать проходить.

**⚠️ CRITICAL**: Ни одна US-фаза не может быть завершена без этих правок.

- [X] T002 Расширить `_RE_MONTH_BARE` в `src/swarm_powerbi_bot/services/sql_client.py`: добавить падежные окончания для «март» и «август» (родительный/дательный/предложный/творительный через `(?:а|у|е|ом)?`), а также творительный падеж для всех остальных месяцев (через расширение группы до `(?:я|е|ю|и|ём|ем|ь)?`). Соблюсти ReDoS-инвариант I-7 (плоские альтернации, без вложенных квантификаторов) — см. `research.md` R-002 и R-007.
- [X] T003 Добавить новую ветку bare-month в `extract_date_params()` в `src/swarm_powerbi_bot/services/sql_client.py` сразу **после** веток `«вчера» / «сегодн»` и **до** ключевых слов периода (`«недел»`, `«месяц»`, `«квартал»`, `«полугод»`, `«год»`), согласно порядку проверок в `research.md` R-001 и `contracts/extract_date_params.md` (Decision Order). В ветке использовать `_RE_MONTH_BARE.search()` и `_match_month()`; вернуть `{DateFrom: первый день, DateTo: последний день месяца}` с учётом 28/29/30/31 и високосного февраля.
- [X] T004 Добавить ровно одно DEBUG-сообщение `period_extracted` перед каждым `return` в `extract_date_params()` в `src/swarm_powerbi_bot/services/sql_client.py`, через существующий `logger`. Полями `extra` передать `strategy` ∈ {`bare_month`, `za_month`, `range`, `absolute`, `keyword`, `default`}, `date_from`, `date_to`, `question_len`. **Не** логировать полный текст `question` (см. `research.md` R-008 и contract I-8).

**Checkpoint**: После T002–T004 запустить `uv run pytest tests/test_period_detection.py tests/test_period_hint.py -q` — старые тесты должны остаться green; новых тестов ещё нет.

---

## Phase 3: User Story 1 — Bare-month парсинг (Priority: P1) 🎯 MVP

**Goal**: Запросы вида «выручка март», «итоги марта», «в августе 2025» возвращают период запрошенного месяца, включая все 12 месяцев × пять падежных форм и явно указанный год (с проверкой високосного февраля).

**Independent Test**: `uv run pytest tests/test_period_detection.py -k "bare_month or padezh or explicit_year or leap or priority_over_keyword" -v` — все новые тесты проходят; в лог-сообщениях `strategy="bare_month"`.

### Tests for User Story 1 (Test-First, обязательно)

> **NOTE**: Тесты пишутся и пушатся первыми; они должны **FAIL** до мёржа T002–T004 и **PASS** после. Если Foundational уже слит, тесты фиксируют новое поведение.

- [X] T005 [P] [US1] Написать параметризованный тест `test_bare_month_nominative_all_12_months` в `tests/test_period_detection.py`: 12 кейсов («выручка январь 2026», «услуги февраль 2025», …, «отчёт декабрь 2026»); проверяют `DateFrom=первый день` и `DateTo=последний день`. Всегда с явным годом (см. plan.md → Testing).
- [X] T006 [P] [US1] Написать параметризованный тест `test_bare_month_cases` в `tests/test_period_detection.py`: не менее 8 кейсов падежных форм — «итоги марта 2026», «отчёту февралю 2026», «в апреле 2026», «мартом 2026», «августом 2025», «в сентябре 2026», «к октябрю 2026», «январём 2024». Проверяет FR-001.
- [X] T007 [P] [US1] Написать тест `test_bare_month_leap_year` в `tests/test_period_detection.py`: «февраль 2024» → `2024-02-01..2024-02-29`; «февраль 2025» → `2025-02-01..2025-02-28`; «февраль 2100» → `2100-02-28` (не високосный); «февраль 2000» → `2000-02-29` (високосный по правилу divisible-by-400). Проверяет FR-002, I-6.
- [X] T008 [P] [US1] Написать тест `test_bare_month_priority_over_keyword` в `tests/test_period_detection.py`: «отчёт за месяц март 2026» → март 2026; «за неделю июня 2026» → весь июнь 2026; «за год январь 2025» → весь январь 2025; «за квартал октября 2025» → весь октябрь 2025. Проверяет FR-008.

### Implementation for User Story 1

Логика реализована в Phase 2 (T002–T004). В этой фазе — только расширение тестов.

- [X] T009 [US1] Запустить `uv run pytest tests/test_period_detection.py -k "bare_month or padezh or leap or priority_over_keyword" -v` — все тесты US1 должны быть GREEN.

**Checkpoint**: US1 (MVP) работает независимо — можно деплоить/показывать.

---

## Phase 4: User Story 2 — Сохранение поведения «за <месяц>» (Priority: P1)

**Goal**: Все существующие запросы с предлогом «за», диапазоны «с X по Y», абсолютные якоря («вчера», «сегодня») и keyword-периоды («неделя», «квартал», «полугодие», «год») работают так же, как и до фикса. Нулевая регрессия.

**Independent Test**: `uv run pytest tests/test_period_detection.py tests/test_period_hint.py -k "regression or za_month or range or keyword" -v` — все тесты green.

### Tests for User Story 2

- [X] T010 [P] [US2] Написать/расширить тесты `test_regression_za_month_*` в `tests/test_period_detection.py`: «выручка за март 2025» → `2025-03-01..2025-03-31`; «за январь 2025» → `2025-01-01..2025-01-31`; «за декабрь 2024» → `2024-12-01..2024-12-31` (граница года). Проверяет FR-004.
- [X] T011 [P] [US2] Написать тесты `test_regression_range` и `test_regression_absolute_anchors` в `tests/test_period_detection.py`: «с 5 по 20 апреля 2025», «с 1 по 15 марта 2026»; «что было вчера», «за сегодня» — поведение не изменилось.
- [X] T012 [P] [US2] Написать параметризованный тест `test_regression_keyword_periods` в `tests/test_period_detection.py`: «за неделю», «за квартал», «за полгода», «за год», «за месяц» — возвращают скользящие окна (7/90/180/365/30 дней) от `date.today()`. Использовать `monkeypatch` на `sql_client.date` с фиксированной датой 2026-04-17 для стабильности.
- [X] T013 [P] [US2] Написать тест `test_za_month_beats_bare_month` в `tests/test_period_detection.py`: «за январь 2025 февраль» → январь 2025 (bare «февраль» игнорируется). Проверяет FR-005 и пример из Edge Cases.

### Implementation for User Story 2

Реализация полностью обеспечена Phase 2; новой кодовой правки не требуется.

- [X] T014 [US2] Запустить `uv run pytest tests/test_period_detection.py -k "regression or za_month_beats" -v` — все тесты US2 должны быть GREEN.

**Checkpoint**: US1 и US2 работают независимо, регрессий нет.

---

## Phase 5: User Story 3 — Comparison single-query fallback (Priority: P2)

**Goal**: При multi-bare-month запросе («сравни март и апрель») single-query fallback возвращает период первого упомянутого месяца, а не default last-30-days.

**Independent Test**: `uv run pytest tests/test_period_detection.py -k "compare_first_month" -v` — все тесты green.

### Tests for User Story 3

- [X] T015 [P] [US3] Написать тест `test_compare_first_month_wins` в `tests/test_period_detection.py`: «сравни март 2026 и апрель 2026» → `2026-03-01..2026-03-31`; «разница между январём и февралём 2025» → `2025-01-01..2025-01-31`; «май vs июнь 2026» → `2026-05-01..2026-05-31`. Проверяет FR-006.
- [X] T016 [P] [US3] Написать тест `test_compare_with_explicit_year_on_first` в `tests/test_period_detection.py`: «сравни январь 2025 и февраль 2026» → январь 2025 (первый месяц со своим годом).

### Implementation for User Story 3

Реализация полностью обеспечена Phase 2; новой кодовой правки не требуется.

- [X] T017 [US3] Запустить `uv run pytest tests/test_period_detection.py -k "compare_first_month or compare_with_explicit_year" -v` — все тесты US3 должны быть GREEN.

**Checkpoint**: Все три US работают независимо.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Гарантии отсутствия ложных срабатываний, ReDoS-защита, регрессия `has_period_hint()`, structured-logging контракт, полный pytest-run, lint, quickstart-валидация и, при необходимости, обновление CLAUDE.md.

- [X] T018 [P] Написать параметризованный тест `test_bare_month_no_false_positives` в `tests/test_period_detection.py`: ≥15 negative-кейсов на составные слова — «январский», «февральский», «мартышка», «апрельский», «майонез», «июньский», «июльский», «августовский», «сентябрьский», «октябрятский», «ноябрьский», «декабрьский», «мартини», «маяковский», «подмайский». Каждый → default last-30-days; `has_period_hint(...)` = False. Соответствует SC-003 и R-006.
- [X] T019 [P] Написать тест `test_redos_guard` в `tests/test_period_detection.py`: `extract_date_params("а" * 10_000)` и `has_period_hint("а" * 10_000)` завершаются за <10 мс каждый и не бросают исключений. Использовать `time.perf_counter()`. Соответствует I-7.
- [X] T020 [P] Написать параметризованный тест `test_has_period_hint_bare_month_all_cases` в `tests/test_period_hint.py`: 12 месяцев × ≥2 формы (именительный + творительный) → `has_period_hint` = True. Также добавить 3 negative-кейса (из T018-набора) → False. Проверяет FR-009.
- [X] T021 [P] Написать тест `test_period_extracted_log_strategy` в `tests/test_period_detection.py` с фикстурой `caplog`: для 6 стратегий (`bare_month`, `za_month`, `range`, `absolute`, `keyword`, `default`) проверить, что в `caplog.records` есть ровно одно DEBUG-сообщение `period_extracted` с соответствующим `extra["strategy"]`. Проверяет FR-011 / I-8.
- [X] T022 [P] Написать тест `test_bare_month_without_year_uses_today_year` в `tests/test_period_detection.py`: через `monkeypatch` заменить `swarm_powerbi_bot.services.sql_client.date.today` (или импортируемый `date`) на фиксированную дату 2026-04-17; проверить «выручка март» → `2026-03-01..2026-03-31». Проверяет FR-003 и strategy=bare_month в логе.
- [X] T023 Запустить `uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/`. Исправить замечания (если есть); при необходимости применить `uv run ruff format src/ tests/`.
- [X] T024 Запустить полный `uv run pytest -q`. Убедиться: 0 регрессий в `test_comparison.py`, `test_keyword_fallback.py`, `test_multi_query.py`, `test_orchestrator.py`, `test_planner*.py`, `test_analyst_fallback.py`.
- [X] T025 Выполнить `quickstart.md` секции 1–4.2 вручную: проверить REPL-вывод, ReDoS-страж, structured logging. Сверить с expected в `specs/012-fix-bare-months/quickstart.md`.
- [X] T026 Проверить `CLAUDE.md` в корне `swarm_powerbi_bot/`: обновлён ли агент-контекст (сделано скриптом `/speckit.plan`), нет ли конфликтов MANUAL ADDITIONS; при необходимости — минимальные правки.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup) → Phase 2 (Foundational)**: T001 должен быть запущен до T002–T004 для фиксации baseline.
- **Phase 2 (Foundational) → Phase 3–5 (US1/US2/US3)**: все US зависят от T002–T004. Без этих правок новые тесты будут падать (US1/US3) или не будут проверять новую стратегию в логах (US2).
- **Phase 6 (Polish)**: после завершения всех US и их checkpoints.

### User Story Dependencies

- **US1 (P1, MVP)**: зависит только от Phase 2. Полностью независима.
- **US2 (P1)**: зависит только от Phase 2. Полностью независима от US1/US3.
- **US3 (P2)**: зависит только от Phase 2. Полностью независима от US1/US2.

### Within Each User Story

- Все тестовые задачи (T005–T008, T010–T013, T015–T016) пишутся в разные функции одного файла `tests/test_period_detection.py` — допустимо параллелить при условии уникальных имён тестов.
- После написания тестов в фазе — запуск pytest (T009, T014, T017) должен быть GREEN.

### Parallel Opportunities

- T002/T003/T004 — частично параллельны (T002 и T004 в разных местах одного файла; T003 идёт после T002, т.к. использует расширенный regex). Безопаснее сериализовать.
- T005–T008 — параллельны (разные тестовые функции).
- T010–T013 — параллельны (разные тестовые функции).
- T015–T016 — параллельны.
- T018–T022 — параллельны (разные функции в разных файлах).
- T023 и T024 — последовательно (сначала ruff, потом pytest).

---

## Parallel Example: User Story 1

```bash
# После завершения Phase 2 можно писать тесты US1 в параллель:
Task: "Параметризованный тест именительного падежа 12 месяцев (T005) в tests/test_period_detection.py"
Task: "Параметризованный тест падежных форм (T006) в tests/test_period_detection.py"
Task: "Тест високосного февраля (T007) в tests/test_period_detection.py"
Task: "Тест приоритета bare-month над keyword (T008) в tests/test_period_detection.py"

# Все четыре добавляются как новые def test_*() в один файл; одновременные правки
# разных тестовых функций безопасны, т.к. merge-конфликты касаются только концов файла.
```

---

## Implementation Strategy

### MVP First (US1)

1. T001 — baseline.
2. T002–T004 — shared code changes (Foundational).
3. T005–T009 — US1 тесты и проверка.
4. **STOP and VALIDATE**: US1 проходит независимо. Можно мержить MVP-инкремент.

### Incremental Delivery

1. Phase 2 + US1 → MVP (basic bare-month support).
2. + US2 → гарантия нулевой регрессии.
3. + US3 → comparison fallback.
4. + Polish → полный набор negative-тестов, ReDoS-страж, structured-logging контракт, full pytest, ruff, quickstart.

### Parallel Team Strategy

Фича мелкая (одна функция), поэтому MAQA-coordinator не применяется (см. plan.md Constitution Check VII). Один feature-агент (Claude Sonnet) исполняет весь план; QA-агент (Opus) проверяет перед мержем.

---

## Summary

| Phase | Tasks | Description |
|---|---|---|
| 1 | T001 | Baseline |
| 2 | T002–T004 | Shared code (regex + ветка + logger) |
| 3 (US1) | T005–T009 | Bare-month nominative + cases + year + priority |
| 4 (US2) | T010–T014 | Regression preservation |
| 5 (US3) | T015–T017 | Comparison first-match |
| 6 (Polish) | T018–T026 | Negatives, ReDoS, has_period_hint, logging, ruff, pytest, quickstart |

**Total**: 26 задач.
**MVP scope**: T001–T009 (9 задач) → US1 работает независимо.
**Parallel opportunities**: T005–T008, T010–T013, T015–T016, T018–T022 — параллельны внутри своих фаз.

## Notes

- [P] = разные тестовые функции или разные файлы; правки внутри одной функции `extract_date_params()` (T002–T004) сериализованы.
- Тесты пишутся раньше реализации по Constitution III (Test-First), но на практике для bugfix в одной функции разумнее сначала ввести тесты в PR-коммит, затем Foundational-патч, чтобы RED→GREEN был явно виден в CI.
- Коммитить после каждой группы (phase-end или checkpoint) через `speckit.git.commit`.
- Avoid: смешивание code-правок из T002–T004 в одну большую диффу без разделения по инварианту.

---

## Phase 7: Adversarial Review Round 4 (post-review fixes)

**Purpose**: Устранить критические и важные находки из `/speckit.review.run` (round 2): FR-001 gap для май падежных форм, I-1 violations в range-ветке и `_month_range`, флаки-тесты из-за `date.today()` и hardcoded `year=2026`, защитная изоляция `logger.debug`.

**⚠️ Найдено в двух параллельных review-раундах (идентичные выводы)**:
- C-1: `_MONTH_MAP` не содержит стемов `мае/маю/маем` → `_match_month("маю") == 0` → bare-month ветка пропускается → нарушение FR-001.
- E-1: `_RE_RANGE` ветка и `_month_range` бросают `ValueError` на `"с 30 по 31 февраля 2025"` / `"январь 0000"` → нарушение I-1 «никогда не бросает».

### Tests (Test-First)

- [X] T027 [P] Добавить параметры для май падежных форм в `test_bare_month_padezh_cases` в `tests/test_period_detection.py`: `("в мае 2026", 2026, 5, 31)`, `("маю 2026", 2026, 5, 31)`, `("маем 2026", 2026, 5, 31)`. Тест должен **FAIL** до T029. Проверяет FR-001 для стема `май`.
- [X] T028 [P] Добавить параметризованный тест `test_invariant_i1_edge_inputs` в `tests/test_period_detection.py` с кейсами: `"с 30 по 31 февраля 2025"`, `"с 1 по 32 марта 2026"`, `"январь 0000"`. Для каждого: `extract_date_params(...)` не бросает и возвращает default last-30-days (или bare_month с валидным годом если regex его отклоняет). Проверяет I-1.

### Implementation

- [X] T029 Добавить в `_MONTH_MAP` в `src/swarm_powerbi_bot/services/sql_client.py` стемы `"мае": 5, "маю": 5, "маем": 5`. Порядок вставки — между `"май": 5` и `"июн": 6` (после май-стема, чтобы `startswith` не ломал поиск).
- [X] T030 Обернуть обращения к `date(...)` в range-ветке (строки ~161-163) и к `_month_range(...)` (строки ~149, ~181) в `try/except ValueError` внутри `extract_date_params()` в `src/swarm_powerbi_bot/services/sql_client.py`. В `except` — `_result("default", today - timedelta(days=30), today, question)`. Инвариант I-1.
- [X] T031 Обернуть `logger.debug(...)` в `_result()` в `src/swarm_powerbi_bot/services/sql_client.py` в `try/except Exception: pass` для защиты от возможных формат-collision в downstream-логгерах. Инвариант I-1 belt-and-suspenders. Не менять сам контракт `extra` (strategy/date_from/date_to/question_len).

### Test-stability refactor

- [X] T032 [P] Вынести `_FixedDate` класс из локальных фикстур в `tests/test_period_detection.py` в модуль-уровень (если ещё не там) и применить autouse-фикстуру `freeze_today` через `monkeypatch.setattr(sql_client, "date", _FixedDate)` на фиксированную дату `2026-04-17`. Устраняет флаки в `test_extract_yesterday`, `test_extract_today`, `test_extract_week`, `test_extract_half_year`, `test_extract_default_30_days`, `test_regression_absolute_anchors`, `test_bare_month_no_false_positives`, `test_regression_keyword_periods`, и hardcoded `year=2026` в `test_bare_month_nominative_all_12_months` / `test_bare_month_priority_over_keyword`. Проверить что existing tests passing с зафиксированной датой.

### Validation

- [X] T033 Запустить `uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/`. При необходимости применить `uv run ruff format src/ tests/`.
- [X] T034 Запустить полный `uv run pytest -q`. Убедиться: 0 регрессий (≥537 passed), новые тесты T027/T028 проходят.

### Dependencies

- T027 → T029 (тест FAIL до фикса)
- T028 → T030 (тест FAIL до фикса)
- T032 может идти параллельно — независим от T027-T031.
- T033/T034 — финал после всего.

---

## Phase 8: Review Round 5 (post-round-4 fixes)

**Purpose**: Закрыть Important findings из `/speckit.review.run` round 5 (6 агентов в параллель): стейлые T-IDs в test_period_hint.py, непокрытие I-5/empty-string/«новый год»/I-3-I-4, слишком широкий `except Exception` в `_result`, misleading comment на `_MONTH_MAP`.

### Implementation

- [X] T035 Переименовать функции `test_T018_*..test_T021_*` в `tests/test_period_hint.py` в `test_bare_month_in_question`, `test_compare_two_months`, `test_backward_compat_month_with_za`, `test_no_period_hint`. Исправить docstring модуля: убрать несуществующие `T018..T021 [US4]` теги (они не соответствуют реальным задачам в tasks.md). Comment-agent finding Important #1.
- [X] T036 Добавить `test_i5_case_insensitive` (parametrize) в `tests/test_period_detection.py`: `"ВЫРУЧКА МАРТ"`, `"Март 2026"`, `"НОЯБРЁМ 2025"`, `"за Январь 2024"`, `"ВЫРУЧКА МАРТА 2026"`. Закрывает I-5. Tests-agent finding Important #2.
- [X] T037 Добавить `test_i1_empty_or_whitespace_input` (parametrize) в `tests/test_period_detection.py`: `""`, `"   "`, `"\n\t  "`, `"\t"`. Должны возвращать default last-30-days. Tests-agent finding Important #3.
- [X] T038 Добавить `test_novy_god_not_parsed_as_year` в `tests/test_period_detection.py`: `extract_date_params("новый год")` → default. Покрывает carveout на [sql_client.py:218](../../src/swarm_powerbi_bot/services/sql_client.py). Tests-agent finding Important #4.
- [X] T039 Добавить `test_i3_i4_return_shape_exactly_two_date_keys` в `tests/test_period_detection.py`: `set(params.keys()) == {"DateFrom","DateTo"}` + `isinstance(..., date)` + `not isinstance(..., datetime)`. Закрывает I-3/I-4. (Нельзя использовать `type(...) is date` из-за autouse `_FixedDate` fixture.) Tests-agent finding.
- [X] T040 В `src/swarm_powerbi_bot/services/sql_client.py:131` сузить `except Exception` до `except (KeyError, TypeError)` вокруг `logger.debug`. Это реальные модусы отказа (LogRecord reserved-name collision + bad `extra` shape); `MemoryError`/программерские баги должны всплывать. Errors-agent finding Important #5.
- [X] T041 Переписать комментарий к `_MONTH_MAP` май-стемам в `src/swarm_powerbi_bot/services/sql_client.py:33-35`: явно указать, что «маем» ловится префиксом «мае» через `startswith`, не требует отдельного стема. Simplify-agent finding F1.
- [X] T042 Спавн follow-up task «Introduce DateParams TypedDict» через `mcp__ccd_session__spawn_task` — cross-file refactor (`planner.py`, `analyst.py`, `chart_renderer.py` + `sql_client.py`) вне scope этого bugfix. Types-agent finding Finding 3.

### Validation

- [X] T043 `uv run ruff check src/ tests/ && uv run ruff format --check src/swarm_powerbi_bot/services/sql_client.py tests/test_period_detection.py tests/test_period_hint.py`.
- [X] T044 Полный `uv run pytest -q`. Результат: **555 passed** (544 + 11 новых: 5 I-5 + 4 I-1 пустая строка + 1 новый год + 1 shape), 0 регрессий.

---

## Phase 9: Review Round 6 (warnings + high-ROI suggestions)

**Purpose**: Закрыть 3 warnings (W-1/W-2/W-3) и применить 2 высокоценных suggestion (S-2 parametrize across strategies, S-3 readable ids) из `/speckit.review.run` round 6. Отложены: F2 drop-the-wrapper, minor comment nits, `"\t"` redundancy (per user decision).

### Implementation

- [X] T045 W-1/W-3: Ужесточить `test_i5_case_insensitive` в `tests/test_period_detection.py` — проверять полный `DateFrom`/`DateTo` (`date(2026, 3, 1)` … `date(2026, 3, 31)` и т.п.) для всех 5 параметров вместо только месяца. Code-agent finding Warning #1.
- [X] T046 W-1/W-3: Ослабить `test_i1_empty_or_whitespace_input` в `tests/test_period_detection.py` — проверять инвариант (`isinstance(params["DateFrom"], date) and params["DateFrom"] <= params["DateTo"]`) вместо конкретной default-стратегии. Убрать redundant `"\t"` (покрыт `"\n\t  "`). Code-agent finding Warning #3.
- [X] T047 W-2: Параметризовать `test_novy_god_not_parsed_as_year` в `tests/test_period_detection.py` с `["новый год", "новый год 2026"]`. Задокументировать известную узость carveout: падежные формы вроде «новым годом» попадают в year-keyword branch (подстроки «новый год» нет). Tests-agent finding Warning #2.
- [X] T048 S-2: Расширить `test_i3_i4_return_shape_exactly_two_date_keys` → `test_i3_i4_return_shape_all_strategies` с parametrize по 6 стратегиям (bare_month, za_month, range, absolute, keyword, default). Code-agent finding Suggestion #2.
- [X] T049 S-3: Добавить `ids=[...]` во все parametrize-блоки (test_i5, test_i1, test_novy_god, test_i3_i4) — читаемые CI-логи. Code-agent finding Suggestion #3.

### Validation

- [X] T050 `uv run ruff check src/ tests/ && uv run ruff format src/ tests/`.
- [X] T051 Полный `uv run pytest -q`. Результат: **560 passed** (555 → 560: +5 из S-2 parametrize, −1 из carveout-ограничения, +1 из расширенных вариантов), 0 регрессий.
