# Спецификация: Расширение тестового покрытия (#10)

**Ветка**: `feature/010-test-coverage`
**Дата**: 2026-04-15
**Статус**: Draft

## Текущее состояние

Существующие тесты (368 passed, 30 deselected integration):

| Категория | Файл(ы) | Кол-во | Что покрывает |
|-----------|---------|--------|---------------|
| Unit | test_planner.py, test_planner_v2.py, test_aggregate_registry.py, etc. | ~300 | Keyword detection, config, registry, period parsing |
| Chart | test_chart_renderer.py | ~15 | render_chart, render_comparison with group_by |
| Analyst fallback | test_analyst_fallback.py | 8 | Comparison deltas, field translation, statistics formatting |
| E2E (mock) | test_e2e_pipeline.py | 8 | Full pipeline with mock SQL/PBI/Analyst |
| Orchestrator | test_orchestrator.py | 2 | Happy path, multi_all_failed |
| Integration (real) | integration/test_real_sql.py | 10 | MSSQL: 26 aggregates, injection, concurrent |
| Integration (real) | integration/test_real_llm.py | 10 | Ollama: planner modes, comparison, decomposition |
| Integration (real) | integration/test_real_e2e.py | 10 | Full pipeline real MSSQL+Ollama |

### Гэпы

1. **Integration**: нет тестов на новые фичи — comparison chart output, fallback text quality, period display
2. **E2E (mock)**: нет comparison/composition pipeline, нет negative scenarios, нет follow-up chains
3. **Smoke**: нет автоматического smoke test — только ручной `docs/test-checklist.md`
4. **Marker `e2e`**: не зарегистрирован — только `integration`

## User Stories

### US-1: Integration тесты новых фич (P1)

Разработчик запускает `pytest tests/integration/ -m integration` и видит что comparison chart, fallback text, period отображаются корректно на реальных данных.

**Acceptance Scenarios**:

1. **Given** MSSQL + Ollama доступны, **When** запрос "сравни выручку марта и февраля", **Then** response содержит image (PNG) и текст с дельтой %
2. **Given** MSSQL доступен, **When** запрос "отток за месяц", **Then** fallback текст содержит "Найдено клиентов:", "Просрочка", без raw field names (ClientName, Phone)
3. **Given** MSSQL доступен, **When** запрос "статистика за неделю", **Then** текст содержит "Период:", денежные поля округлены до 2 знаков

### US-2: E2E тесты с mock Telegram (P1)

Разработчик запускает `pytest -m e2e` с mock SQL (без MSSQL/Ollama) и видит что 10 типовых вопросов из checklist проходят pipeline, включая comparison, composition, follow-up chains, negative scenarios.

**Acceptance Scenarios**:

1. **Given** mock SQL с реалистичными данными, **When** 10 вопросов из test-checklist.md, **Then** каждый возвращает непустой SwarmResponse
2. **Given** mock SQL, **When** "сравни выручку марта и февраля" через orchestrator, **Then** response.image != None, response.answer содержит "%" (delta)
3. **Given** mock SQL, **When** цепочка follow-up (вопрос → "а за февраль?" → "сравни"), **Then** topic сохраняется, ответы непустые
4. **Given** mock SQL, **When** SQL injection "'; DROP TABLE --", **Then** нет ошибки, ответ graceful
5. **Given** mock SQL, **When** вопрос не по теме "рецепт борща", **Then** ответ есть, не crash

### US-3: Smoke тест — быстрая проверка новых фич (P2)

Обновить существующий `test_e2e_pipeline.py` — добавить проверку comparison, composition, fallback text quality.

**Acceptance Scenarios**:

1. **Given** mock orchestrator, **When** comparison question, **Then** chart + text с дельтами
2. **Given** mock orchestrator, **When** statistics question, **Then** текст содержит "Период:" и округлённые числа
3. **Given** mock orchestrator, **When** decomposition question, **Then** analyst получает multi_results

## Clarifications

### Session 2026-04-15

- Q: E2E mock тесты: нужно ли покрывать MultiPlan flow или только legacy? → A: Оба пути — legacy + MultiPlan с mock registry
- Q: Какой timeout для integration тестов (MSSQL + облачный Ollama)? → A: 50 секунд
- Q: E2E mock тесты в default pytest run или отдельный marker? → A: Default run (всегда в CI без явного -m e2e)

## Requirements

### Functional Requirements

- **FR-001**: Pytest marker `e2e` MUST быть зарегистрирован в `pyproject.toml`
- **FR-002**: Integration тесты MUST использовать marker `@pytest.mark.integration` и skip без среды
- **FR-003**: E2E тесты MUST работать без MSSQL/Ollama (mock). Marker `e2e` зарегистрирован но НЕ исключён из default run — запускаются всегда вместе с unit
- **FR-004**: Все новые тесты MUST проходить в CI (e2e + unit — всегда, integration — только со средой)
- **FR-005**: Comparison integration тест MUST проверять наличие PNG image и текста с дельтой
- **FR-006**: Fallback text тесты MUST проверять отсутствие raw SQL field names
- **FR-007**: E2E negative тесты MUST покрывать: SQL injection, вопрос не по теме, пустой период
- **FR-008**: E2E mock тесты MUST покрывать оба пути: legacy pipeline + MultiPlan с mock aggregate_registry
- **FR-009**: MockSQL.MOCK_DATA MUST покрывать все 10 тем из test-checklist.md (outflow, statistics, trend, masters, referrals, birthday, communications, forecast, services, quality)

### Файлы

- `tests/integration/test_real_e2e.py` — дополнить comparison/composition/fallback проверками
- `tests/test_e2e_pipeline.py` — дополнить comparison, composition, negative, follow-up chains
- `pyproject.toml` — зарегистрировать marker `e2e`

## Success Criteria

- **SC-001**: `pytest -m "not integration"` проходит с ≥385 тестов (сейчас 368)
- **SC-002**: `pytest tests/integration/ -m integration` — добавлено ≥5 новых тестов на comparison/fallback/period
- **SC-003**: E2E mock тесты покрывают 10 вопросов из test-checklist.md + 4 negative scenario
- **SC-004**: Нет raw field names в fallback текстах ни в одном тестовом сценарии
- **SC-005**: Integration тесты укладываются в timeout 50 секунд на запрос (облачный Ollama)

## Assumptions

- Integration тесты пропускаются без MSSQL/Ollama (существующий механизм conftest.py)
- E2E тесты работают полностью на моках — запускаются в любом CI
- Существующие тесты не модифицируются, только дополняются
- `docs/test-checklist.md` — справочный документ, автотесты дублируют его программно
