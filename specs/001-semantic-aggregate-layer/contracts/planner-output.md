# Contract: PlannerAgent Output

## Одношаговый Planning

**Input**: `UserQuestion.text` + `aggregate-catalog.yaml` (полный) + `semantic-catalog.yaml`
**Output**: JSON

```json
{
  "intent": "comparison",
  "needs_master_resolve": false,
  "period_hint": "last_month",
  "queries": [
    {
      "aggregate_id": "revenue_summary",
      "params": {
        "date_from": "2026-03-01",
        "date_to": "2026-03-31",
        "object_id": 506770,
        "group_by": "total"
      },
      "label": "Выручка за март"
    },
    {
      "aggregate_id": "revenue_summary",
      "params": {
        "date_from": "2026-04-01",
        "date_to": "2026-04-15",
        "object_id": 506770,
        "group_by": "total"
      },
      "label": "Выручка за апрель"
    }
  ]
}
```

**Fields**:
- `intent`: enum — `single` | `comparison` | `decomposition` | `trend` | `ranking`
- `needs_master_resolve`: bool — true если вопрос содержит имя мастера
- `period_hint`: str | null — подсказка для дат (last_week, last_month, this_month, ...)
- `queries`: list — до 10 запросов

**Validation**:
- `aggregate_id` — must be in aggregate-catalog.yaml whitelist
- `params` — validated by AggregateRegistry (типы + allowed_group_by per aggregate)
- `queries.length` — max 10
- `label` — non-empty string, used by AnalystAgent for context

**LLM constraints**:
- Temperature: 0.1
- Timeout: 5 сек
- Circuit breaker: 3 consecutive timeouts → TopicRegistry fallback на 60 сек

## Fallback (LLM unavailable / invalid plan)

**Trigger**: LLM timeout, error, or aggregate_id not in whitelist.
**Output**: MultiPlan with single AggregateQuery derived from TopicRegistry keyword matching. Intent = "single".
