# Спецификация: Orchestrator fallback при ошибке multi_results (#4)

**Ветка**: `feature/004-orchestrator-fallback-fix` | **Дата**: 2026-04-15

## Проблема

Когда multi_plan создал запросы (comparison/decomposition), но все multi_results failed — orchestrator запускает legacy `_run_sql()` с `plan.topic` = catalog aggregate_id (например `clients_outflow`). Legacy SQL не знает catalog ids → дефолтит на `statistics` → показывает выручку вместо ошибки.

## Решение

Если multi_plan.queries были и multi_results все failed — НЕ запускать legacy SQL. Вместо этого:
- `sql_insight` = пустой (rows=[])
- Analyst получит пустые данные → покажет сообщение «Данных не найдено»

## Scope

Файл: `src/swarm_powerbi_bot/orchestrator.py` (строки ~139-147)

## Acceptance Criteria

- [ ] Когда все multi_results failed, legacy SQL НЕ запускается
- [ ] Пользователь видит сообщение об ошибке, а не неверные данные
- [ ] Когда multi_plan=None (legacy flow), legacy SQL работает как раньше
- [ ] Тесты покрывают сценарий
