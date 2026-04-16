# Quickstart: Исправление маршрутизации и chart rendering

**Feature**: 011-fix-keyword-fallback-chart  
**Date**: 2026-04-15

## Что меняется

4 production-файла, 4 направления фиксов:

| Файл | Что делаем | FR |
|------|-----------|-----|
| `services/topic_registry.py` | Контекстные правила в `detect_topic()` | FR-001 |
| `services/llm_client.py` | Circuit breaker для `plan_query()` | FR-012 |
| `agents/analyst.py` | Дополнить `_FIELD_LABELS`, `_HIDDEN_FIELDS` | FR-004, FR-005, FR-006 |
| `services/chart_renderer.py` | Исправить `_PREFERRED_VALUE`, boolean exclusion | FR-007, FR-008 |
| `services/sql_client.py` | Расширить `has_period_hint()` | FR-009, FR-010 |

## Порядок реализации

### 1. analyst.py — field labels (самое простое)

Добавить маппинги в `_FIELD_LABELS`:
```python
"ServiceCategory": "Категория услуг",
"ServiceCount": "Кол-во услуг",
"MasterCategory": "Специализация",
"Rating": "Рейтинг",
"ReturningClients": "Вернувшиеся клиенты",
"TotalHours": "Часы работы",
"EndOfWeek": "Неделя",
"WeekLabel": "Неделя",
```

Добавить в `_HIDDEN_FIELDS`:
```python
"IsPrimary", "ServiceCategory", "MasterCategory"
```

В `_fallback_summary()` — скрывать поля без маппинга (не показывать raw).

### 2. chart_renderer.py — preferred values

Исправить `_PREFERRED_VALUE`:
```python
"services": "ServiceCount",   # было "Revenue"
"masters": "TotalRevenue",    # было "Revenue"
```

В `_pick_label_value()` — добавить `IsPrimary` в `skip` и проверку `isinstance(val, bool)`.

### 3. sql_client.py — period hint

Добавить `_RE_MONTH_BARE` regex (месяцы без «за»).

Обновить `has_period_hint()`:
```python
if _RE_MONTH.search(text) or _RE_MONTH_BARE.search(text) or _RE_RANGE.search(text):
    return True
```

### 4. topic_registry.py — контекстные правила scoring

Добавить `_CONTEXT_RULES` — контекстные правила для неоднозначных вопросов:
```python
_CONTEXT_RULES = [
    # (паттерн в тексте, topic_boost, score_bonus)
    # Период + «выручк» → statistics, не services
    (lambda t: any(p in t for p in ("недел", "месяц", "квартал")) and "выручк" in t, "statistics", 3),
    # Ranking + финансы → masters
    (lambda t: any(p in t for p in ("кто больш", "топ", "рейтинг")) and any(p in t for p in ("денег", "выручк", "принёс", "принес")), "masters", 3),
]
```

### 5. llm_client.py — circuit breaker для plan_query()

Добавить CB-проверку в начало `plan_query()`:
```python
async with self._cb_lock:
    now = time.monotonic()
    if self._cb_open_until > now:
        return None
```

## Тестирование

```bash
# Запуск всех тестов
uv run pytest -q

# Только новые тесты
uv run pytest tests/test_field_labels.py tests/test_chart_preferred.py tests/test_period_hint.py tests/test_llm_routing.py -v

# Integration тесты (требуют Ollama + MSSQL)
uv run pytest tests/integration/ -v -m "not slow"
```

## Проверка в Telegram

После деплоя проверить 4 сценария:
1. «какая выручка за неделю?» → statistics (не services)
2. «топ мастеров по выручке» → ответ с русскими названиями полей
3. «популярные услуги» → chart по ServiceCount (не IsPrimary)
4. «сравни март и апрель» → comparison без кнопок периода
