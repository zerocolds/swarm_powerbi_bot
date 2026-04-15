# Implementation Plan: Fix comparison chart и текстовое описание

**Feature**: 003-006-fix-comparison-chart
**Issues**: #5, #6, #7
**Date**: 2026-04-15

## Technical Context

- Python 3.11+, matplotlib 3.8+, pyodbc
- `render_comparison()` получает только `topic`, `rows_a/b`, `label_a/b` — нет метаданных о колонках
- `AggregateResult` не несёт информации о group_by, label_col, value_col
- Каталог `aggregate-catalog.yaml` содержит `returns` (список колонок) и `allowed_group_by`, но не размечает label vs value
- LLM часто недоступен → fallback-тексты должны быть самодостаточными

## Архитектурные решения

### Q1: Как render_comparison() узнаёт какая колонка — метрика, а какая — группировка?

**Решение: передать `group_by` через AggregateResult + конвенционный маппинг в renderer.**

Цепочка:
1. `AggregateQuery.params` уже содержит `group_by` (задаётся planner'ом)
2. `sql_agent.run_multi()` копирует `group_by` в новое поле `AggregateResult.group_by`
3. Orchestrator передаёт `group_by` в `render_comparison()` как новый kwarg
4. `render_comparison()` использует маппинг `group_by → label_col`:

```python
_GROUP_BY_LABEL_COL = {
    "status": "ClientStatus",
    "master": "MasterName",
    "reason": "Reason",
    "result": "Result",
    "manager": "Manager",
    "service": "ServiceName",
    "salon": "SalonName",
    "channel": "Channel",
}
```

Когда `label_col` найдена в данных → per-row grouped bars (ось X = значения label_col).
Когда нет → текущее поведение (агрегация всех строк в одну сумму per metric).

**Альтернативы отвергнуты:**
- Передавать `aggregate_registry` в renderer — связывает рендер с каталогом
- Добавлять `label_col`/`value_col` в `AggregateResult` — требует парсинг каталога в sql_agent, избыточно
- Хардкод в renderer по topic — хрупко, не масштабируется

### Q2: Как analyst формирует текст comparison — откуда берёт названия метрик на русском?

**Решение: `_METRIC_LABELS` dict в analyst.py.**

```python
_METRIC_LABELS: dict[str, str] = {
    "ClientCount": "Клиенты",
    "TotalVisits": "Визиты",
    "TotalSpent": "Сумма трат",
    "Revenue": "Выручка",
    "AvgCheck": "Средний чек",
    "UniqueClients": "Уникальные клиенты",
    "Visits": "Визиты",
    "ActiveMasters": "Мастера",
    "TotalHours": "Часов работы",
    "BookedCount": "Записались",
    "RefusedCount": "Отказались",
    "TotalCount": "Всего коммуникаций",
}
```

Используется в:
- `_fallback_multi()` — вместо "label: N записей" → "Отток: 22 клиента в марте, 18 в апреле (−18%)"
- `format_comparison()` — вместо "ClientCount" → "Клиенты"

Fallback при отсутствии в dict: оставить англ. название как есть.

### Q3: Как fallback_summary переводит сырые поля?

**Решение: `_FIELD_LABELS` dict + topic-specific форматтеры в analyst.py.**

```python
_FIELD_LABELS: dict[str, str] = {
    "ClientName": "Клиент",
    "DaysSinceLastVisit": "Дней с последнего визита",
    "DaysOverdue": "Дней просрочки",
    "TotalSpent": "Сумма трат",
    "TotalVisits": "Визитов",
    "LastVisit": "Последний визит",
    "ExpectedNextVisit": "Ожидаемый визит",
    "ServicePeriodDays": "Период визитов (дни)",
    "Revenue": "Выручка",
    "AvgCheck": "Средний чек",
    "Visits": "Визиты",
    "UniqueClients": "Уникальные клиенты",
}
```

Скрытые поля (не показывать в fallback): `Phone`, `CRMId`, `ObjectId`, `MasterId`, `ClientId`, `Id`, `Top`.

**Topic-specific форматтеры** для outflow/leaving:

```python
def _format_outflow_summary(rows: list[dict]) -> str:
    count = len(rows)
    overdue = [r.get("DaysOverdue", 0) or 0 for r in rows]
    min_o, max_o = min(overdue), max(overdue)
    # Топ по тратам
    top = max(rows, key=lambda r: r.get("TotalSpent", 0) or 0)
    top_name = top.get("ClientName", "?")
    top_spent = top.get("TotalSpent", 0)
    top_visits = top.get("TotalVisits", 0)
    return (
        f"Отток клиентов: {count} записей за период ...\n"
        f"Просрочка визитов — от {min_o} до {max_o} дней.\n"
        f"Наибольшая сумма трат у клиента {top_name} — {top_spent:,.0f} ₽ за {top_visits} визитов."
    )
```

## Project Structure (изменяемые файлы)

```
src/swarm_powerbi_bot/
  models.py                    # AggregateResult += group_by field
  agents/
    analyst.py                 # _METRIC_LABELS, _FIELD_LABELS, topic formatters
  services/
    chart_renderer.py          # render_comparison — per-row grouped bars
  orchestrator.py              # передача group_by в render_comparison
tests/
  test_chart_renderer.py       # тесты render_comparison с group_by
  test_analyst.py              # тесты fallback текстов
```

## Phases

### Phase 1: Data layer — AggregateResult.group_by

1. Добавить `group_by: str = ""` в `AggregateResult` dataclass
2. В `sql_agent.run_multi()` — копировать `query.params.get("group_by", "")` в result

### Phase 2: Chart — render_comparison per-row grouped bars

1. Добавить `_GROUP_BY_LABEL_COL` маппинг
2. Добавить `group_by: str = ""` kwarg в `render_comparison()`
3. Новая ветка логики: если `group_by` → label_col найден в данных → per-row bars
4. Сохранить текущую ветку для `group_by=""` или `group_by=total`
5. Обновить orchestrator: передать `group_by` из AggregateResult

### Phase 3: Analyst — comparison текст с дельтами

1. Добавить `_METRIC_LABELS` dict
2. Переписать `_fallback_multi()`: для каждого ok_result — ключевая метрика + значение + дельта
3. Обновить `format_comparison()` — использовать русские названия метрик

### Phase 4: Analyst — fallback_summary перевод полей

1. Добавить `_FIELD_LABELS` dict и `_HIDDEN_FIELDS` set
2. Добавить topic-specific форматтеры: `_format_outflow_summary()`, `_format_statistics_summary()`
3. Обновить `_fallback_summary()` — использовать форматтер по topic, fallback на translated fields

### Phase 5: Tests

1. `test_chart_renderer.py` — render_comparison с group_by=status (per-row bars), group_by=total (legacy), пустые данные
2. `test_analyst.py` — _fallback_multi с дельтами, _fallback_summary с переводом, topic formatters
