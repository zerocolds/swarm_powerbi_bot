# Contract: Keyword Fallback и Display Fixes

**Feature**: 011-fix-keyword-fallback-chart  
**Date**: 2026-04-16 (updated post-critique)

## Контракт detect_topic() — улучшенный keyword fallback

### topic_registry.detect_topic()

```python
def detect_topic(question: str, last_topic: str = "") -> str:
    """Определяет тему вопроса по ключевым словам (scoring + контекстные правила)."""
```

**Текущее поведение**: `sum(1 for kw in entry.keywords if kw in text)` — простой подсчёт.

**Новое поведение**: Базовый scoring + контекстные правила:
- «выручка за неделю» → `statistics` (период + «выручк» → statistics boost)
- «кто больше принёс денег?» → `masters` (ranking + «денег» → masters boost)
- «популярные услуги» → `services` (прямое совпадение сохраняется)
- «почему упала выручка?» → `statistics` (аналитический вопрос → statistics)

**Обратная совместимость**: Все текущие прямые маппинги (отток, уходящие, прогноз) сохраняются. Контекстные правила влияют только на неоднозначные случаи.

## Контракт fallback summary

### AnalystAgent._fallback_summary()

**Поведение для неизвестных полей (FR-005)**:
- Если поле в `_HIDDEN_FIELDS` → пропускается
- Если поле в `_FIELD_LABELS` → отображается с русским label
- Если поле НЕ в `_FIELD_LABELS` и НЕ в `_HIDDEN_FIELDS` → **пропускается** (не отображается raw)

**Текущий код** (analyst.py:304): `label = _FIELD_LABELS.get(key, key)` — fallback на raw key.
**Новый код**: `if key not in _FIELD_LABELS: continue` — пропуск.

## Контракт chart rendering

### ChartRenderer._pick_label_value()

**Поведение для boolean полей (FR-008)**:
- `isinstance(val, bool)` → пропускается (bool — подкласс int в Python)
- `IsPrimary` добавляется в `skip` set
- `_PREFERRED_VALUE[topic]` → проверяется первым

**Исправления _PREFERRED_VALUE**:
- `services` → `ServiceCount` (было `Revenue`)
- `masters` → `TotalRevenue` (было `Revenue`)

## Контракт has_period_hint()

### sql_client.has_period_hint()

**Расширенное поведение (FR-009, FR-010, FR-011)**:
- `"выручка за март"` → `True` (текущее, через _RE_MONTH)
- `"выручка март"` → `True` (новое, через _RE_MONTH_BARE)
- `"сравни март и апрель"` → `True` (новое)
- `"с марта по апрель"` → `True` (новое)
- `"мастер Марта"` → `False` (word boundary — «Марта» после имени не матчит как месяц)
- `"как дела"` → `False` (без изменений)

**Реализация**: `_RE_MONTH_BARE` с `\b` word boundaries для минимизации false positives на именах.

## Контракт circuit breaker

### LLMClient.plan_query()

**Новое поведение (FR-012)**:
- Проверка `_cb_open_until` в начале (аналогично `plan_aggregates()`)
- При timeout/ошибке: `_cb_failures += 1`
- При `_cb_failures >= threshold`: `_cb_open_until = now + cooldown`
- Переиспользует существующий CB state из `__init__`

## Гарантии обратной совместимости

1. `run()` возвращает `Plan` с теми же полями — потребители не меняются
2. `notes` маркеры сохраняются: `"planner:llm"` / `"planner:keyword"`
3. `detect_topic()` — расширение scoring, signature неизменна
4. `_FIELD_LABELS` — только добавления, без удалений/переименований
5. `has_period_hint()` — расширение, все существующие True-кейсы сохраняются
6. `plan_query()` — при CB open возвращает None (как при timeout), потребитель уже обрабатывает
