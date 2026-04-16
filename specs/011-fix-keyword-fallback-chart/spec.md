# Feature Specification: Исправление маршрутизации и chart rendering

**Feature Branch**: `feature/011-fix-keyword-fallback-chart`
**Created**: 2026-04-15
**Status**: Draft
**Input**: Системное исправление маршрутизации запросов и chart rendering (#13, #14, #15, #16)

---

## Clarifications

### Session 2026-04-15

- Q: Как решать проблему keyword scoring — чинить веса или менять подход? → A: Убрать хардкод keywords, маршрутизировать через LLM. LLM получает список методов с описаниями возвращаемых данных и решает какой вызвать.
- Q: Откуда брать описание колонок SP для каталога LLM? → A: Собирать автоматически из aggregate_catalog.yaml + TopicEntry.description + _FIELD_LABELS ключи.

### Session 2026-04-16 (critique findings)

- Q: run() уже имеет LLM-first routing — в чём реальная проблема маршрутизации? → A: `PlannerAgent.run()` уже вызывает `_llm_plan()` → `LLMClient.plan_query()` первым (planner.py:458). Keyword scoring — fallback. Проблема: (1) если `OLLAMA_API_KEY` не задан → LLM всегда возвращает None → keyword fallback, (2) keyword fallback привязывает «выручк» только к services. Фикс: улучшить keyword fallback scoring + обеспечить диагностику какой путь используется.
- Q: FR-011 меняет семантику с "5 полей 1-й строки" на "5 записей" — это scope creep? → A: Да, FR-011 убран — текущее поведение (5 полей первой строки) достаточно при условии что поля переведены.

---

## Baseline: текущее поведение (As-Is)

### Проблема 1: keyword fallback неправильно маршрутизирует запросы (#13, #16)

`PlannerAgent.run()` **уже** использует LLM-first routing: `_llm_plan()` → `LLMClient.plan_query()` (planner.py:458). При недоступности LLM (нет `OLLAMA_API_KEY`, timeout, ошибка) используется keyword fallback из `topic_registry.py`.

Keyword fallback: `"выручк"` привязан **только** к `services` (topic_registry.py:109). Scoring — простой `sum()` без весов и контекста. Результат: «выручка за неделю» → `services` вместо `statistics`.

**Корневая причина**: Если `OLLAMA_API_KEY` не задан → `plan_query()` возвращает `None` (llm_client.py:131) → keyword fallback **всегда**. Даже если LLM доступен — keyword fallback должен быть точнее для graceful degradation.

**Решение**:
1. Улучшить keyword fallback: добавить весовые коэффициенты, контекстные правила (если вопрос про период → statistics, а не services)
2. Добавить logging/диагностику: при каждом routing логировать `planner:llm` vs `planner:keyword` для мониторинга
3. Обеспечить документирование настройки `OLLAMA_API_KEY` для production

### Проблема 2: raw SQL field names в ответе (#13, #14)

`analyst.py:130-158` — `_FIELD_LABELS` покрывает не все поля. Отсутствуют:
- `ServiceCategory`, `IsPrimary`, `ServiceCount` (тема services)
- `MasterCategory`, `Rating` (тема masters)
- `UniqueClients`, `ActiveMasters`, `Visits` (тема statistics)

Fallback summary показывает первые 5 полей первой строки — если поле не в `_FIELD_LABELS`, отображается сырое SQL-имя.

### Проблема 3: chart по неправильному полю (#13, #14)

`chart_renderer.py` — `_PREFERRED_VALUE` для `services` указывает `Revenue`, но SP возвращает другие колонки. Если preferred column не найдена, берёт **первое числовое поле** (`IsPrimary` boolean → 0/1).

### Проблема 4: «сравни март и апрель» → кнопки периода (#15)

`sql_client.py` — `_RE_MONTH` требует предлог **«за»** перед месяцем. «Сравни **март** и апрель» не матчит → `has_period_hint()` = `False` → кнопки периода вместо orchestrator.

---

## User Scenarios & Testing

### US-001 — LLM выбирает правильный метод для вопроса (Priority: P1)

**Как** владелец салона,
**я хочу** задать вопрос на естественном языке и получить релевантные данные,
**чтобы** бот понимал контекст, а не просто искал ключевые слова.

**Why P1**: Корневая причина всех 4 issues — keyword scoring не понимает контекст. LLM-маршрутизация решает проблему системно.

**Independent Test**: Отправить 10 вопросов из checklist → каждый маршрутизируется на правильный topic/procedure.

**Acceptance Scenarios**:

1. **Given** вопрос «какая выручка за неделю?», **When** LLM маршрутизация, **Then** выбирает `spKDO_Statistics` (сводные KPI)
2. **Given** вопрос «кто больше принёс денег?», **When** LLM маршрутизация, **Then** выбирает `spKDO_Masters` (топ мастеров)
3. **Given** вопрос «популярные услуги за месяц», **When** LLM маршрутизация, **Then** выбирает `spKDO_Services`
4. **Given** вопрос «почему упала выручка?», **When** LLM маршрутизация, **Then** выбирает несколько методов (decomposition) или `spKDO_Statistics` + `spKDO_Trend`
5. **Given** LLM недоступен (timeout/error), **When** fallback, **Then** используется keyword scoring из topic_registry (текущее поведение)

---

### US-002 — Ответ без сырых SQL field names (Priority: P1)

**Как** пользователь,
**я хочу** видеть русские названия полей в ответе бота,
**чтобы** понимать данные без знания SQL.

**Why P1**: Raw field names делают ответ бесполезным для нетехнического пользователя.

**Independent Test**: Задать вопрос по любой теме → ответ не содержит ни одного camelCase/PascalCase идентификатора.

**Acceptance Scenarios**:

1. **Given** тема `services`, **When** fallback summary, **Then** `ServiceCategory` → «Категория», `IsPrimary` → скрыто, `ServiceCount` → «Кол-во услуг»
2. **Given** тема `masters`, **When** fallback summary, **Then** `MasterCategory` → «Специализация», `Rating` → «Рейтинг»
3. **Given** тема `statistics`, **When** fallback summary, **Then** `UniqueClients` → «Уникальных клиентов», `ActiveMasters` → «Активных мастеров»
4. **Given** любая тема, **When** fallback summary и поле не в `_FIELD_LABELS`, **Then** поле скрыто (не показывается), а не отображается как raw name

---

### US-003 — Chart по релевантной метрике (Priority: P2)

**Как** пользователь,
**я хочу** видеть график по осмысленной метрике (выручка, визиты),
**чтобы** chart был полезным, а не показывал boolean поле.

**Why P2**: Chart дополняет ответ, но текст важнее.

**Independent Test**: Запросить тему → chart ось Y = revenue/visits/count (не boolean/ID).

**Acceptance Scenarios**:

1. **Given** тема `services`, **When** chart rendering, **Then** value axis = `ServiceCount` или `Revenue` (не `IsPrimary`)
2. **Given** тема `masters`, **When** chart rendering, **Then** value axis = `TotalRevenue` или `TotalVisits` (не `Rating`)
3. **Given** preferred column не найдена в данных, **When** chart rendering, **Then** выбирается следующая по приоритету числовая метрика, исключая boolean/ID поля

---

### US-004 — «Сравни март и апрель» без кнопок периода (Priority: P2)

**Как** пользователь,
**я хочу** написать «сравни март и апрель» и получить comparison ответ,
**чтобы** не нажимать лишние кнопки.

**Why P2**: Comparison — продвинутый сценарий, но блокирует use case целиком.

**Independent Test**: Отправить «сравни март и апрель» → бот не показывает кнопки, а возвращает сравнение.

**Acceptance Scenarios**:

1. **Given** вопрос «сравни март и апрель», **When** `has_period_hint()`, **Then** возвращает `True` (месяцы распознаны без предлога «за»)
2. **Given** вопрос «выручка март», **When** `has_period_hint()`, **Then** возвращает `True`
3. **Given** вопрос «отток за прошлый месяц», **When** `has_period_hint()`, **Then** возвращает `True` (текущее поведение сохраняется)

---

### Edge Cases

- LLM timeout → graceful degradation на keyword fallback (не ошибка, а fallback)
- LLM возвращает несуществующий topic_id → использовать keyword fallback
- Вопрос без контекста: «как дела?» → LLM должен выбрать `statistics` (default/overview) или вежливо отказать
- Fallback summary с 0 строк → не показывать поля, только «Данные не найдены»
- Chart с 1 строкой → не рисовать chart (бессмысленный bar chart из 1 полоски)
- Месяц без года: «март» → текущий год (2026)
- Два месяца: «март и апрель» → оба распознаны как period hint
- Имена «Марта», «Майя» → `has_period_hint()` НЕ должен давать false positive (word boundaries в regex)
- LLM выбирает decomposition (несколько методов) → orchestrator должен обработать multi-query

---

## Requirements

### Functional Requirements

- **FR-001**: Keyword fallback в `detect_topic()` MUST улучшить маршрутизацию: вопросы с контекстом периода («выручка за неделю», «статистика за месяц») MUST маршрутизироваться на `statistics`, а не `services`. Keyword `"выручк"` MUST иметь маппинг на несколько тем с весами, а не только на `services`.
- **FR-002**: `PlannerAgent.run()` MUST логировать какой путь использован: `planner:llm` или `planner:keyword` (уже реализовано через notes — убедиться что logging достаточен для production-диагностики).
- **FR-003**: LLM-путь в `run()` (через `_llm_plan()` → `plan_query()`) MUST сохранять текущее поведение. `_PLANNER_SYSTEM_PROMPT` уже корректно различает statistics/services/masters — не модифицировать без необходимости.
- **FR-004**: `_FIELD_LABELS` MUST покрывать все поля, возвращаемые stored procedures для всех тем topic_registry.
- **FR-005**: Поля без маппинга в `_FIELD_LABELS` MUST быть скрыты в fallback summary (не отображаться), а не показываться raw.
- **FR-006**: `_HIDDEN_FIELDS` MUST включать `IsPrimary`, `ServiceCategory` (boolean/внутренние поля).
- **FR-007**: `_PREFERRED_VALUE` MUST соответствовать реальным колонкам stored procedures. Для `services` — `ServiceCount`, для `masters` — `TotalRevenue`.
- **FR-008**: Chart MUST исключать boolean-поля и ID-поля из выбора value axis.
- **FR-009**: `has_period_hint()` MUST распознавать русские названия месяцев без предлога «за»: «март», «апрель», «январь 2026».
- **FR-010**: `has_period_hint()` MUST распознавать конструкции «март и апрель», «с марта по апрель».
- **FR-011**: `has_period_hint()` MUST НЕ давать false positive на имена собственные (Марта, Майя). Regex MUST использовать word boundaries `\b` для минимизации false positives.
- **FR-012**: `plan_query()` SHOULD иметь circuit breaker аналогично `plan_aggregates()` для защиты от каскадных timeout при недоступности Ollama.

### Key Entities

- **TopicEntry**: topic_id, procedure, keywords, description — реестр доступных методов. Keywords используются для fallback scoring.
- **_FIELD_LABELS**: dict SQL column name → русское отображаемое имя
- **_HIDDEN_FIELDS**: set полей, скрываемых из fallback summary
- **_PREFERRED_VALUE**: dict topic → preferred chart value column

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Все 10 вопросов из test-checklist.md маршрутизируются на правильный topic (100% accuracy) — как через LLM путь, так и через keyword fallback
- **SC-002**: Ни один ответ fallback summary не содержит PascalCase/camelCase SQL field names
- **SC-003**: Chart value axis для каждого topic соответствует осмысленной метрике (revenue, visits, count — не boolean/ID)
- **SC-004**: «Сравни март и апрель» не показывает кнопки периода и проходит в orchestrator
- **SC-005**: Существующие тесты (392 passed) не ломаются
- **SC-006**: При недоступности LLM бот деградирует на keyword fallback без ошибок для пользователя

---

## Assumptions

- Stored procedures не меняются — фикс затрагивает Python-код
- LLM (Ollama) доступен локально; PlannerAgent уже имеет LLMClient — используем существующую инфраструктуру
- topic_registry.py сохраняется как fallback и как источник каталога методов для LLM
- aggregate_catalog.yaml (из feature/001) может дополнять каталог, но не является обязательной зависимостью
- Production code на ветке main — baseline; feature branch от main
- Latency LLM routing: допустимо до 3 секунд на маршрутизацию (пользователь видит «typing...» в Telegram)
