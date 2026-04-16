# Implementation Plan: Расширение тестового покрытия (#10)

**Branch**: `feature/010-test-coverage` | **Date**: 2026-04-15 | **Spec**: [spec.md](spec.md)

## Summary

Добавление ~25 тестов в три слоя: integration (MSSQL+Ollama), E2E mock (оба pipeline пути), smoke (новые фичи). Без изменений в production code — только тесты и pytest config.

## Technical Context

- **Language/Version**: Python 3.11+
- **Test Framework**: pytest + pytest-asyncio, asyncio_mode=auto
- **Markers**: `integration` (existing, excluded from default), `e2e` (new, included in default)
- **Mock Strategy**: inline dicts + conftest fixtures для orchestrator с mock registry
- **Integration Timeout**: 50с per test (облачный Ollama)
- **Dependencies**: Existing — pyodbc, httpx, matplotlib. No new deps.

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven | OK | spec.md + plan.md + clarifications done |
| II. Agent-Only | OK | All code by AI agent |
| III. Test-First | OK | This IS the test feature |
| IX. Typing | OK | Tests — type hints not required |
| X. Secrets | OK | Tests use env vars, no hardcoded secrets |

## Phase 0: Research

No NEEDS CLARIFICATION. All decisions made in clarification session:
- E2E covers both legacy + MultiPlan paths
- Timeout 50s
- E2E in default run

## Phase 1: Design

**No data-model.md** — feature adds only tests, no new entities.
**No contracts/** — no new external interfaces.

## Phase 2: Implementation Plan

### 2.1 pytest config — register `e2e` marker

**File**: `pyproject.toml`

Add `e2e` marker to `[tool.pytest.ini_options].markers`. Do NOT add it to `addopts` exclusion.

### 2.2 Integration: comparison chart output

**File**: `tests/integration/test_real_e2e.py`

Add after existing test #5:
- `test_e2e_comparison_has_chart_and_delta` — comparison returns PNG + answer with "%"
- `test_e2e_comparison_no_raw_fields` — no ClientName/Phone in answer text
- `test_e2e_fallback_text_has_period` — statistics answer contains "Период:"
- `test_e2e_statistics_money_rounded` — no long decimals in answer

All use `real_orchestrator` fixture, marker `@pytest.mark.integration`, `@pytest.mark.timeout(50)`.

**Assertion strategy (integration)**: структурные проверки only — `resp.image is not None`, `resp.answer` non-empty, `resp.topic` set. НЕ проверять содержимое текста (LLM непредсказуем). Content assertions — только в E2E mock тестах.

### 2.3 Integration: LLM planning on 10 questions

**File**: `tests/integration/test_real_llm.py`

Add parametrized test:
- `test_planner_10_questions` — parametrize with 10 questions from test-checklist.md, assert valid MultiPlan (queries non-empty, intent set)

### 2.4 E2E mock: 10 checklist questions + comparison/composition

**File**: `tests/test_e2e_pipeline.py`

Add to existing file (it already has mock SQL/PBI/Analyst):
- Extend `MockSQL.MOCK_DATA` to cover all 10 checklist topics (add referrals, birthday, communications, forecast, services, quality + comparison data for two periods)
- Add `MockSQLMulti` that supports `run_multi()` returning AggregateResult list
- Add `MockAnalystMulti` with `run_multi()` support
- Add `MockPlannerWithRegistry` for MultiPlan flow

New tests:
- `test_comparison_pipeline` — comparison via MultiPlan, chart PNG + answer with delta
- `test_composition_pipeline` — decomposition via MultiPlan, multi_results to analyst
- `test_statistics_has_period` — fallback text includes "Период:"
- `test_statistics_money_rounded` — no long decimals
- `test_10_checklist_questions` — parametrize 10 questions, each returns non-empty SwarmResponse
- `test_follow_up_chain` — question → follow-up → topic preserved
- `test_follow_up_to_comparison` — question → "сравни" follow-up → comparison intent

### 2.5 E2E mock: negative scenarios

**File**: `tests/test_e2e_pipeline.py`

- `test_negative_sql_injection` — "'; DROP TABLE --" → graceful response
- `test_negative_off_topic` — "рецепт борща" → response without crash
- `test_negative_empty_period` — question with no date range → fallback works
- `test_negative_long_text` — >1000 char input → no crash

### 2.6 Smoke: update existing tests

**File**: `tests/test_e2e_pipeline.py`

Ensure existing `MockAnalyst.run()` accepts `has_chart` kwarg (already does). Add:
- `test_outflow_fallback_no_raw_fields` — analyst fallback text hides Phone/ClientName
- `test_statistics_fallback_russian_labels` — no raw SQL field names

### 2.7 conftest — shared fixtures (extract from test_orchestrator.py)

**File**: `tests/conftest.py` (create if needed)

Extract and reuse DummyClasses from `test_orchestrator.py` (DummyPlanner, DummySQL, DummyPBI, DummyRender, DummyAnalyst). Add:
- `MockRegistry` — minimal AggregateRegistry stub with `get_aggregate()` and `list_aggregates()`
- `MockPlannerWithRegistry` — supports `run_multi()` returning MultiPlan
- `MockSQLMulti` — supports `run_multi()` returning AggregateResult list
- `MockAnalystMulti` — supports `run_multi()`
- Fixture `mock_orchestrator_multi` — SwarmOrchestrator wired with MultiPlan mocks

## File Summary

| File | Action | Tests Added |
|------|--------|-------------|
| `pyproject.toml` | Edit — add `e2e` marker | 0 |
| `tests/integration/test_real_e2e.py` | Edit — add 4 tests | 4 |
| `tests/integration/test_real_llm.py` | Edit — add parametrized test | 1 (x10 params) |
| `tests/test_e2e_pipeline.py` | Edit — add mocks + 15 tests | ~15 |
| `tests/conftest.py` | Create — shared fixtures | 0 |

**Total**: ~20 new test functions, ≥385 total with parametrize.

## Risks

- **Parametrized LLM tests flaky** — облачный Ollama может отвечать непредсказуемо. Mitigation: assert только структуру (MultiPlan fields), не содержимое.
- **Mock orchestrator complexity** — MultiPlan flow требует mock registry + mock run_multi. Mitigation: reuse patterns from existing test_orchestrator.py DummyClasses.
