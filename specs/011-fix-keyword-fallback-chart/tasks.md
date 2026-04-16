# Tasks: Исправление маршрутизации и chart rendering

**Input**: Design documents from `/specs/011-fix-keyword-fallback-chart/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Включены — конституция требует Test-First (Принцип III).

**Organization**: Tasks grouped by user story (US1-US4) для независимой реализации и тестирования.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Нет инфраструктурных задач — проект уже настроен, все зависимости установлены.

*Пропущена — нет setup-задач.*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Нет blocking prerequisites — все 4 user stories работают с разными файлами и могут начинаться сразу.

*Пропущена — нет foundational-задач.*

---

## Phase 3: User Story 1 — Улучшение keyword fallback маршрутизации (Priority: P1) 🎯 MVP

**Goal**: Keyword fallback в `detect_topic()` корректно маршрутизирует вопросы с контекстом периода и ranking.

**Independent Test**: Вызвать `detect_topic("какая выручка за неделю?")` → `statistics`, `detect_topic("кто больше принёс денег?")` → `masters`, `detect_topic("популярные услуги")` → `services`.

### Tests for US1

- [x] T001 [P] [US1] Тест keyword fallback scoring: контекстные правила для «выручка + период → statistics» в `tests/test_keyword_fallback.py`
- [x] T002 [P] [US1] Тест keyword fallback: «кто больше принёс денег» → masters в `tests/test_keyword_fallback.py`
- [x] T003 [P] [US1] Тест keyword fallback: прямые маппинги сохраняются («популярные услуги» → services, «отток» → outflow) в `tests/test_keyword_fallback.py`

### Implementation for US1

- [x] T004 [US1] Добавить контекстные правила `_CONTEXT_RULES` в `src/swarm_powerbi_bot/services/topic_registry.py` — boost для statistics при период + «выручк», boost для masters при ranking + финансы
- [x] T005 [US1] Обновить `detect_topic()` в `src/swarm_powerbi_bot/services/topic_registry.py` — применять `_CONTEXT_RULES` после базового scoring
- [x] T006 [US1] Добавить circuit breaker в `plan_query()` в `src/swarm_powerbi_bot/services/llm_client.py` — переиспользовать CB state из `__init__`, аналогично `plan_aggregates()`

**Checkpoint**: `detect_topic()` корректно маршрутизирует 10 тестовых вопросов. `plan_query()` защищён circuit breaker.

---

## Phase 4: User Story 2 — Ответ без сырых SQL field names (Priority: P1)

**Goal**: Fallback summary не содержит PascalCase/camelCase SQL field names. Все поля переведены или скрыты.

**Independent Test**: Вызвать `_fallback_summary()` с данными services/masters → ответ не содержит raw SQL names.

### Tests for US2

- [x] T007 [P] [US2] Тест: все поля services-темы переведены или скрыты в `tests/test_field_labels.py`
- [x] T008 [P] [US2] Тест: все поля masters-темы переведены или скрыты в `tests/test_field_labels.py`
- [x] T009 [P] [US2] Тест: неизвестное поле (не в _FIELD_LABELS и не в _HIDDEN_FIELDS) пропускается в fallback summary в `tests/test_field_labels.py`

### Implementation for US2

- [x] T010 [P] [US2] Дополнить `_FIELD_LABELS` в `src/swarm_powerbi_bot/agents/analyst.py` — добавить ServiceCategory, ServiceCount, MasterCategory, Rating, ReturningClients, TotalHours, EndOfWeek, WeekLabel
- [x] T011 [P] [US2] Дополнить `_HIDDEN_FIELDS` в `src/swarm_powerbi_bot/agents/analyst.py` — добавить IsPrimary, ServiceCategory, MasterCategory
- [x] T012 [US2] Изменить `_fallback_summary()` в `src/swarm_powerbi_bot/agents/analyst.py` — пропускать поля без маппинга в `_FIELD_LABELS` (не показывать raw name)

**Checkpoint**: Fallback summary для всех тем показывает только русские названия полей. Неизвестные поля скрыты.

---

## Phase 5: User Story 3 — Chart по релевантной метрике (Priority: P2)

**Goal**: Chart value axis = осмысленная метрика (не boolean, не ID).

**Independent Test**: `_pick_label_value(rows, "services")` → value_col = `ServiceCount` (не `IsPrimary`).

### Tests for US3

- [x] T013 [P] [US3] Тест: _PREFERRED_VALUE["services"] = ServiceCount в `tests/test_chart_preferred.py`
- [x] T014 [P] [US3] Тест: _PREFERRED_VALUE["masters"] = TotalRevenue в `tests/test_chart_preferred.py`
- [x] T015 [P] [US3] Тест: boolean-поле (IsPrimary) пропускается при выборе value axis в `tests/test_chart_preferred.py`

### Implementation for US3

- [x] T016 [P] [US3] Исправить `_PREFERRED_VALUE` в `src/swarm_powerbi_bot/services/chart_renderer.py` — services→ServiceCount, masters→TotalRevenue
- [x] T017 [US3] Обновить `_pick_label_value()` в `src/swarm_powerbi_bot/services/chart_renderer.py` — добавить IsPrimary в skip set, добавить проверку `isinstance(val, bool)` для исключения boolean-полей

**Checkpoint**: Chart для services показывает ServiceCount, для masters — TotalRevenue. Boolean-поля исключены из value axis.

---

## Phase 6: User Story 4 — «Сравни март и апрель» без кнопок периода (Priority: P2)

**Goal**: `has_period_hint()` распознаёт месяцы без предлога «за».

**Independent Test**: `has_period_hint("сравни март и апрель")` → `True`.

### Tests for US4

- [x] T018 [P] [US4] Тест: «выручка март» → True в `tests/test_period_hint.py`
- [x] T019 [P] [US4] Тест: «сравни март и апрель» → True в `tests/test_period_hint.py`
- [x] T020 [P] [US4] Тест: «отток за прошлый месяц» → True (обратная совместимость) в `tests/test_period_hint.py`
- [x] T021 [P] [US4] Тест: «как дела» → False (false positive protection) в `tests/test_period_hint.py`

### Implementation for US4

- [x] T022 [US4] Добавить `_RE_MONTH_BARE` regex в `src/swarm_powerbi_bot/services/sql_client.py` — месяцы без «за» с word boundaries `\b`
- [x] T023 [US4] Обновить `has_period_hint()` в `src/swarm_powerbi_bot/services/sql_client.py` — добавить проверку `_RE_MONTH_BARE.search(text)`

**Checkpoint**: «Сравни март и апрель» не показывает кнопки периода.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Интеграционные тесты и документация.

- [x] T024 [P] Расширить `test_planner_10_questions` в `tests/integration/test_real_llm.py` — добавить проверку keyword fallback path (mock LLM → None)
- [x] T025 [P] Расширить `test_e2e_fallback_no_raw_fields` в `tests/integration/test_real_e2e.py` — добавить проверку новых полей (ServiceCategory, MasterCategory, IsPrimary)
- [x] T026 Запустить `uv run pytest -q && uv run ruff check src/ tests/` — полный прогон тестов и линтера (426 passed, ruff clean)
- [ ] T027 Запустить quickstart.md валидацию — проверить 4 сценария из Telegram

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1-2**: Пропущены (нет setup/foundational задач)
- **US1 (Phase 3)**: Может начинаться сразу — topic_registry.py и llm_client.py
- **US2 (Phase 4)**: Может начинаться сразу — analyst.py
- **US3 (Phase 5)**: Может начинаться сразу — chart_renderer.py
- **US4 (Phase 6)**: Может начинаться сразу — sql_client.py
- **Polish (Phase 7)**: После завершения всех US

### User Story Dependencies

- **US1 (P1)**: Независима — topic_registry.py, llm_client.py
- **US2 (P1)**: Независима — analyst.py
- **US3 (P2)**: Независима — chart_renderer.py
- **US4 (P2)**: Независима — sql_client.py

**Все 4 user stories работают с разными файлами и могут реализовываться параллельно.**

### Within Each User Story

- Тесты → написать и убедиться что FAIL
- Implementation → реализовать
- Checkpoint → запустить тесты, убедиться что PASS

### Parallel Opportunities

Все 4 US полностью параллельны:
```
US1 (topic_registry.py, llm_client.py) ─┐
US2 (analyst.py)                         ├─► Phase 7 (integration tests, validation)
US3 (chart_renderer.py)                  │
US4 (sql_client.py)                     ─┘
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. US1: Улучшить keyword fallback → 80% вопросов маршрутизируются правильно
2. US2: Field labels → ответы читаемы
3. **STOP and VALIDATE**: Тест в Telegram
4. US3 + US4: Chart + period parsing → polish

### Incremental Delivery

1. US1 → Keyword fallback маршрутизирует правильно → Deploy
2. US2 → Ответы без raw fields → Deploy
3. US3 → Charts осмысленные → Deploy
4. US4 → Period parsing → Deploy

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable
- 4 US × разные файлы = полный параллелизм
- Commit after each task or logical group
