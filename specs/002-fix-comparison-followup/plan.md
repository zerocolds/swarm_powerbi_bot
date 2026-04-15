# Implementation Plan: Fix comparison follow-up intent

**Spec**: specs/002-fix-comparison-followup/spec.md
**Issue**: #2
**Scope**: 3 файла, ~50 строк изменений

## Затронутые файлы

| Файл | Изменение |
|------|-----------|
| `src/swarm_powerbi_bot/services/llm_client.py` | `plan_aggregates()` принимает `last_topic`, добавляет в LLM prompt |
| `src/swarm_powerbi_bot/agents/planner.py` | `_llm_plan_multi()` передаёт `last_topic`; `_fallback_multi_plan()` определяет comparison intent + генерирует 2 запроса |
| `tests/test_planner_v2.py` | 3 новых теста: follow-up comparison LLM, follow-up comparison fallback, follow-up без last_topic |

## Изменения

### 1. `llm_client.py` — передача last_topic в LLM prompt

**Сигнатура**: добавить `last_topic: str = ""` в `plan_aggregates()`.

**Промпт**: после "ПРАВИЛА DECOMPOSITION" добавить блок:
```
КОНТЕКСТ FOLLOW-UP:
Если last_topic указан — пользователь продолжает предыдущий разговор.
Используй last_topic как основу для выбора агрегата.
Пример: last_topic="clients_outflow", вопрос="сравни по месяцам"
→ intent=comparison, aggregate_id=clients_outflow для обоих периодов.
```

**Message**: в user message добавить `\nКонтекст: last_topic={last_topic}` если `last_topic` не пустой.

### 2. `planner.py` — передача last_topic + fallback comparison

**`_llm_plan_multi()`**: передать `question.last_topic` в `plan_aggregates()`.

**`_fallback_multi_plan()`**:
- Определить intent по ключевым словам: если текст содержит "сравни"/"compare"/"сравнен" → intent=comparison
- При intent=comparison + topic из last_topic:
  - Генерировать 2 AggregateQuery: текущий месяц + прошлый месяц
  - Для клиентских агрегатов (`clients_*`): принудительно `group_by=status`
- При intent=comparison без last_topic: fallback на revenue_total

### 3. `tests/test_planner_v2.py` — 3 теста

- `test_followup_comparison_llm`: mock LLM возвращает comparison plan при last_topic
- `test_followup_comparison_fallback`: без LLM, "сравни" + last_topic → comparison + 2 queries
- `test_followup_comparison_no_context`: "сравни" без last_topic → fallback на revenue_total
