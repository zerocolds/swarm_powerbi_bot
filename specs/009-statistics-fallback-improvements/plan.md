# План реализации: Улучшение fallback statistics (#9)

**Ветка**: `feature/009-statistics-fallback-improvements` | **Дата**: 2026-04-15 | **Spec**: [spec.md](spec.md)

## Summary

Минимальные правки в одном файле (`analyst.py`) + тесты. Без архитектурных изменений.

## Изменения

### 1. `_METRIC_LABELS` / `_FIELD_LABELS` — добавить TotalRevenue

Добавить `"TotalRevenue": "Выручка (₽)"` в оба словаря.

**Файл**: `src/swarm_powerbi_bot/agents/analyst.py` (строки ~110, ~130)

### 2. `_format_statistics_summary()` — округление денежных полей

Выделить set `_MONEY_FIELDS = {"Revenue", "TotalRevenue", "AvgCheck", "RevenuePerHour"}`.
Для денежных полей — `{val:,.2f}`, остальные float — `{val:,.0f}`, int — как есть.

Добавить `"TotalRevenue"` в список итерации (между UniqueClients и Revenue).

**Файл**: `src/swarm_powerbi_bot/agents/analyst.py` (строки ~341-356)

### 3. `_fallback_summary()` — период из sql_insight.params

После заголовка topic_desc вставить:
```
date_from = sql_insight.params.get("DateFrom") or sql_insight.params.get("date_from")
date_to = sql_insight.params.get("DateTo") or sql_insight.params.get("date_to")
if date_from and date_to:
    lines.append(f"Период: {df} — {dt}")
```

Поддержать `date` объекты (.isoformat()) и строки ([:10]).

**Файл**: `src/swarm_powerbi_bot/agents/analyst.py` (строки ~270-276)

### 4. Default ветка — float форматирование

В generic preview (строки ~305-307) добавить:
```python
if isinstance(val, float):
    val = f"{val:,.2f}"
```

### 5. Тесты

- `test_statistics_money_rounding` — AvgCheck/TotalRevenue округлены до 2 знаков
- `test_fallback_shows_period` — текст содержит «Период:» если DateFrom/DateTo в params
- `test_total_revenue_translated` — нет raw «TotalRevenue» в выводе

**Файл**: `tests/test_analyst_fallback.py`

## Риски

Нет. Изменения только в форматировании текста, без влияния на логику агентов.
