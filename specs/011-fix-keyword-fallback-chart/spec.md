# Feature Specification: Исправление keyword fallback и chart rendering

**Feature Branch**: `feature/011-fix-keyword-fallback-chart`
**Created**: 2026-04-15
**Status**: Draft
**Input**: Системное исправление keyword fallback и chart rendering (#13, #14, #15, #16)

---

## Baseline: текущее поведение (As-Is)

### Проблема 1: topic_registry keyword scoring (#13, #16)

`topic_registry.py:109` — keyword `"выручк"` привязан **только** к `services`:
```
services → ["услуг", "выручк", "чек", "оборот", "продаж", "средний чек", "доход"]
statistics → ["статистик", "сводк", "итог", "показател", "общ", "kpi"]
```

Результат: «выручка за неделю», «почему упала выручка?», «кто больше принёс денег?» → `services` (популярные услуги) вместо `statistics` / `masters` / `decomposition`.

Scoring (line 152): `sum(1 for kw in entry.keywords if kw in text)` — простой подсчёт совпадений без весов. При одинаковом score побеждает первый в списке.

### Проблема 2: raw SQL field names в ответе (#13, #14)

`analyst.py:130-158` — `_FIELD_LABELS` покрывает не все поля. Отсутствуют:
- `ServiceCategory`, `IsPrimary`, `ServiceCount` (тема services)
- `MasterCategory`, `Rating` (тема masters)
- `UniqueClients`, `ActiveMasters`, `Visits` (тема statistics)

`_HIDDEN_FIELDS` (line 155-158) не включает `IsPrimary`, `ServiceCategory`, `MasterCategory`.

Fallback summary (line 298-314) показывает первые 5 полей первой строки — если поле не в `_FIELD_LABELS`, отображается сырое SQL-имя.

### Проблема 3: chart по неправильному полю (#13, #14)

`chart_renderer.py:107-116` — `_PREFERRED_VALUE` для `services` указывает `Revenue`, но stored procedure `spKDO_Services` возвращает другие колонки (`ServiceCount`, `IsPrimary`). Если preferred column не найдена, `_pick_label_value()` (line 119-152) берёт **первое числовое поле**, которым оказывается `IsPrimary` (boolean → 0/1).

### Проблема 4: «сравни март и апрель» → кнопки периода (#15)

`sql_client.py:44-49` — `_RE_MONTH` требует предлог **«за»**: `r"за\s+(январ..."`. Текст «сравни **март** и апрель» не содержит «за» → `has_period_hint()` возвращает `False` → telegram_bot.py показывает кнопки «За какой период?» вместо передачи в orchestrator.

---

## User Scenarios & Testing

### US-001 — Вопрос о выручке маршрутизируется на statistics (Priority: P1)

**Как** владелец салона,
**я хочу** задать вопрос «какая выручка за неделю?» и получить сводные KPI (выручка, визиты, средний чек),
**чтобы** видеть финансовую картину, а не список популярных услуг.

**Why P1**: Базовый сценарий — 4 из 4 issues (#13, #14, #15, #16) начинаются с неправильной маршрутизации «выручка».

**Independent Test**: Отправить «какая выручка за неделю?» → topic = `statistics`, ответ содержит TotalRevenue/Visits/AvgCheck.

**Acceptance Scenarios**:

1. **Given** вопрос «какая выручка за неделю?», **When** keyword scoring, **Then** topic = `statistics` (не `services`)
2. **Given** вопрос «кто больше принёс денег?», **When** keyword scoring, **Then** topic = `masters`
3. **Given** вопрос «выручка по мастерам», **When** keyword scoring и note `breakdown_by_master`, **Then** topic = `masters`
4. **Given** вопрос «популярные услуги за месяц», **When** keyword scoring, **Then** topic = `services`

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

- Вопрос содержит keywords из нескольких тем: «выручка по мастерам» → должен победить `masters` (note `breakdown_by_master`)
- Вопрос без keywords: «как дела?» → topic = `statistics` (default)
- Fallback summary с 0 строк → не показывать поля, только «Данные не найдены»
- Chart с 1 строкой → не рисовать chart (бессмысленный bar chart из 1 полоски)
- Месяц без года: «март» → текущий год (2026)
- Два месяца: «март и апрель» → оба распознаны как period hint

---

## Requirements

### Functional Requirements

- **FR-001**: Keyword `"выручк"` и `"доход"` MUST маршрутизировать на `statistics` по умолчанию (не `services`). Topic `services` MUST активироваться только при явных keywords: `"услуг"`, `"процедур"`, `"популярн"`.
- **FR-002**: Keyword `"денег"`, `"денежн"`, `"заработ"` MUST маршрутизировать на `statistics`.
- **FR-003**: Контекстный override: «выручка по мастерам» MUST → `masters`, «популярные услуги» MUST → `services`, «выручка за неделю» MUST → `statistics`.
- **FR-004**: `_FIELD_LABELS` MUST покрывать все поля, возвращаемые stored procedures для всех тем topic_registry.
- **FR-005**: Поля без маппинга в `_FIELD_LABELS` MUST быть скрыты в fallback summary (не отображаться), а не показываться raw.
- **FR-006**: `_HIDDEN_FIELDS` MUST включать `IsPrimary`, `ServiceCategory` (boolean/внутренние поля).
- **FR-007**: `_PREFERRED_VALUE` MUST соответствовать реальным колонкам stored procedures. Для `services` — `ServiceCount`, для `masters` — `TotalRevenue`.
- **FR-008**: Chart MUST исключать boolean-поля и ID-поля из выбора value axis.
- **FR-009**: `has_period_hint()` MUST распознавать русские названия месяцев без предлога «за»: «март», «апрель», «январь 2026».
- **FR-010**: `has_period_hint()` MUST распознавать конструкции «март и апрель», «с марта по апрель».
- **FR-011**: Fallback summary MUST показывать до 5 записей (не 1), отсортированных по основной метрике темы.

### Key Entities

- **TopicEntry**: topic_id, procedure, keywords — определяет маршрутизацию вопроса к stored procedure
- **_FIELD_LABELS**: dict SQL column name → русское отображаемое имя
- **_HIDDEN_FIELDS**: set полей, скрываемых из fallback summary
- **_PREFERRED_VALUE**: dict topic → preferred chart value column

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Все 10 вопросов из test-checklist.md маршрутизируются на правильный topic (100% accuracy)
- **SC-002**: Ни один ответ fallback summary не содержит PascalCase/camelCase SQL field names
- **SC-003**: Chart value axis для каждого topic соответствует осмысленной метрике (revenue, visits, count — не boolean/ID)
- **SC-004**: «Сравни март и апрель» не показывает кнопки периода и проходит в orchestrator
- **SC-005**: Существующие тесты (392 passed) не ломаются

---

## Assumptions

- Stored procedures не меняются — фикс затрагивает только Python-код (topic_registry, analyst, chart_renderer, sql_client)
- LLM planner path остаётся как fallback для сложных запросов; keyword scoring остаётся primary для производительности
- Все 17 тем из topic_registry сохраняются, меняются только keywords и их распределение
- Production code на ветке main — baseline; feature branch от main
