# Research: Исправление маршрутизации и chart rendering

**Feature**: 011-fix-keyword-fallback-chart  
**Date**: 2026-04-15

## R1: Диагностика маршрутизации — почему `run()` маршрутизирует неправильно?

**Finding**: `PlannerAgent.run()` **уже** использует LLM-first routing (planner.py:458).

**Root cause analysis**:
1. `run()` вызывает `_llm_plan()` → `LLMClient.plan_query()` первым
2. `plan_query()` проверяет `self.settings.ollama_api_key` (llm_client.py:131)
3. Если `OLLAMA_API_KEY` не задан → `return None` → **всегда** keyword fallback
4. Keyword fallback: `detect_topic()` — `"выручк"` привязан к `services` (topic_registry.py:109)
5. Scoring: `sum(1 for kw in entry.keywords if kw in text)` — без контекста и весов

**Decision**: Улучшить keyword fallback scoring с контекстными правилами + circuit breaker для plan_query().

**Rationale**: LLM-путь уже работает корректно (когда доступен). `_PLANNER_SYSTEM_PROMPT` правильно различает statistics/services/masters. Проблема — keyword fallback слишком примитивен для graceful degradation. Нужно улучшить fallback, а не добавлять новый LLM-путь.

**Alternatives considered**:
- *Добавить второй LLM-путь с каталогом из TopicEntry*: Отклонено — дублирование уже существующего `_llm_plan()` + `_PLANNER_SYSTEM_PROMPT`.
- *Перевод всех потребителей на run_multi()*: Слишком большой scope — run() используется в legacy orchestrator путях.
- *Гибридный scoring (keywords + embeddings)*: Overcomplicated — достаточно контекстных правил в detect_topic().

## R2: Улучшение keyword fallback scoring

**Decision**: Добавить контекстные правила в `detect_topic()`.

**Approach**:
- Если вопрос содержит период-контекст («за неделю», «за месяц») + «выручк» → приоритет `statistics` над `services`
- Если вопрос содержит «кто больше/топ/рейтинг» + «денег/выручк» → приоритет `masters`
- Если вопрос содержит прямое указание услуг («популярные услуги», «топ услуг») → `services`
- Весовые модификаторы: контекстное совпадение → +2 к score темы

**Implementation**: Добавить `_CONTEXT_RULES` — список `(pattern, topic_boost)` правил, применяемых после базового scoring. Не менять signature `detect_topic()`.

**Alternatives considered**:
- *Каталог методов для нового LLM-промпта*: Отклонено (critique E1) — `run()` уже вызывает `_llm_plan()` с `_PLANNER_SYSTEM_PROMPT`, который корректно маршрутизирует.
- *Перевес keywords*: Частичное решение — помогает для «выручка за неделю», но не для «кто больше принёс денег».

## R3: Стратегия fallback при недоступности LLM

**Decision**: `topic_registry.detect_topic()` как fallback без изменений.

**Rationale**: Keyword scoring работает для 80% вопросов (основные темы). Проблема — edge cases с пересекающимися keywords. Как fallback это приемлемо. Circuit breaker уже не нужен — httpx timeout достаточен.

**Implementation**: В `run()` — try/except вокруг LLM-вызова, при ошибке → `detect_topic()`.

## R4: Расширение has_period_hint()

**Decision**: Добавить regex для распознавания месяцев без предлога «за».

**Rationale**: Текущий `_RE_MONTH` требует `за\s+` перед названием месяца. «Сравни **март** и апрель» не матчит. Нужен дополнительный regex `_RE_MONTH_BARE` без обязательного предлога.

**Implementation**:
```python
_RE_MONTH_BARE = re.compile(
    r"(январ\w*|феврал\w*|март\w*|апрел\w*|ма[йя]\w*|"
    r"июн\w*|июл\w*|август\w*|сентябр\w*|октябр\w*|ноябр\w*|декабр\w*)"
    r"(?:\s+(\d{4}))?",
    re.IGNORECASE,
)
```

В `has_period_hint()` добавить проверку `_RE_MONTH_BARE.search(text)`.

**Risk**: False positives на имена «Марта», «Майя». Митигация: проверять в контексте — если есть числовое слово рядом или тематический контекст.

## R5: Дополнение _FIELD_LABELS и _PREFERRED_VALUE

**Decision**: Полный аудит колонок всех SP и заполнение пробелов.

**Findings из кода**:

**_FIELD_LABELS** — отсутствуют:
| Поле | Тема | Предложенный label |
|------|------|-------------------|
| ServiceCategory | services | «Категория услуг» |
| IsPrimary | services | скрыть (_HIDDEN_FIELDS) |
| ServiceCount | services | «Кол-во услуг» |
| MasterCategory | masters | «Специализация» |
| Rating | masters | «Рейтинг» |
| UniqueClients | statistics | уже есть («Уникальные клиенты») |
| ActiveMasters | statistics | уже есть («Активные мастера») |
| Visits | statistics | уже есть («Визиты») |
| ReturningClients | statistics | «Вернувшиеся клиенты» |
| TotalHours | statistics | «Часы работы» |
| EndOfWeek | trend | «Неделя» |
| WeekLabel | trend | «Неделя» |

**_HIDDEN_FIELDS** — добавить:
- `IsPrimary` (boolean, не информативен)
- `ServiceCategory` (внутренний классификатор)
- `MasterCategory` (внутренний классификатор)

**_PREFERRED_VALUE** — исправить:
| Тема | Текущее | Исправленное | Причина |
|------|---------|-------------|---------|
| services | `Revenue` | `ServiceCount` | SP spKDO_Services возвращает ServiceCount, не Revenue |
| masters | `Revenue` | `TotalRevenue` | Поле называется TotalRevenue, не Revenue |

**Chart boolean exclusion**: В `_pick_label_value()` добавить `IsPrimary` в `skip` set и проверку `isinstance(val, bool)`.

## R6: Scope влияния на run_multi() и planner.py

**Decision**: `run_multi()` и `run()` не модифицируются (routing logic).

**Rationale**: Оба метода уже LLM-first с keyword fallback. `_FIELD_LABELS`, `_HIDDEN_FIELDS`, `_PREFERRED_VALUE` — общие для обоих путей (в analyst.py и chart_renderer.py), поэтому фиксы автоматически улучшат оба пути. Модифицируется только `detect_topic()` (keyword fallback) и `plan_query()` (circuit breaker).

## R7: Circuit breaker для plan_query() (critique E4)

**Decision**: Добавить circuit breaker в `plan_query()` аналогично `plan_aggregates()`.

**Rationale**: `plan_aggregates()` (llm_client.py:166-174) уже имеет CB: `_cb_failures`, `_cb_open_until`, `_cb_lock`. Но `plan_query()` (llm_client.py:122) не защищён — при каскадных timeout (Ollama down) каждый запрос ждёт full timeout. CB fields уже есть в `LLMClient.__init__` — нужно переиспользовать в `plan_query()`.

**Implementation**: Добавить проверку `self._cb_open_until` в начало `plan_query()` и инкремент `_cb_failures` при timeout/ошибке. Переиспользовать существующий CB state (общий для обоих методов).
