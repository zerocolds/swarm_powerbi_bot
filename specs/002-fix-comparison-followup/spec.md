# Feature Specification: Fix comparison follow-up intent

**Feature Branch**: `feature/002-fix-comparison-followup`
**Created**: 2026-04-15
**Status**: Draft
**Input**: Bugfix для GitHub issue #2
**Links**: https://github.com/k-p-i-bi/tg_bot/issues/2

## Описание проблемы

При follow-up вопросе «сравни по месяцам за два месяца» после вопроса об оттоке клиентов бот возвращает **сырой список клиентов** (ClientName, Phone, DaysSinceLastVisit) вместо **помесячного сравнения** агрегированных цифр оттока.

### Root cause анализ

Три точки отказа:

1. **`LLMClient.plan_aggregates()`** (`llm_client.py:140`) получает только `question.text` ("сравни по месяцам за два месяца") без `last_topic`. LLM не знает что предыдущий вопрос был об оттоке и не может выбрать правильный агрегат.

2. **`PlannerAgent._llm_plan_multi()`** (`planner.py:229`) вызывает `plan_aggregates(question=question.text, ...)` — передаёт только текст, игнорирует `question.last_topic`.

3. **`PlannerAgent._fallback_multi_plan()`** (`planner.py:346`) хардкодит `intent="single"` — даже keyword fallback не может вернуть comparison, даже если текст содержит «сравни».

## User Scenarios & Testing

### User Story 1 — Follow-up comparison по клиентским агрегатам (Priority: P1)

Пользователь спрашивает про отток, получает ответ, затем просит сравнить по месяцам. Бот должен понять контекст и вернуть помесячное сравнение оттока.

**Why this priority**: Это основной баг из issue #2 — comparison follow-up полностью сломан для клиентских тем.

**Independent Test**: Отправить два вопроса: "покажи отток" → "сравни по месяцам за два месяца". Второй ответ должен содержать агрегированные цифры за два периода.

**Acceptance Scenarios**:

1. **Given** пользователь спросил "покажи отток" и получил ответ с `topic=clients_outflow`, **When** отправляет follow-up "сравни по месяцам за два месяца" с `last_topic=clients_outflow`, **Then** бот возвращает `intent=comparison`, 2 запроса к `clients_outflow` с разными периодами (месяц 1 и месяц 2), агрегированный текст с процентом изменения.

2. **Given** пользователь спросил "покажи отток", **When** отправляет "сравни по месяцам", **Then** ответ НЕ содержит сырых данных клиентов (имена, телефоны), а содержит агрегированные числа (количество клиентов в оттоке за период A vs период B).

---

### User Story 2 — Follow-up comparison по выручке (Priority: P1)

Пользователь спрашивает про выручку, затем просит сравнить. Должен работать так же.

**Why this priority**: Выручка — самый частый запрос, comparison для неё уже частично работает, но передача last_topic улучшит точность.

**Independent Test**: "покажи выручку за март" → "а за февраль? сравни". Второй ответ — comparison chart.

**Acceptance Scenarios**:

1. **Given** `last_topic=revenue_total`, **When** "сравни с прошлым месяцем", **Then** `intent=comparison`, 2 запроса к `revenue_total`, comparison chart (image != None).

---

### User Story 3 — Keyword fallback с comparison intent (Priority: P2)

Если LLM недоступен (circuit breaker, timeout), keyword fallback должен распознавать intent=comparison по ключевым словам «сравни», «сравнение», «compare».

**Why this priority**: Без этого при LLM-отказе comparison полностью теряется.

**Independent Test**: Выключить Ollama, отправить "сравни выручку за март и февраль". Fallback должен вернуть intent=comparison.

**Acceptance Scenarios**:

1. **Given** LLM недоступен, **When** вопрос содержит "сравни" + last_topic, **Then** `_fallback_multi_plan` возвращает `intent=comparison`, 2 AggregateQuery с разными периодами.

2. **Given** LLM недоступен, **When** вопрос "сравни" без last_topic и без конкретной темы, **Then** fallback возвращает `intent=single` с `revenue_total` (безопасный default).

---

### Edge Cases

- Follow-up "сравни" без предыдущего контекста (last_topic пустой) → LLM должен попытаться определить тему из текста, fallback → revenue_total
- "Сравни по салонам" (не по времени, а по объектам) → intent=comparison с group_by=salon, НЕ два периода
- "Сравни за три месяца" → допустимо вернуть trend (intent=trend) вместо comparison
- Клиентские агрегаты с group_by=list vs group_by=status: comparison должен использовать group_by=status для агрегированных цифр, не list

## Requirements

### Functional Requirements

- **FR-001**: `LLMClient.plan_aggregates()` MUST принимать и передавать `last_topic` в LLM prompt, чтобы LLM знал контекст предыдущего вопроса
- **FR-002**: `PlannerAgent._llm_plan_multi()` MUST передавать `question.last_topic` в вызов `plan_aggregates()`
- **FR-003**: `PlannerAgent._fallback_multi_plan()` MUST определять `intent=comparison` по ключевым словам (сравни, сравнение, compare) и генерировать 2 AggregateQuery с разными периодами
- **FR-004**: При comparison для клиентских агрегатов (clients_outflow, clients_leaving и т.д.) system MUST использовать `group_by=status` (агрегированные цифры), а не `group_by=list` (сырой список)
- **FR-005**: LLM system prompt MUST содержать инструкцию: "Если last_topic указан, используй его как контекст для follow-up вопроса"

### Key Entities

- **UserQuestion**: уже содержит `last_topic: str` — используется в `_fallback_multi_plan`, но НЕ передаётся в LLM prompt
- **MultiPlan**: intent field уже поддерживает "comparison" — нет изменений в модели

## Success Criteria

### Measurable Outcomes

- **SC-001**: Follow-up "сравни по месяцам" после вопроса об оттоке возвращает intent=comparison и 2 запроса с разными периодами (тест-кейс из issue #2)
- **SC-002**: Ответ на comparison follow-up НЕ содержит сырых данных клиентов (телефонов, имён) — только агрегированные цифры
- **SC-003**: Все существующие 351 тестов проходят без регрессий
- **SC-004**: Keyword fallback при "сравни" + last_topic возвращает intent=comparison

## Assumptions

- Модель данных (UserQuestion, MultiPlan, AggregateQuery) не меняется
- LLM prompt расширяется одной строкой с last_topic — нет риска превышения контекста
- `group_by=status` поддерживается для всех `clients_*` агрегатов (проверено в каталоге: `allowed_group_by: [list, status, master]`)
- Comparison chart (matplotlib) уже поддерживает 2 набора данных — изменения только в planning слое
