# Tasks: Fix comparison chart и текстовое описание

**Input**: plan.md, spec.md
**Issues**: #5, #6, #7

## Phase 1: Data layer

- [ ] T001 Добавить `group_by: str = ""` в `AggregateResult` dataclass (`models.py`)
- [ ] T002 В `sql_agent.run_multi()` копировать `query.params.get("group_by", "")` в `AggregateResult.group_by`

## Phase 2: Chart

- [ ] T003 Добавить `_GROUP_BY_LABEL_COL` маппинг и `group_by` kwarg в `render_comparison()`, реализовать per-row grouped bars (`chart_renderer.py`)
- [ ] T004 Обновить orchestrator: передать `group_by` из `AggregateResult` в `render_comparison()` (`orchestrator.py`)

## Phase 3: Analyst — comparison текст

- [ ] T005 Добавить `_METRIC_LABELS` dict, переписать `_fallback_multi()` с дельтами и русскими названиями (`analyst.py`)

## Phase 4: Analyst — fallback_summary

- [ ] T006 Добавить `_FIELD_LABELS`, `_HIDDEN_FIELDS`, topic-specific форматтеры (`_format_outflow_summary`, `_format_statistics_summary`), обновить `_fallback_summary()` (`analyst.py`)

## Phase 5: Tests

- [ ] T007 Тесты render_comparison (group_by=status per-row, group_by=total legacy, пустые данные) + тесты analyst fallback (дельты, перевод полей, topic formatters)
