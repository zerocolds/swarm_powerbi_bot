# Tasks: Semantic Aggregate Layer

**Input**: Design documents from `/specs/001-semantic-aggregate-layer/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Tests**: Включены — конституция требует Test-First (принцип III), порог покрытия 60%.

**Organization**: Задачи сгруппированы по user stories. Bootstrap-фазы (US-001..US-006) — dev-time утилиты, не runtime.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Может выполняться параллельно (разные файлы, нет зависимостей)
- **[Story]**: К какой user story относится задача

---

## Phase 1: Setup

**Purpose**: Создание структуры проекта и базовых зависимостей

- [ ] T001 Создать директории: `catalogs/`, `catalogs/bootstrap/`, `scripts/bootstrap/`, `sql/` в корне проекта
- [ ] T002 [P] Расширить `src/swarm_powerbi_bot/config.py`: добавить пути к каталогам (CATALOG_DIR, SEMANTIC_CATALOG_PATH, AGGREGATE_CATALOG_PATH)
- [ ] T003 [P] Расширить `src/swarm_powerbi_bot/models.py`: добавить dataclass-ы AggregateQuery, MultiPlan, AggregateResult, ComparisonResult по data-model.md
- [ ] T004 [P] Замерить baseline latency для 17 типовых вопросов текущей архитектуры (для верификации SC-007). Результат сохранить в `specs/001-semantic-aggregate-layer/baseline-latency.md`

**Checkpoint**: Структура проекта готова, модели определены

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core-модули, от которых зависят все user stories runtime-фаз

**⚠️ CRITICAL**: User stories фаз 5-9 не могут начаться до завершения этой фазы

- [ ] T005 Создать `src/swarm_powerbi_bot/services/aggregate_registry.py`: загрузка YAML-каталогов (PyYAML), whitelist-валидация aggregate_id, типизированная валидация параметров (date, enum, int range), per-aggregate allowed_group_by. Один модуль = catalog_loader + parameter_validator + registry
- [ ] T006 [P] Создать `src/swarm_powerbi_bot/services/master_resolver.py`: fuzzy-match по tbMasters (per-request SQL + difflib.SequenceMatcher, порог ≥0.6 короткие / ≥0.7 длинные)
- [ ] T007 [P] Создать `src/swarm_powerbi_bot/services/query_logger.py`: structured JSON logging агрегатных вызовов (timestamp, user_id, aggregate_id, params, duration_ms, row_count, status). Rotation 10MB×5. НЕ логировать данные ответа/токены
- [ ] T008 Написать тесты `tests/test_aggregate_registry.py`: загрузка каталогов, whitelist-валидация, типизация параметров (date format, enum membership, int range), per-aggregate allowed_group_by, невалидный aggregate_id → reject
- [ ] T009 [P] Написать тесты `tests/test_master_resolver.py`: fuzzy-match "Ана"→"Анна", 0 кандидатов, несколько кандидатов, mock SQL
- [ ] T010 [P] Написать тесты `tests/test_query_logger.py`: JSON формат, поля присутствуют, rotation, отсутствие чувствительных данных

**Checkpoint**: Foundation ready — можно начинать bootstrap и runtime user stories

---

## Phase 3: Bootstrap Discovery — US-001 + US-002 + US-003 + US-006 (Priority: P1) 🎯 MVP

**Goal**: Dev-time утилиты для извлечения семантики из PBIX и создания runtime-каталогов

**Independent Test**: `python scripts/bootstrap/extract_pbix.py powebi/КДО\ 3.2.1.pbix catalogs/bootstrap/semantic-model.yaml` → файл содержит все 8 таблиц, связи, DAX-меры

### Тесты

- [ ] T011 [P] [US1] Написать тесты `tests/test_extract_pbix.py`: извлечение таблиц/колонок, relationships, DAX-мер, иерархий из mock PBIX-структуры (zipfile с DataModelSchema JSON)

### Реализация

- [ ] T012 [US1] Создать `scripts/bootstrap/extract_pbix.py`: zipfile+json → `catalogs/bootstrap/semantic-model.yaml`. Поддержка UTF-16 LE с BOM. Извлечение tables[], relationships[], measures[]. По spec US-001
- [ ] T013 [US2] Создать `scripts/bootstrap/map_pbix_to_sql.py`: на основе semantic-model.yaml + `sql/create_kdo_procedures.sql` → `catalogs/bootstrap/pbix-to-sql-mapping.yaml`. Статусы: sql_covered / python_postprocess / not_covered. По spec US-002
- [ ] T014 [US3] Создать `scripts/bootstrap/generate_semantic_catalog.py`: на основе semantic-model.yaml → `catalogs/semantic-catalog.yaml` (runtime). Бизнес-сущности, правила, связи на русском. БЕЗ SQL-кода и имён таблиц. По spec US-003
- [ ] T015 [US6] Создать шаблон `catalogs/aggregate-catalog.yaml` с форматом из data-model.md: id, name, category, description, parameters (с allowed_group_by), returns, related_dax, examples. По spec US-006
- [ ] T016 [P] [US6] Создать `catalogs/category-index.yaml` с 8 категориями из data-model.md (clients, revenue, masters, services, communications, trends, referrals, overview). Примечание: используется только как справочник для разработчика, НЕ для runtime двухшагового planning в v1

**Checkpoint**: Bootstrap-утилиты готовы, runtime-каталоги созданы

---

## Phase 4: Gap Analysis & SQL Generation — US-004 + US-005 (Priority: P2)

**Goal**: Найти непокрытые метрики PBIX и создать SQL-агрегаты

**Independent Test**: `python scripts/bootstrap/gap_analysis.py` → gaps.md с приоритизированным списком

- [ ] T017 [US4] Создать `scripts/bootstrap/gap_analysis.py`: на основе pbix-to-sql-mapping.yaml → `catalogs/bootstrap/gaps.md`. Список not_covered DAX-мер + приоритеты P1/P2/P3. По spec US-004
- [ ] T018 [US5] Создать `scripts/bootstrap/validate_aggregates.py`: верификация SQL-агрегатов vs DAX-оригиналов, допуск ≤1%, тестовый ObjectId=506770. По spec US-005

**Checkpoint**: Gap-анализ завершён, план SQL-агрегатов определён

---

## Phase 5: SQL Layer — US-007 (Priority: P1)

**Goal**: SQL indexed views и TVF для базовых агрегатов, единый интерфейс вызова

**Independent Test**: `SELECT * FROM vwKDO_RevenueSummary WHERE ObjectId=506770 AND EndOfMonth='2026-03-31'` → корректные данные

- [ ] T019 [US7] Создать `sql/create_materialized_aggregates.sql`: indexed views (vwKDO_RevenueSummary, vwKDO_MasterSummary, vwKDO_ServiceSummary, vwKDO_ChannelSummary) с SCHEMABINDING. По research R-002
- [ ] T020 [US7] Создать `sql/create_gap_aggregates.sql`: TVF для агрегатов с динамическими параметрами (фильтры по статусу клиента через fnKDO_ClientStatus). По research R-002
- [ ] T021 [US7] Наполнить `catalogs/aggregate-catalog.yaml` реальными агрегатами: все 17 существующих тем topic_registry + gap-агрегаты. Каждый с allowed_group_by, parameters, returns, examples

**Checkpoint**: SQL-слой готов, каталог наполнен

---

## Phase 6: PlannerAgent + DB Protection — US-008 + US-012 (Priority: P1)

**Goal**: LLM выбирает агрегаты из каталога в один шаг. Whitelist-защита БД.

**Independent Test**: Вопрос "покажи средний чек по мастерам за март" → PlannerAgent возвращает MultiPlan с aggregate_id=revenue_by_master, params={group_by: master, date_from, date_to}

### Тесты

- [ ] T022 [P] [US8] Написать тесты `tests/test_planner_v2.py`: mock LLMClient возвращает фиксированный JSON → парсинг в MultiPlan; невалидный JSON → graceful fallback; aggregate_id не из каталога → TopicRegistry fallback; кросс-доменный запрос → несколько агрегатов
- [ ] T023 [P] [US12] Написать тесты `tests/test_security.py`: SQL injection в вопросе → "не могу ответить"; aggregate_id не из whitelist → reject; невалидные параметры (date format, group_by не из allowed) → reject; read-only user проверка

### Реализация

- [ ] T024 [US8] Переработать `src/swarm_powerbi_bot/agents/planner.py`: одношаговый planning — system prompt содержит полный aggregate-catalog.yaml + semantic-catalog.yaml, user prompt = вопрос. Output: JSON → MultiPlan. Temperature 0.1. По contracts/planner-output.md
- [ ] T025 [US8] Расширить `src/swarm_powerbi_bot/services/llm_client.py`: новый метод plan_aggregates(question, catalog) → JSON. Timeout 5 сек. Circuit breaker: 3 consecutive timeouts → fallback на TopicRegistry на 60 сек. По research R-003
- [ ] T026 [US8] Расширить `src/swarm_powerbi_bot/orchestrator.py`: при доступном LLM — PlannerAgent v2 → MultiPlan; при fallback — TopicRegistry → single AggregateQuery. Невалидный план (aggregate_id не из каталога) → TopicRegistry fallback
- [ ] T027 [US12] Расширить `src/swarm_powerbi_bot/services/sql_client.py`: метод execute_aggregate(aggregate_id, params) — вызов через AggregateRegistry.validate() перед выполнением. Read-only подключение. По spec US-012

**Checkpoint**: PlannerAgent v2 работает, DB защищена whitelist-ом

---

## Phase 7: Multi-query SQLAgent — US-009 (Priority: P1)

**Goal**: До 10 параллельных агрегатных запросов за один вопрос

**Independent Test**: MultiPlan с 2 запросами → SQLAgent выполняет оба параллельно → list[AggregateResult]

### Тесты

- [ ] T028 [US9] Написать тесты `tests/test_multi_query.py`: 2 запроса → оба выполняются; 12 запросов → лимит 10; partial failure (таймаут одного) → остальные возвращаются; Semaphore(5) ограничивает concurrency. По contracts/sql-agent-input.md

### Реализация

- [ ] T029 [US9] Расширить `src/swarm_powerbi_bot/agents/sql.py`: метод run_multi(plan: MultiPlan) — asyncio.gather + Semaphore(5), timeout 10 сек per query, partial failure handling. Лимит 10 запросов
- [ ] T030 [US9] Адаптировать `src/swarm_powerbi_bot/agents/analyst.py`: принимает list[AggregateResult], формирует единый ответ с синтезом нескольких результатов. По contracts/analyst-input.md
- [ ] T031 [US9] Расширить `src/swarm_powerbi_bot/orchestrator.py`: полный multi-query flow — PlannerAgent → MasterResolver (если нужен) → SQLAgent.run_multi() → ChartRenderer → AnalystAgent
- [ ] T032 [US9] Интеграция query_logger.py в SQLAgent: логирование каждого агрегатного вызова

**Checkpoint**: Multi-query работает, все P1 user stories завершены

---

## Phase 8: Сравнения — US-010 (Priority: P2)

**Goal**: "Сравни выручку за март и апрель" → grouped bar chart + delta текст

**Independent Test**: Вопрос "сравни март и апрель" → 2 запроса с разными периодами → grouped bar chart + текст с % изменения

### Тесты

- [ ] T033 [US10] Написать тесты `tests/test_comparison.py`: сравнение двух периодов → два запроса одного агрегата; "этот vs прошлый месяц" → корректные даты; сравнение мастеров → fuzzy-match + два запроса; grouped bar chart render; неполный текущий месяц → отметка в ответе

### Реализация

- [ ] T034 [US10] Расширить `src/swarm_powerbi_bot/agents/planner.py`: intent=comparison → два вызова одного агрегата с разными date_from/date_to. Автоопределение "этот месяц", "прошлый квартал"
- [ ] T035 [US10] Расширить `src/swarm_powerbi_bot/services/chart_renderer.py`: grouped bar chart (ax.bar с offset), multi-line comparison, delta-аннотации (+12.5% зелёным, −3.2% красным). По research R-006
- [ ] T036 [US10] Расширить `src/swarm_powerbi_bot/agents/analyst.py`: comparison text template — "Метрика за период 1: X. За период 2: Y. Изменение: +/-Z%". Пометка неполного периода. По contracts/analyst-input.md

**Checkpoint**: Сравнения работают

---

## Phase 9: Композиция — US-011 (Priority: P3)

**Goal**: "Почему упала выручка?" → декомпозиция на 4-5 запросов, анализ факторов

**Independent Test**: Вопрос "почему упала выручка?" → 4 агрегата (выручка/клиенты/чек/загрузка × 2 периода) → ответ с основным фактором

### Тесты

- [ ] T037 [US11] Написать тесты `tests/test_composition.py`: decomposition intent → до 5 агрегатов; factor analysis → определение основного фактора; лимит 10 запросов при decomposition

### Реализация

- [ ] T038 [US11] Расширить `src/swarm_powerbi_bot/agents/planner.py`: intent=decomposition → набор агрегатов для факторного анализа (revenue + clients + avg_check × 2 периода)
- [ ] T039 [US11] Расширить `src/swarm_powerbi_bot/agents/analyst.py`: decomposition text — "Выручка упала на X%. Основная причина: <фактор> (снижение на Y%)". Не более 3 факторов

**Checkpoint**: Композиция работает, все runtime-фичи завершены

---

## Phase 10: CI Pipeline + Polish — US-013 + Cross-Cutting

**Purpose**: Автоматизация и cross-cutting concerns

- [ ] T040 [P] [US13] Создать CI-задачу (GitHub Actions) для пересборки semantic-model.yaml при изменении PBIX. Проверка совместимости агрегатов. Issue при новых gaps. По spec US-013
- [ ] T041 [P] Обновить `docs/` — документация каталогов, нового flow PlannerAgent, агрегатов. Обновить CLAUDE.md при изменении структуры
- [ ] T042 [P] Обновить `Dockerfile`: включить `catalogs/*.yaml` в образ, исключить `catalogs/bootstrap/`, `scripts/bootstrap/`, `sql/`, `powebi/`
- [ ] T043 Прогон всех 77 существующих тестов — backward compatibility (SC-001). Проверка ruff check + ruff format
- [ ] T044 Прогон quickstart.md: полный цикл pytest -q, docker build

**Checkpoint**: Все задачи завершены, проект готов к review

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → блокирует всё остальное
                                          ↓
                   ┌──────────────────────┼──────────────────┐
                   ↓                      ↓                  ↓
          Phase 3 (Bootstrap)    Phase 6 (Planner+Security)  |
                   ↓                      ↓                  |
          Phase 4 (Gap Analysis) Phase 7 (Multi-query)       |
                   ↓                      ↓                  |
          Phase 5 (SQL Layer) ──→ Phase 8 (Comparisons)      |
                                          ↓                  |
                                 Phase 9 (Composition)       |
                                          ↓                  ↓
                                 Phase 10 (CI + Polish)
```

### User Story Dependencies

- **US-001 → US-002 → US-003 + US-006**: Последовательная цепочка bootstrap (Phase 3)
- **US-004 → US-005**: Gap analysis → SQL generation (Phase 4), зависит от Phase 3
- **US-007**: SQL layer (Phase 5), зависит от US-006 (каталог)
- **US-008 + US-012**: PlannerAgent + DB Protection (Phase 6), зависит от Phase 2 (aggregate_registry)
- **US-009**: Multi-query (Phase 7), зависит от US-008
- **US-010**: Comparisons (Phase 8), зависит от US-009
- **US-011**: Composition (Phase 9), зависит от US-010
- **US-013**: CI pipeline (Phase 10), зависит от US-001..US-006

### Параллельные потоки

**Bootstrap (Phase 3-5)** и **Runtime (Phase 6-9)** могут выполняться ПАРАЛЛЕЛЬНО:
- Поток A: Phase 3 → Phase 4 → Phase 5 (dev-time bootstrap)
- Поток B: Phase 6 → Phase 7 → Phase 8 → Phase 9 (runtime код)

Phase 5 (SQL Layer) должен завершиться до финального тестирования Phase 7+.

### Within Each User Story

- Тесты FIRST (должны FAIL до реализации)
- Models → Services → Agents → Integration
- Коммит после каждой задачи или логической группы

### Parallel Opportunities

- T002 + T003 + T004 (Setup: config, models, baseline — разные файлы)
- T005 + T006 + T007 (Foundational: registry, resolver, logger — разные файлы)
- T008 + T009 + T010 (Foundational тесты — разные файлы)
- T022 + T023 (Phase 6 тесты — разные файлы)
- T040 + T041 + T042 (Polish — разные файлы)
- Поток A (bootstrap) ∥ Поток B (runtime)

---

## Parallel Example: Phase 6 (PlannerAgent + Security)

```bash
# Тесты параллельно:
Task: T022 — test_planner_v2.py
Task: T023 — test_security.py

# Реализация после тестов:
Task: T024 — planner.py (зависит от T022)
Task: T025 — llm_client.py (параллельно с T024)
Task: T026 — orchestrator.py (зависит от T024, T025)
Task: T027 — sql_client.py (параллельно с T024)
```

---

## Implementation Strategy

### MVP First (P1 stories only)

1. Phase 1: Setup → Phase 2: Foundational
2. Phase 3: Bootstrap (US-001..US-006) — создание каталогов
3. Phase 5: SQL Layer (US-007) — SQL-агрегаты
4. Phase 6: PlannerAgent + Security (US-008 + US-012)
5. Phase 7: Multi-query (US-009)
6. **STOP AND VALIDATE**: 77 тестов + новые тесты проходят, PlannerAgent отвечает на 17 типовых вопросов

### Incremental Delivery

1. MVP (P1) → тест → деплой
2. + Comparisons (US-010, P2) → тест → деплой
3. + Composition (US-011, P3) → тест → деплой
4. + CI Pipeline (US-013, P3) → тест → деплой

### MAQA Strategy

Фича имеет ≥3 независимых задач → MAQA coordinator:
- **Поток A (Sonnet)**: Bootstrap tools (Phase 3-5)
- **Поток B (Sonnet)**: Runtime modules (Phase 6-7)
- **Поток C (Sonnet)**: Тесты (T008-T010, T022-T023, T028, T033)
- **QA (Opus)**: Ревью каждого потока

---

## Notes

- [P] = разные файлы, нет зависимостей
- [Story] связывает задачу с user story из spec.md
- Каждая user story тестируема независимо
- 77 существующих тестов НЕ ломаются (backward compatibility)
- TopicRegistry сохраняется как fallback — не удалять
- PBIX нужен только для bootstrap (Phase 3-4), НЕ runtime
- В Docker: только `src/` + `catalogs/*.yaml`
