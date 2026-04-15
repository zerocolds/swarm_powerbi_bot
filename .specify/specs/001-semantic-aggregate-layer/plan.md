# Implementation Plan: Semantic Aggregate Layer

**Branch**: `feature/001-semantic-aggregate-layer` | **Date**: 2026-04-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-semantic-aggregate-layer/spec.md`

## Summary

Переход от жёстко привязанных 17 stored procedures (keyword-matching через topic_registry) к семантическому слою агрегатов: LLM выбирает агрегаты из каталога в двухшаговом planning (категория → детали), SQLAgent выполняет до 10 параллельных запросов к предрассчитанным (materialized) агрегатам, AnalystAgent синтезирует multi-result ответ.

4 фазы: Discovery (dev-time bootstrap: PBIX→YAML→SQL) → SQL layer (materialized агрегаты) → LLM planning (двухшаговый) → Сравнения/Композиция.

**Ключевой принцип**: PBIX нужен только для bootstrap (Phase 0) — чтобы ПОНЯТЬ семантику и ПЕРЕНЕСТИ её в SQL-агрегаты + YAML-каталоги. После этого PBIX боту не нужен. В runtime бот работает ТОЛЬКО с закоммиченными YAML-каталогами и SQL-агрегатами.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8, selenium ≥4.22, python-dotenv ≥1.0.1
**Storage**: Microsoft SQL Server (pyodbc, ODBC Driver 17); materialized агрегаты (indexed views) с overhead ≤3x хранения
**Testing**: pytest ≥8.0, pytest-asyncio ≥0.23; порог покрытия 60% (целевой 80%)
**Target Platform**: Linux (Docker, python:3.11-slim) + Selenium standalone-chrome:124.0
**Project Type**: Telegram-бот (polling) + multi-agent swarm orchestrator
**Performance Goals**: ≤15 сек на вопрос (до 10 параллельных запросов по 10 сек каждый); materialized агрегаты для снижения латентности
**Constraints**: read-only SQL user; LLM никогда не генерирует SQL; whitelist aggregate_id + typed parameters; max 10 queries/question
**Scale/Scope**: мало клиентов (салоны красоты), big-bang раскатка; 17 существующих тем + gap-агрегаты из PBIX

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Принцип | Статус | Обоснование |
|---|---|---|---|
| I | Spec-Driven Development | ✅ PASS | Спецификация spec.md создана и clarified (5 уточнений) |
| II | Agent-Only Code | ✅ PASS | Весь код будет написан через SDD-пайплайн |
| III | Test-First | ✅ PASS | Каждый US имеет acceptance scenarios → тесты; 77 существующих тестов сохраняются |
| IV | Multi-Agent Review Gate | ✅ PASS | Запланировано: review → staff-review → verify → verify-tasks |
| V | Adversarial Review Gate | ✅ PASS | Запланировано: Gemini ∥ Codex после speckit-ревью |
| VI | Adversarial Diversity | ✅ PASS | Claude пишет, Gemini+Codex ревьюят |
| VII | MAQA | ✅ PASS | Фичи с ≥3 задачами → MAQA coordinator |
| VIII | Документация = DoD | ✅ PASS | docs/ обновляется в каждой фазе |
| IX | Типизация + ruff | ✅ PASS | Type hints обязательны, ruff в pipeline |
| X | Секреты | ✅ PASS | .env исключён из коммита, read-only SQL user |

**Verdict**: ALL GATES PASS. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-semantic-aggregate-layer/
├── plan.md              # Этот файл
├── spec.md              # Спецификация (13 US, 20 FR, 5 clarifications)
├── research.md          # Phase 0: исследование PBIX, tooling, materialization
├── data-model.md        # Phase 1: модель данных (каталоги, агрегаты)
├── quickstart.md        # Phase 1: быстрый старт разработки
├── contracts/           # Phase 1: контракты между агентами
│   ├── planner-output.md
│   ├── sql-agent-input.md
│   └── analyst-input.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/swarm_powerbi_bot/
├── config.py                          # Расширяется: пути к каталогам
├── models.py                          # Расширяется: AggregateQuery, MultiPlan, ComparisonResult
├── orchestrator.py                    # Расширяется: multi-query flow
├── agents/
│   ├── base.py                        # Без изменений
│   ├── planner.py                     # ПЕРЕРАБОТКА: двухшаговый planning по каталогу
│   ├── analyst.py                     # Адаптация: multi-result synthesis
│   ├── sql.py                         # Расширение: batch parallel queries
│   ├── powerbi.py                     # Без изменений
│   └── render.py                      # Без изменений
├── services/
│   ├── llm_client.py                  # Новый system prompt: category index + aggregate details
│   ├── sql_client.py                  # Расширение: execute_aggregate(), fuzzy_match_master()
│   ├── topic_registry.py              # Без изменений (fallback)
│   ├── chart_renderer.py              # Расширение: grouped bar, multi-line comparison
│   ├── catalog_loader.py              # НОВЫЙ: загрузка и валидация YAML-каталогов
│   ├── aggregate_registry.py          # НОВЫЙ: whitelist, parameter validation, dispatch
│   ├── parameter_validator.py         # НОВЫЙ: typed validation (date, enum, int range)
│   ├── master_resolver.py             # НОВЫЙ: fuzzy-match по tbMasters (per-request)
│   ├── query_logger.py                # НОВЫЙ: structured logging агрегатных вызовов
│   ├── powerbi_model_client.py        # Без изменений
│   ├── powerbi_render_client.py       # Без изменений
│   ├── registration.py                # Без изменений
│   └── stt_client.py                  # Без изменений
├── telegram_bot.py                    # Без изменений
└── main.py                            # Расширение: инициализация каталогов

catalogs/                              # НОВАЯ директория (коммитится в репо)
├── semantic-catalog.yaml              # RUNTIME: бизнес-модель для LLM (загружается ботом)
├── aggregate-catalog.yaml             # RUNTIME: каталог агрегатов (загружается ботом)
└── category-index.yaml                # RUNTIME: компактный индекс категорий для шага 1

catalogs/bootstrap/                    # Dev-time артефакты Phase 0 (справочные, не runtime)
├── semantic-model.yaml                # Полная модель PBIX (для разработчика)
├── pbix-to-sql-mapping.yaml           # Маппинг PBIX→SQL (для разработчика)
└── gaps.md                            # Gap-анализ (для планирования)

scripts/bootstrap/                     # Dev-time утилиты Phase 0 (НЕ runtime-зависимость)
├── extract_pbix.py                    # zipfile+json → semantic-model.yaml
├── map_pbix_to_sql.py                 # Маппинг PBIX→SQL
├── generate_semantic_catalog.py       # Генерация semantic-catalog.yaml
├── gap_analysis.py                    # Gap-анализ
└── validate_aggregates.py             # Верификация SQL vs DAX (≤1% допуск)

sql/
├── create_kdo_procedures.sql          # Существующий (без изменений)
├── create_materialized_aggregates.sql # НОВЫЙ: indexed views для базовых агрегатов
└── create_gap_aggregates.sql          # НОВЫЙ: TVF для gap-агрегатов

tests/
├── [14 существующих тестов]           # Без изменений (backward compatibility)
├── test_catalog_loader.py             # НОВЫЙ: загрузка и валидация каталогов
├── test_aggregate_registry.py         # НОВЫЙ: whitelist, dispatch, параметры
├── test_parameter_validator.py        # НОВЫЙ: типизация, enum, ranges
├── test_master_resolver.py            # НОВЫЙ: fuzzy-match
├── test_planner_v2.py                 # НОВЫЙ: двухшаговый planning
├── test_multi_query.py                # НОВЫЙ: batch parallel queries, partial failure
├── test_comparison.py                 # НОВЫЙ: сравнение периодов и мастеров
├── test_composition.py                # НОВЫЙ: декомпозиция сложных вопросов
├── test_query_logger.py               # НОВЫЙ: structured logging
├── test_extract_pbix.py               # НОВЫЙ: PBIX extraction
└── test_security.py                   # НОВЫЙ: SQL injection, whitelist, read-only
```

**Structure Decision**: Расширение существующей плоской структуры `src/swarm_powerbi_bot/`. Новые модули добавляются в `services/`. Чёткое разделение на:
- `catalogs/` — **runtime** YAML-каталоги (коммитятся, загружаются ботом при старте)
- `catalogs/bootstrap/` — **dev-time** артефакты Phase 0 (справочные, не нужны боту)
- `scripts/bootstrap/` — **dev-time** утилиты для извлечения PBIX (не runtime-зависимость, не в Docker)
- `sql/` — SQL-скрипты (выполняются DBA, не ботом)

PBIX нужен только для bootstrap. В Docker-образ бота попадают только `catalogs/*.yaml` и `src/`.

## Complexity Tracking

Нарушений конституции нет. Таблица пуста.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
