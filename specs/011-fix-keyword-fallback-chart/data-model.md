# Data Model: Исправление маршрутизации и chart rendering

**Feature**: 011-fix-keyword-fallback-chart  
**Date**: 2026-04-15

## Существующие entity (без изменений)

### TopicEntry (topic_registry.py)

```python
@dataclass(frozen=True)
class TopicEntry:
    topic_id: str          # "statistics", "masters", "services", ...
    procedure: str         # "dbo.spKDO_Statistics", ...
    keywords: list[str]    # ["статистик", "сводк", ...] — для fallback scoring
    description: str       # "Статистика — сводные KPI-показатели"
```

- 15 тем зарегистрировано в `TOPICS`
- `detect_topic(question, last_topic)` — keyword scoring, используется как fallback
- `DEFAULT_TOPIC = "statistics"`

### Plan / MultiPlan (models.py)

```python
@dataclass
class Plan:
    objective: str
    topic: str            # topic_id из TopicEntry
    sql_needed: bool
    powerbi_needed: bool
    render_needed: bool
    notes: list[str]      # ["planner:llm", "topic:statistics"]
```

- `notes` содержит маркеры: `"planner:llm"` / `"planner:keyword"` — источник маршрутизации

## Модифицируемые структуры

### _FIELD_LABELS (analyst.py) — расширение

**Текущее состояние**: 22 маппинга SQL→русский.

**Добавляемые маппинги**:

| SQL поле | Русский label | Тема |
|----------|--------------|------|
| ServiceCategory | Категория услуг | services |
| ServiceCount | Кол-во услуг | services |
| MasterCategory | Специализация | masters |
| Rating | Рейтинг | masters |
| ReturningClients | Вернувшиеся клиенты | statistics |
| TotalHours | Часы работы | statistics |
| EndOfWeek | Неделя | trend |
| WeekLabel | Неделя | trend |

### _HIDDEN_FIELDS (analyst.py) — расширение

**Текущее состояние**: 10 полей (Phone, CRMId, ObjectId, MasterId, ClientId, Id, Top, SalonName, FirstVisit, LastCommResult, ServicePeriodDays).

**Добавляемые поля**:

| Поле | Причина скрытия |
|------|----------------|
| IsPrimary | Boolean-флаг, не информативен для пользователя |
| ServiceCategory | Внутренний классификатор |
| MasterCategory | Внутренний классификатор |

### _PREFERRED_VALUE (chart_renderer.py) — исправление

| topic | Текущее значение | Новое значение | Причина |
|-------|-----------------|---------------|---------|
| services | Revenue | ServiceCount | SP возвращает ServiceCount, Revenue нет |
| masters | Revenue | TotalRevenue | Поле называется TotalRevenue |

### _pick_label_value() (chart_renderer.py) — boolean exclusion

В `skip` set добавить: `IsPrimary`.  
В проверку `isinstance(val, (int, float))` добавить `and not isinstance(val, bool)` — Python `bool` является подклассом `int`.

### _RE_MONTH_BARE (sql_client.py) — новый regex

```python
_RE_MONTH_BARE = re.compile(
    r"\b(январ\w*|феврал\w*|март\w*|апрел\w*|ма[йя]\w*|"
    r"июн\w*|июл\w*|август\w*|сентябр\w*|октябр\w*|ноябр\w*|декабр\w*)\b"
    r"(?:\s+(\d{4}))?",
    re.IGNORECASE,
)
```

Используется в `has_period_hint()` для распознавания месяцев без предлога «за».

### Каталог методов для LLM (planner.py) — новая функция

```python
def _build_method_catalog(self) -> str:
    """Формирует текстовый каталог legacy-процедур для LLM system prompt."""
```

**Источники данных**:
1. `TOPICS` из `topic_registry.py` → procedure, description
2. `_FIELD_LABELS` из `analyst.py` → колонки с русскими именами

**Выходной формат** (строка для system prompt):
```
Доступные методы:
- statistics (spKDO_Statistics): Статистика — сводные KPI-показатели
  Колонки: Выручка (₽), Визиты, Уникальные клиенты, Средний чек (₽)
- masters (spKDO_Masters): Мастера — загрузка, эффективность
  Колонки: Мастер, Выручка (₽), Визиты
...
```

## Связи между entity

```
TopicEntry ──uses──► detect_topic() ──fallback──► PlannerAgent.run()
                                                        │
                                                   LLM primary
                                                        │
                                                        ▼
                                               _build_method_catalog()
                                                   │         │
                                    TopicEntry.description    _FIELD_LABELS keys
                                                        │
                                                        ▼
                                                  Plan(topic=...)
                                                   │         │
                                    AnalystAgent._fallback_summary()
                                    (uses _FIELD_LABELS, _HIDDEN_FIELDS)
                                                        │
                                    ChartRenderer._pick_label_value()
                                    (uses _PREFERRED_VALUE, skip set)
```

## Валидация

- `_FIELD_LABELS` MUST покрывать все поля из `aggregate_catalog.yaml:returns`
- `_PREFERRED_VALUE[topic]` MUST быть подмножеством реальных колонок SP
- `_HIDDEN_FIELDS` ∩ `_PREFERRED_VALUE.values()` = ∅ (не скрываем то, что показываем на графике)
- `_build_method_catalog()` возвращаемый текст MUST содержать все 15 topics из `TOPICS`
