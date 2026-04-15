# Data Model: Semantic Aggregate Layer

## Новые модели Python (models.py)

### AggregateQuery
Один запрос к агрегату из каталога.
```
AggregateQuery:
  aggregate_id: str          # id из aggregate-catalog.yaml (whitelist)
  params: dict               # типизированные параметры
    date_from: date          # YYYY-MM-DD (required)
    date_to: date            # YYYY-MM-DD (required)
    object_id: int | None    # SalonId
    master_id: int | None    # из tbMasters
    group_by: str | None     # enum: master/service/week/month/salon/channel/status/reason/result/manager/list
    filter: str | None       # enum: all/outflow/leaving/forecast/noshow/quality/birthday
    top_n: int               # 1..50, default 20
  label: str                 # человекочитаемое описание запроса (для AnalystAgent)
```

### MultiPlan
План выполнения для одного вопроса пользователя (результат двухшагового planning).
```
MultiPlan:
  objective: str             # цель вопроса
  intent: str                # comparison | single | decomposition | trend
  categories: list[str]      # выбранные категории (шаг 1)
  queries: list[AggregateQuery]  # до 10 запросов (шаг 2)
  topic: str                 # для follow-ups и chart type
  render_needed: bool
  notes: list[str]           # planner annotations
```

### AggregateResult
Результат одного агрегатного запроса.
```
AggregateResult:
  aggregate_id: str
  label: str
  rows: list[dict]
  row_count: int
  duration_ms: int
  status: str                # ok | error | timeout
  error: str | None
```

### ComparisonResult
Результат сравнения двух наборов данных.
```
ComparisonResult:
  period_a: str              # "Март 2026"
  period_b: str              # "Апрель 2026"
  results_a: AggregateResult
  results_b: AggregateResult
  deltas: dict[str, float]   # метрика → процент изменения
```

## YAML-каталоги (catalogs/)

### category-index.yaml
Компактный индекс для шага 1 LLM planning.
```
categories:
  - id: clients
    name: "Клиенты"
    description: "Статусы клиентов: отток, уходящие, прогноз, контроль качества, недошедшие"
    keywords: [клиент, отток, уход, прогноз, качество, недошед, база]

  - id: revenue
    name: "Выручка и финансы"
    description: "Выручка, средний чек, оплаты, абонементы"
    keywords: [выручк, чек, оплат, абонемент, деньг, финанс]

  - id: masters
    name: "Мастера"
    description: "Показатели мастеров: выручка, клиенты, загрузка, обучение"
    keywords: [мастер, специалист, загрузк, обучен]

  - id: services
    name: "Услуги"
    description: "Услуги: популярность, выручка, средний чек, категории"
    keywords: [услуг, процедур, категори]

  - id: communications
    name: "Коммуникации"
    description: "Звонки, ОПЗ, лист ожидания, результаты коммуникаций"
    keywords: [коммуникац, звонок, опз, ожидан, менеджер]

  - id: trends
    name: "Тренды и динамика"
    description: "Динамика по неделям/месяцам, сравнения периодов"
    keywords: [тренд, динамик, по неделям, по месяцам, сравн]

  - id: referrals
    name: "Привлечение"
    description: "Каналы привлечения, рефералы, источники клиентов"
    keywords: [реферал, привлечен, канал, источник]

  - id: overview
    name: "Общая статистика"
    description: "KPI, сводка, общие показатели салона"
    keywords: [статистик, сводк, kpi, общ, итог]
```

### aggregate-catalog.yaml (формат одного агрегата)
```
aggregates:
  - id: client_outflow
    name: "Отток клиентов"
    category: clients
    description: "Клиенты без визита > ServicePeriod + 31..240 дней. Показывает: имя, телефон, дней без визита, сумму визитов."
    parameters:
      - name: date_from
        type: date
        required: true
      - name: date_to
        type: date
        required: true
      - name: object_id
        type: int
        required: true
        description: "ID салона"
      - name: top_n
        type: int
        required: false
        default: 20
        min: 1
        max: 50
    returns:
      - ClientName: str
      - Phone: str
      - LastVisit: date
      - DaysSinceLastVisit: int
      - TotalVisits: int
      - TotalSpent: float
    related_dax: "Статус клиента для обработки (Отток)"
    examples:
      - question: "покажи отток за месяц"
        params: {date_from: "2026-03-01", date_to: "2026-03-31", object_id: 506770}
      - question: "сколько клиентов ушло"
        params: {date_from: "2026-03-16", date_to: "2026-04-15", object_id: 506770}
```

## SQL: materialized агрегаты

### Indexed Views (предрассчитанные)
Для агрегатов без динамических WHERE-фильтров:
- `vwKDO_RevenueSummary` — выручка, визиты, клиенты, средний чек по ObjectId + EndOfWeek/EndOfMonth
- `vwKDO_MasterSummary` — выручка, клиенты, часы по мастерам + ObjectId + период
- `vwKDO_ServiceSummary` — услуги, количество, выручка по ObjectId + период
- `vwKDO_ChannelSummary` — каналы привлечения, клиенты, выручка

### TVF (динамические, с параметрами)
Для агрегатов с фильтрами по статусу клиента:
- Существующие v1/v2 SP — оборачиваются в dispatcher
- `fnKDO_ClientStatus` — без изменений, используется как building block
- Gap-агрегаты — создаются по результатам gap-анализа

## Связи между компонентами

```
User Question
  │
  ▼
TelegramSwarmBot (без изменений)
  │
  ▼
SwarmOrchestrator.handle_question()
  │
  ├──► PlannerAgent.run()
  │     ├── Шаг 1: LLMClient.classify_categories(question, category-index.yaml)
  │     │           → {"categories": [...], "intent": "..."}
  │     ├── Шаг 2: LLMClient.select_aggregates(question, intent, filtered_catalog)
  │     │           → MultiPlan с list[AggregateQuery]
  │     └── Fallback: TopicRegistry.detect_topic() → single AggregateQuery
  │
  ├──► MasterResolver.resolve(question, object_id) [если имя в вопросе]
  │     └── SELECT from tbMasters + difflib.SequenceMatcher
  │
  ├──► SQLAgent.run_multi(plan: MultiPlan) [параллельно, asyncio.gather]
  │     ├── AggregateRegistry.validate(query) → whitelist + param check
  │     ├── ParameterValidator.validate(params) → typed validation
  │     ├── SQLClient.execute_aggregate(aggregate_id, params) [×N, max 10]
  │     └── QueryLogger.log(user_id, aggregate_id, params, duration, status)
  │
  ├──► PowerBIModelAgent.run() [параллельно с SQLAgent, без изменений]
  │
  ├──► ChartRenderer.render(topic, results, plan.intent)
  │     ├── single → существующая логика (bar/hbar/line/pie)
  │     ├── comparison → grouped bar / multi-line + delta annotations
  │     └── decomposition → multi-panel or summary bar
  │
  └──► AnalystAgent.run(question, results: list[AggregateResult], plan)
        ├── Multi-result synthesis
        ├── Comparison text: "Выручка выросла на X%"
        └── Follow-ups based on topic + intent
```
