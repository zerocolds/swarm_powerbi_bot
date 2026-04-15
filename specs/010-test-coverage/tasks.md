# Задачи: Расширение тестового покрытия (#10)

## Фаза 1: Инфраструктура

- [x] **T001**: Зарегистрировать marker `e2e` в `pyproject.toml` (не исключать из default run)
  - Файл: `pyproject.toml`

- [x] **T002**: Создать `tests/conftest.py` — вынести shared DummyClasses из `test_orchestrator.py`, добавить MockRegistry, MockPlannerWithRegistry, MockSQLMulti, MockAnalystMulti, fixture `mock_orchestrator_multi`
  - Файлы: `tests/conftest.py`, `tests/test_orchestrator.py` (импорт из conftest)

## Фаза 2: E2E mock — расширение MOCK_DATA и pipeline

- [x] **T003**: Расширить `MockSQL.MOCK_DATA` в `test_e2e_pipeline.py` до 10 тем (добавить referrals, birthday, communications, forecast, services, quality)
  - Файл: `tests/test_e2e_pipeline.py`

- [x] **T004**: E2E mock: comparison pipeline через MultiPlan — `test_comparison_pipeline` (chart PNG + delta text), `test_composition_pipeline` (decomposition, multi_results)
  - Файл: `tests/test_e2e_pipeline.py`

- [x] **T005**: E2E mock: parametrized `test_10_checklist_questions` — 10 вопросов из test-checklist.md, каждый → non-empty SwarmResponse
  - Файл: `tests/test_e2e_pipeline.py`

- [x] **T006**: E2E mock: follow-up chains — `test_follow_up_chain` (topic preserved), `test_follow_up_to_comparison`
  - Файл: `tests/test_e2e_pipeline.py`

## Фаза 3: E2E mock — negative scenarios

- [x] **T007**: Negative: `test_negative_sql_injection`, `test_negative_off_topic`, `test_negative_empty_period`, `test_negative_long_text`
  - Файл: `tests/test_e2e_pipeline.py`

## Фаза 4: Smoke — fallback quality

- [x] **T008**: Smoke: `test_outflow_fallback_no_raw_fields`, `test_statistics_fallback_russian_labels`, `test_statistics_has_period`
  - Файл: `tests/test_e2e_pipeline.py`

## Фаза 5: Integration — новые фичи

- [x] **T009**: Integration: `test_e2e_comparison_has_chart`, `test_e2e_fallback_no_raw_fields`, `test_e2e_fallback_has_period`, `test_e2e_statistics_money_rounded` — structural assertions only
  - Файл: `tests/integration/test_real_e2e.py`

- [x] **T010**: Integration: parametrized `test_planner_10_questions` — 10 вопросов → valid MultiPlan
  - Файл: `tests/integration/test_real_llm.py`
