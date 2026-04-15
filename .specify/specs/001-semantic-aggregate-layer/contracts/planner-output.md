# Contract: PlannerAgent Output

## Шаг 1 — Category Classification

**Input**: `UserQuestion.text` + `category-index.yaml` + `semantic-catalog.yaml`
**Output**: JSON

```json
{
  "categories": ["clients", "revenue"],
  "intent": "comparison",
  "needs_master_resolve": false,
  "period_hint": "last_month"
}
```

**Fields**:
- `categories`: list[str] — id из category-index.yaml, 1..3 категории
- `intent`: enum — `single` | `comparison` | `decomposition` | `trend` | `ranking`
- `needs_master_resolve`: bool — true если вопрос содержит имя мастера
- `period_hint`: str | null — подсказка для дат (last_week, last_month, this_month, ...)

**Validation**: categories must exist in category-index.yaml

## Шаг 2 — Aggregate Selection

**Input**: вопрос + intent + детальный каталог выбранных категорий
**Output**: JSON

```json
{
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

**Validation**:
- `aggregate_id` — must be in aggregate-catalog.yaml whitelist
- `params` — each validated by ParameterValidator
- `queries.length` — max 10
- `label` — non-empty string, used by AnalystAgent for context

## Fallback (LLM unavailable)

**Output**: MultiPlan with single AggregateQuery derived from TopicRegistry keyword matching. Intent = "single".
