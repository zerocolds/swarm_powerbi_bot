# Tasks: Fix comparison follow-up intent

**Input**: plan.md, spec.md
**Issue**: #2

## Phase 1: Fix

- [ ] T001 Расширить `LLMClient.plan_aggregates()` — добавить параметр `last_topic: str`, включить в system prompt и user message
- [ ] T002 Обновить `PlannerAgent._llm_plan_multi()` — передавать `question.last_topic` в `plan_aggregates()`
- [ ] T003 Обновить `PlannerAgent._fallback_multi_plan()` — определять intent=comparison по ключевым словам, генерировать 2 AggregateQuery с разными периодами, для clients_* использовать group_by=status

## Phase 2: Tests

- [ ] T004 Написать тесты в `tests/test_planner_v2.py`: follow-up comparison (LLM mock), fallback comparison, comparison без контекста
