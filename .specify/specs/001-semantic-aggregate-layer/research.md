# Research: Semantic Aggregate Layer

## R-001: Извлечение DataModelSchema из PBIX

**Decision**: Python `zipfile` + `json` как **dev-time утилита** (scripts/bootstrap/). Это одноразовая bootstrap-операция, НЕ runtime-зависимость бота.

**Rationale**: PBIX нужен чтобы ПОНЯТЬ семантику Power BI модели и ПЕРЕНЕСТИ её в SQL-агрегаты + YAML-каталоги. После bootstrap PBIX боту не нужен. Скрипты извлечения запускаются разработчиком локально, не попадают в Docker-образ и не являются зависимостью бота.

**Alternatives considered**:
- pbi-tools CLI (.NET) — fallback если zipfile+json не парсит DataModelSchema
- Tabular Editor CLI — избыточен для one-time read-only извлечения
- Power BI REST API — требует Azure AD tenant, не работает с локальными файлами

**Implementation notes**:
- Скрипты живут в `scripts/bootstrap/` — dev-time only
- PBIX содержит `DataModelSchema` в root или в `DataModel/DataModelSchema`
- Файл может быть UTF-16 LE с BOM — нужна детекция encoding
- JSON парсится в dict → `model.tables[]`, `model.relationships[]`, `model.tables[].measures[]`
- Результат: `catalogs/bootstrap/semantic-model.yaml` (справочный артефакт)
- На основе semantic-model.yaml создаются runtime-каталоги: `catalogs/semantic-catalog.yaml`, `catalogs/aggregate-catalog.yaml`, `catalogs/category-index.yaml`
- Runtime-каталоги коммитятся в репо и обновляются только при изменении PBIX (CI-задача)
- В Docker-образ бота попадают только `catalogs/*.yaml`, не `catalogs/bootstrap/` и не `scripts/bootstrap/`

## R-002: Materialized агрегаты в MSSQL

**Decision**: SQL Server Indexed Views для часто используемых агрегатов (статистика, выручка по мастерам, тренды). TVF для агрегатов с динамическими параметрами (фильтры по статусу клиента).

**Rationale**: Indexed Views в SQL Server физически хранят результат GROUP BY и автоматически обновляются при INSERT/UPDATE/DELETE базовых таблиц. Overhead хранения обычно 5-15% от базовых таблиц (далеко от лимита 3x). Для агрегатов с WHERE-фильтрами (outflow/leaving/forecast) indexed views не подходят — используем TVF с предвычисленным fnKDO_ClientStatus.

**Alternatives considered**:
- Materialized tables с триггерами — сложнее, риск рассинхронизации, overhead на INSERT
- Redis/memory cache — дополнительная инфраструктура, не нужна при малом количестве клиентов
- Columnstore indexes — избыточно для объёмов данных салонов красоты

**Implementation notes**:
- Indexed views требуют `SCHEMABINDING` и определённых SET options
- Ограничение: нельзя использовать OUTER JOIN, subqueries, EXISTS, UNION в indexed view
- Для сложных агрегатов (с JOIN через fnKDO_ClientStatus) — оставляем TVF
- Оценка overhead: ~8 indexed views × средний размер салона (50K записей) ≈ 100-400MB дополнительно ≪ 3x

## R-003: Двухшаговый LLM planning

**Decision**: Два вызова LLM за один вопрос пользователя. Шаг 1: классификация по категориям (быстрый, ~200 токенов вход). Шаг 2: выбор агрегатов из детального каталога выбранных категорий (~1-2K токенов вход).

**Rationale**: Полный каталог может превысить context window GLM-5 при росте числа агрегатов. Двухшаговый подход ограничивает контекст на шаге 2, повышает точность выбора, поддерживает кросс-доменные запросы (шаг 1 выбирает несколько категорий).

**Alternatives considered**:
- Полный каталог в prompt — не масштабируется при >50 агрегатах
- Embedding pre-filter (RAG) — дополнительная инфраструктура, не нужна на текущем масштабе
- Один шаг с категорийным маркером — менее точен для кросс-доменных запросов

**Implementation notes**:
- category-index.yaml: ~10-15 категорий, по 2-3 строки каждая (описание + ключевые слова)
- Шаг 1 prompt: system = category-index + semantic-catalog (бизнес-правила), user = вопрос
- Шаг 1 output: JSON `{"categories": ["clients", "revenue"], "intent": "comparison"}`
- Шаг 2 prompt: system = detailed aggregates для выбранных категорий, user = вопрос + intent
- Шаг 2 output: JSON `{"queries": [{"aggregate_id": "...", "params": {...}}, ...]}`
- Temperature 0.1 для обоих шагов (deterministic planning)
- Дополнительная латентность: ~1-2 сек (два sequential LLM calls вместо одного)

## R-004: Fuzzy-match имён мастеров

**Decision**: Per-request SQL запрос к tbMasters с LIKE + Levenshtein distance в Python.

**Rationale**: Актуальные данные важнее скорости (мастера уходят/приходят). Объём невелик (типично 5-30 мастеров на салон) — запрос быстрый. Levenshtein в Python покрывает опечатки ("Ана" → "Анна").

**Alternatives considered**:
- Кеш при старте бота — не обновляется при добавлении мастера
- SQL Server SOUNDEX — не работает с кириллицей
- Full-text search — избыточно для 5-30 записей

**Implementation notes**:
- `SELECT Id, Name FROM tbMasters WHERE ObjectId = @ObjectId`
- В Python: сравнение через `difflib.SequenceMatcher` (stdlib, без зависимостей)
- Порог similarity: ≥0.6 для коротких имён, ≥0.7 для длинных
- Если несколько кандидатов — возвращаем всех, LLM disambiguates
- Если 0 кандидатов — AnalystAgent отвечает "мастер не найден"

## R-005: Structured logging агрегатных вызовов

**Decision**: Python `logging` module с JSON formatter. Один лог-файл `aggregate_queries.log`.

**Rationale**: Минимальный overhead, stdlib, достаточно для аудита и отладки. Структурированный JSON позволяет будущий экспорт в ELK/Grafana.

**Alternatives considered**:
- structlog — дополнительная зависимость, избыточна
- SQL-таблица для логов — усложняет, нарушает read-only принцип
- stdout JSON (Docker logs) — годится, но нет персистентности

**Implementation notes**:
- Поля: `timestamp`, `user_id`, `aggregate_id`, `params` (sanitized), `duration_ms`, `row_count`, `status` (ok/error/timeout)
- НЕ логируем: data ответа, connection strings, tokens
- Log rotation: 10MB × 5 файлов (по умолчанию)
- В Docker: дублируем в stdout для `docker logs`

## R-006: Сравнительные графики в matplotlib

**Decision**: Расширение существующего `chart_renderer.py`: grouped bar chart для сравнения периодов, multi-line chart для трендов с несколькими рядами.

**Rationale**: matplotlib уже в зависимостях, существующий код работает. Grouped bar — стандартная фича matplotlib. Не нужна новая библиотека.

**Alternatives considered**:
- plotly — интерактивные графики, но Telegram показывает только PNG
- seaborn — красивее, но дополнительная зависимость
- таблица вместо графика — менее наглядно для сравнений

**Implementation notes**:
- Grouped bar: `ax.bar(x - width/2, ...)` + `ax.bar(x + width/2, ...)` с легендой периодов
- Multi-line comparison: несколько `ax.plot()` с разными цветами/стилями
- Delta-аннотация: "+12.5%" или "−3.2%" над барами
- Цветовое кодирование: зелёный для роста, красный для падения
