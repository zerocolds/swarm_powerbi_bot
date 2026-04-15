# Спецификация: Улучшение fallback statistics (#9)

**Ветка**: `feature/009-statistics-fallback-improvements` | **Дата**: 2026-04-15

## Проблема

Fallback-текст для topic `statistics` имеет три дефекта:

1. **Нет периода** — пользователь не видит за какой период данные (DateFrom–DateTo из SQL params)
2. **Не округлены денежные поля** — `TotalRevenue: 425916.72294397687`, `AvgCheck: 1935.985104290804` вместо `425,916.72` / `1,935.99`
3. **TotalRevenue не переведён** — показывается raw SQL field name вместо «Выручка (₽)»

## Scope

Файл: `src/swarm_powerbi_bot/agents/analyst.py`

### Что нужно сделать

1. `_fallback_summary()` — добавить строку «Период: YYYY-MM-DD — YYYY-MM-DD» из `sql_insight.params` (ключи `DateFrom`/`DateTo`)
2. `_format_statistics_summary()` — денежные поля (Revenue, TotalRevenue, AvgCheck, RevenuePerHour) округлять до 2 знаков: `{val:,.2f}`
3. `_METRIC_LABELS` и `_FIELD_LABELS` — добавить `"TotalRevenue": "Выручка (₽)"`
4. Default ветка `_fallback_summary()` — float значения форматировать через `{val:,.2f}`

### Out of scope

- Изменение графиков
- Comparison текст (покрыт #7)
- Orchestrator fallback (покрыт #4)

## Acceptance Criteria

- [ ] Текст statistics содержит строку «Период: ...» если DateFrom/DateTo есть в params
- [ ] TotalRevenue отображается как «Выручка (₽): 425,916.72»
- [ ] AvgCheck отображается как «Средний чек (₽): 1,935.99»
- [ ] Нет raw SQL field names в выводе
- [ ] Существующие тесты не ломаются
- [ ] Новые тесты покрывают округление и период
