# Implementation Plan: Исправление маршрутизации и chart rendering

**Branch**: `feature/011-fix-keyword-fallback-chart` | **Date**: 2026-04-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-fix-keyword-fallback-chart/spec.md`
**Updated**: 2026-04-16 (post-critique: E1-E4, P1, P2)

## Summary

Системное исправление 4 production-багов (#13-#16):
1. **Keyword fallback** — улучшить `detect_topic()` scoring с контекстными правилами (FR-001). `run()` уже LLM-first (planner.py:458), но при `OLLAMA_API_KEY=""` → всегда keyword fallback.
2. **Field labels** — дополнить `_FIELD_LABELS` / `_HIDDEN_FIELDS` для всех SP-полей (FR-004-FR-006).
3. **Chart rendering** — исправить `_PREFERRED_VALUE`, исключить boolean из value axis (FR-007-FR-008).
4. **Period parsing** — расширить `has_period_hint()` для месяцев без «за» (FR-009-FR-010).

**Ключевое уточнение (critique E1)**: `PlannerAgent.run()` **уже** использует LLM-first routing через `_llm_plan()` → `plan_query()`. Не нужно добавлять новый LLM-путь — нужно улучшить keyword fallback и обеспечить диагностику.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8  
**Storage**: Microsoft SQL Server (pyodbc, ODBC Driver 17)  
**Testing**: pytest + pytest-asyncio, ruff (линтинг). LLM-зависимые тесты мокируются через `AsyncMock` на `LLMClient.plan_query()` (существующий паттерн в test_real_llm.py).  
**Target Platform**: Linux server (Docker → GHCR)  
**Project Type**: Telegram-бот (multi-agent аналитическая система)  
**Performance Goals**: LLM routing ≤3 сек (пользователь видит «typing...» в Telegram)  
**Constraints**: Graceful degradation при недоступности LLM; backward-compatible с legacy `run()` consumers  
**Scale/Scope**: ~300 LOC изменений, 4 файла production-кода + тесты

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Принцип | Статус | Комментарий |
|---|---------|--------|-------------|
| I | Spec-Driven Development | ✅ PASS | Спецификация spec.md утверждена, 4 User Stories, 12 FR |
| II | Agent-Only Code | ✅ PASS | Код пишется через SDD-пайплайн |
| III | Test-First | ✅ PASS | Каждый US имеет acceptance scenarios; тесты для keyword fallback, field labels, chart, period parsing |
| IV | Multi-Agent Review Gate | ✅ PASS | Полный цикл ревью запланирован после implement |
| V | Adversarial Review Gate | ✅ PASS | DeepSeek + Codex после speckit-ревью |
| VI | Adversarial Diversity | ✅ PASS | Claude пишет, DeepSeek + Codex ревьюят |
| VII | MAQA | ℹ️ N/A | <3 независимых задач — MAQA не требуется (4 файла тесно связаны) |
| VIII | Документация | ✅ PASS | CLAUDE.md обновится при изменении структуры |
| IX | Типизация и качество | ✅ PASS | Type hints для публичных API, ruff, whitelist-валидация процедур |
| X | Секреты | ✅ PASS | Нет новых секретов; LLM уже подключен через существующий LLMClient |

**Результат**: Все гейты пройдены. Принцип VII (MAQA) не применим — задачи связаны (общий topic/field mapping контекст).

## Project Structure

### Documentation (this feature)

```text
specs/011-fix-keyword-fallback-chart/
├── plan.md              # Этот файл
├── research.md          # Phase 0: исследование подхода
├── data-model.md        # Phase 1: модели данных
├── quickstart.md        # Phase 1: быстрый старт
├── contracts/           # Phase 1: контракты интерфейсов
│   └── routing-contract.md
└── tasks.md             # Phase 2: задачи (создаётся /speckit.tasks)
```

### Source Code (repository root)

```text
src/swarm_powerbi_bot/
├── agents/
│   ├── planner.py          # [READ-ONLY] run() уже LLM-first; не модифицируем routing
│   └── analyst.py          # [MODIFY] _FIELD_LABELS, _HIDDEN_FIELDS, fallback summary
├── services/
│   ├── chart_renderer.py   # [MODIFY] _PREFERRED_VALUE, boolean exclusion в _pick_label_value
│   ├── sql_client.py       # [MODIFY] has_period_hint() — _RE_MONTH_BARE без «за»
│   ├── topic_registry.py   # [MODIFY] улучшить detect_topic() — контекстные правила scoring
│   └── llm_client.py       # [MODIFY] circuit breaker для plan_query() (FR-012)
├── models.py               # [READ-ONLY] Plan, MultiPlan, QueryParams

tests/
├── test_keyword_fallback.py    # [CREATE] тесты улучшенного keyword scoring
├── test_field_labels.py        # [CREATE] тесты field labels / hidden fields
├── test_chart_preferred.py     # [CREATE] тесты chart value axis selection
├── test_period_hint.py         # [CREATE] тесты has_period_hint() расширения
└── integration/
    ├── test_real_llm.py        # [MODIFY] расширение 10-вопросов теста
    └── test_real_e2e.py        # [MODIFY] проверка raw fields
```

**Structure Decision**: Существующая структура `src/swarm_powerbi_bot/` сохраняется. Модификация 4 файлов production-кода, создание 4 unit-тест файлов.

## Architecture: Routing Paths

### Текущее состояние (обе ветки уже существуют)

```
PlannerAgent.run()
  │
  ├─► _llm_plan() → LLMClient.plan_query()     [PRIMARY — если OLLAMA_API_KEY задан]
  │     │
  │     ├─ LLM → JSON → QueryParams → _derive_topic() → topic
  │     └─ None (ошибка/timeout/no key)
  │           │
  └─► detect_topic() → keyword scoring           [FALLBACK — если LLM вернул None]
        │
        └─ sum(keywords) → topic_id
```

### Что исправляем

1. **`detect_topic()`** (topic_registry.py) — улучшить scoring:
   - Добавить контекстные правила: «выручка за неделю» → период + «выручк» → statistics (не services)
   - Добавить весовые коэффициенты: «кто больше принёс денег» → masters (не services)
   - Сохранить обратную совместимость: прямые запросы «популярные услуги» → services

2. **`_fallback_summary()`** (analyst.py) — скрывать unknown поля:
   - `_FIELD_LABELS.get(key, key)` → если нет маппинга, пропустить (не показывать raw)

3. **`_pick_label_value()`** (chart_renderer.py) — исключить boolean:
   - `isinstance(val, bool)` → skip
   - `_PREFERRED_VALUE` — исправить маппинги

4. **`has_period_hint()`** (sql_client.py) — расширить regex:
   - `_RE_MONTH_BARE` — месяцы без «за» с word boundaries

5. **`plan_query()`** (llm_client.py) — добавить circuit breaker:
   - Аналогично `plan_aggregates()` — защита от каскадных timeout

### Не модифицируем

- **`PlannerAgent.run()`** — routing logic уже корректен (LLM-first → keyword fallback)
- **`_PLANNER_SYSTEM_PROMPT`** — уже различает statistics/services/masters
- **`PlannerAgent.run_multi()`** — уже LLM-first через aggregate_registry

## Complexity Tracking

> Нет нарушений конституции — таблица не заполняется.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
