# Quickstart: Semantic Aggregate Layer

## Порядок разработки

### Phase 0: Discovery (dev-time bootstrap, выполняется ОДИН РАЗ разработчиком)

> PBIX нужен только здесь — чтобы понять семантику и перенести её в SQL + каталоги.
> После Phase 0 PBIX боту не нужен. Скрипты НЕ попадают в Docker-образ.

```bash
# 1. Извлечь семантическую модель из PBIX (dev-time утилита)
python scripts/bootstrap/extract_pbix.py powebi/КДО\ 3.2.1.pbix catalogs/bootstrap/semantic-model.yaml

# 2. Создать маппинг PBIX→SQL (dev-time)
python scripts/bootstrap/map_pbix_to_sql.py catalogs/bootstrap/semantic-model.yaml sql/create_kdo_procedures.sql catalogs/bootstrap/pbix-to-sql-mapping.yaml

# 3. Сгенерировать runtime-каталоги для LLM (dev-time → коммитятся в репо)
python scripts/bootstrap/generate_semantic_catalog.py catalogs/bootstrap/semantic-model.yaml catalogs/semantic-catalog.yaml

# 4. Gap-анализ (dev-time)
python scripts/bootstrap/gap_analysis.py catalogs/bootstrap/pbix-to-sql-mapping.yaml catalogs/bootstrap/gaps.md

# 5. Ручная проверка gaps.md → решить какие агрегаты создавать

# 6. Коммит runtime-каталогов
git add catalogs/semantic-catalog.yaml catalogs/aggregate-catalog.yaml catalogs/category-index.yaml
```

### Phase 1: SQL layer (dev-time, выполняется DBA/разработчиком)

```bash
# 1. Создать materialized aggregates (indexed views)
# sql/create_materialized_aggregates.sql → выполнить на MSSQL

# 2. Создать gap-агрегаты (TVF)
# sql/create_gap_aggregates.sql → выполнить на MSSQL (после утверждения человеком!)

# 3. Сформировать aggregate-catalog.yaml + category-index.yaml → коммит в репо
# Каждый агрегат: id, name, description, parameters, returns, examples

# 4. Верифицировать агрегаты vs DAX (≤1% допуск, dev-time)
python scripts/bootstrap/validate_aggregates.py catalogs/aggregate-catalog.yaml --object-id 506770
```

### Phase 2: Python layer

```bash
# Новые модули в src/swarm_powerbi_bot/services/:
# aggregate_registry.py (загрузка каталогов + whitelist + param validation) → master_resolver.py → query_logger.py

# Изменённые модули:
# agents/planner.py (одношаговый planning по полному каталогу)
# agents/sql.py (multi-query)
# agents/analyst.py (multi-result synthesis)
# services/llm_client.py (новые prompts)
# services/chart_renderer.py (grouped bar, comparison)
# orchestrator.py (MultiPlan flow)
# models.py (AggregateQuery, MultiPlan, AggregateResult, ComparisonResult)

# Запуск тестов
pytest -q

# Линтинг
ruff check src/ tests/
ruff format --check src/ tests/
```

### Phase 3: Сравнения

```bash
# Расширение PlannerAgent: intent=comparison → LLM выбирает два запроса с разными периодами
# Расширение ChartRenderer: grouped bar chart + delta annotations
# Расширение AnalystAgent: comparison text template
```

### Phase 4: Композиция

```bash
# Расширение PlannerAgent: intent=decomposition → до 5 запросов разных агрегатов
# Расширение AnalystAgent: factor analysis text
```

## Зависимости между фазами

```
Phase 0 (Discovery) ← DEV-TIME ONLY, разработчик локально
  │
  ├── catalogs/bootstrap/semantic-model.yaml ─► Phase 1 (понимание семантики)
  ├── catalogs/bootstrap/gaps.md ─────────────► Phase 1 (какие агрегаты создавать)
  │
  └──► КОММИТ runtime-каталогов в репо:
       catalogs/semantic-catalog.yaml
       catalogs/aggregate-catalog.yaml
       catalogs/category-index.yaml

Phase 1 (SQL layer) ← DEV-TIME, DBA выполняет SQL на MSSQL
  │
  ├── SQL indexed views + TVF ─► runtime (бот подключается через pyodbc)
  └── aggregate-catalog.yaml ──► Phase 2 (registry, planner)

Phase 2 (Python layer) ← КОД БОТА, runtime
  │
  ├── Бот загружает catalogs/*.yaml при старте
  ├── PlannerAgent v2 ──────► Phase 3, Phase 4
  └── SQLAgent multi-query ─► Phase 3, Phase 4

Phase 3 (Comparisons) ← runtime
  │
  └── comparison charts ────► Phase 4 (Composition)
```

## Что попадает в Docker-образ бота (runtime)

```
src/                     # Python-код бота
catalogs/*.yaml          # 3 runtime-каталога (semantic-catalog, aggregate-catalog, category-index)
```

## Что НЕ попадает в Docker (dev-time only)

```
powebi/*.pbix            # PBIX-файл (нужен только для bootstrap)
scripts/bootstrap/       # Утилиты извлечения PBIX
catalogs/bootstrap/      # Промежуточные артефакты Phase 0
sql/                     # DDL-скрипты (выполняются DBA отдельно)
```

## Проверка

```bash
# Полный прогон тестов (77 существующих + новые)
pytest -q

# Проверка backward compatibility
pytest tests/test_planner.py tests/test_topic_registry.py tests/test_orchestrator.py -q

# Линтинг
ruff check && ruff format --check

# Docker build
docker build -t swarm-powerbi-bot .
```
