# Contract: SQLAgent Input/Output

## Input

`MultiPlan` from PlannerAgent containing `list[AggregateQuery]`.

Each `AggregateQuery`:
```
aggregate_id: str   — validated against whitelist
params: dict        — validated by ParameterValidator
label: str          — passthrough to result
```

## Processing

1. Validate `len(queries) <= 10`, truncate with diagnostic if exceeded
2. For each query: `AggregateRegistry.resolve(aggregate_id)` → SQL procedure/view name
3. `ParameterValidator.validate(params, aggregate_spec)` — reject on invalid
4. `asyncio.gather(*[execute(q) for q in queries])` — parallel, each with 10s timeout
5. Log each call via `QueryLogger`

## Output

`list[AggregateResult]`:
```
aggregate_id: str
label: str
rows: list[dict]     — column names as keys, values as str/int/float
row_count: int
duration_ms: int
status: str          — "ok" | "error" | "timeout"
error: str | None    — error message if status != "ok"
```

## Error handling

- Timeout → status="timeout", rows=[], error="Query exceeded 10s"
- SQL error → status="error", rows=[], error=sanitized message (no connection strings)
- Invalid aggregate_id → query skipped, logged as "unknown_aggregate"
- Partial success: other queries still executed and returned
