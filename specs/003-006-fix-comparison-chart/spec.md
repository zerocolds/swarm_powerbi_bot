# Feature Specification: Исправление comparison chart и текстового описания

**Feature Branch**: `feature/006-fix-comparison-chart`
**Created**: 2026-04-15
**Status**: Draft
**Issues**: #5, #6, #7
**Input**: Comparison chart для оттока показывает сумму ClientCount всех статусов (~5300) вместо breakdown по статусам. Текстовое описание — "10 записей" без контекста.

## User Scenarios & Testing

### User Story 1 — Comparison chart с осмысленными метриками (Priority: P1)

Пользователь спрашивает «отток клиентов», затем follow-up «сравни по месяцам за два месяца». Бот показывает grouped bar chart с breakdown по статусам клиентов (отток, уходящие, прогноз и т.д.) для двух периодов, а не суммарный ClientCount.

**Why this priority**: Без этого comparison chart бесполезен — показывает одну суммированную цифру вместо детализации.

**Independent Test**: Спросить «отток», затем «сравни по месяцам» → график должен содержать столбцы по статусам (не один столбец ClientCount).

**Acceptance Scenarios**:

1. **Given** `group_by=status` вернул 10 строк (по статусу) за каждый период, **When** `render_comparison` строит chart, **Then** на оси X — названия статусов (Отток, Уходящие, Прогноз...), на оси Y — ClientCount, два столбца per status (Март/Апрель).
2. **Given** `group_by=total` вернул 1 строку за каждый период, **When** `render_comparison` строит chart, **Then** показывает KPI-метрики (Visits, Revenue, AvgCheck) как grouped bars — текущее поведение сохранено.
3. **Given** один из периодов вернул 0 строк, **When** `render_comparison` строит chart, **Then** показывает данные одного периода + пометку "нет данных за второй период".

---

### User Story 2 — Текстовое описание comparison (Priority: P1)

При comparison ответ содержит осмысленное описание: что сравнивается, ключевые метрики с дельтами, а не просто "N записей".

**Why this priority**: Текст — единственная информация для пользователей без зрения или с маленьким экраном. "10 записей" — бесполезно.

**Independent Test**: Follow-up «сравни по месяцам» → текст содержит название метрики, значения за оба периода, дельту в %.

**Acceptance Scenarios**:

1. **Given** comparison двух периодов clients_outflow с `group_by=status`, **When** analyst формирует текст, **Then** текст содержит: "Сравнение оттока: Март 2026 vs Апрель 2026", количество клиентов в оттоке за каждый период, дельту в %.
2. **Given** comparison revenue_total, **When** analyst формирует текст, **Then** текст содержит: Visits, Revenue, AvgCheck с дельтами.
3. **Given** LLM недоступен (fallback), **When** `_fallback_multi()` формирует текст, **Then** текст всё равно содержит ключевые метрики и дельты (не "N записей").

---

### User Story 3 — Fallback-описание single-запросов (Priority: P2)

При ответе на single-запрос (отток, статистика) без LLM, fallback-описание использует человекочитаемые имена полей и показывает агрегированные статистики, а не сырые поля первой строки.

**Why this priority**: Улучшает UX при отключённом LLM, но менее критично чем comparison.

**Independent Test**: Спросить «покажи отток» при выключенном LLM → описание содержит "дней с последнего визита", не "DaysSinceLastVisit".

**Acceptance Scenarios**:

1. **Given** SQL вернул 20 строк оттока, **When** `_fallback_summary()` формирует текст, **Then** показывает: count, диапазон просрочки (от X до Y дней), топ по тратам — без Phone и raw timestamps.
2. **Given** SQL вернул строки statistics, **When** `_fallback_summary()` формирует текст, **Then** показывает: Визиты: N, Клиенты: N, Выручка: N₽, Средний чек: N₽.

---

### Edge Cases

- Что если `group_by=status` вернул строки без колонки `ClientStatus`? → Fallback на текущее агрегирующее поведение.
- Что если один период вернул 0 строк? → Показать данные одного периода + пометку.
- Что если все числовые значения = 0? → Показать "Нет данных для сравнения".
- Что если в comparison label_a = label_b (одинаковые периоды)? → Не крашиться, показать обе колонки.

## Requirements

### Functional Requirements

- **FR-001**: `render_comparison()` MUST определять наличие label-колонки (ClientStatus, Reason, MasterName) и строить per-row grouped bars вместо агрегации всех строк в одну сумму.
- **FR-002**: `render_comparison()` MUST сохранять текущее поведение (агрегация метрик) когда label-колонки нет (single-row результаты, total group_by).
- **FR-003**: `_fallback_multi()` в analyst MUST показывать ключевую метрику, значения за оба периода и дельту (%) вместо "N записей".
- **FR-004**: `_fallback_summary()` в analyst MUST использовать переведённые имена полей и скрывать Phone, raw ISO timestamps.
- **FR-005**: `_fallback_summary()` для outflow/leaving MUST показывать агрегированные статистики (count, диапазон просрочки, топ по тратам).

### Key Entities

- **render_comparison()**: `chart_renderer.py` — рендер comparison chart. Сейчас агрегирует все строки → одна сумма per metric. Нужно: per-row bars при наличии label-колонки.
- **_fallback_multi()**: `analyst.py:461` — текст для multi-query ответов. Сейчас "label: N записей". Нужно: метрика + дельта.
- **_fallback_summary()**: `analyst.py:211` — текст для single-query ответов. Сейчас raw field names. Нужно: перевод + агрегация.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Comparison chart для `group_by=status` показывает столбцы по статусам, не одну сумму ClientCount.
- **SC-002**: Текст comparison содержит название метрики + дельту в % для хотя бы одной метрики.
- **SC-003**: Fallback-описание single-запроса не содержит raw field names (ClientName, DaysSinceLastVisit и т.д.).
- **SC-004**: Все существующие тесты проходят без регрессий (354+ passed).

## Assumptions

- LLM (Ollama) часто недоступен → fallback-тексты должны быть самодостаточными.
- `group_by=status` возвращает колонку `ClientStatus` с текстовым названием статуса.
- `group_by=total` возвращает 1 строку с агрегированными метриками.
- Comparison chart используется только из orchestrator → multi_results path.
