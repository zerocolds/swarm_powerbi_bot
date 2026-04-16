# swarm_powerbi_bot Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-15

## Active Technologies
- Microsoft SQL Server (pyodbc, ODBC Driver 17); materialized агрегаты (indexed views) с overhead ≤3x хранения (010-test-coverage)

- Python 3.11+ + python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8, selenium ≥4.22, python-dotenv ≥1.0.1 (001-semantic-aggregate-layer)

## Project Structure

```text
src/
  swarm_powerbi_bot/
    services/         # бизнес-логика: aggregate_registry, master_resolver, query_logger, ...
    agents/           # агенты: planner, sql, analyst (поддержка run_multi)
tests/
catalogs/
  aggregate-catalog.yaml   # каталог семантических агрегатов
  category-index.yaml      # индекс категорий для маршрутизации
  bootstrap/               # dev-only bootstrap данные (не копируются в образ)
scripts/
  bootstrap/               # dev-time утилиты (не копируются в образ)
sql/                       # SQL-скрипты (не копируются в образ)
```

## Commands

uv run pytest -q && uv run ruff check src/ tests/

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 011-fix-keyword-fallback-chart: Added Python 3.11+ + python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8
- 010-test-coverage: Added Python 3.11+ + python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8, selenium ≥4.22, python-dotenv ≥1.0.1

- 001-semantic-aggregate-layer (Phase 10 Polish):
  - Added services: `aggregate_registry`, `master_resolver`, `query_logger`
  - Agent capabilities: `planner.run_multi`, `sql.run_multi`, `analyst.run_multi` (multi-query и comparison chart)
  - Каталоги `catalogs/aggregate-catalog.yaml` и `catalogs/category-index.yaml`
  - CI workflow `.github/workflows/validate-catalogs.yml` валидирует каталоги на push/PR
  - Dockerfile копирует `catalogs/*.yaml`; bootstrap/scripts/sql исключены из образа

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
