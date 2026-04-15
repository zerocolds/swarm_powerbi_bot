# Задачи: Orchestrator fallback (#4)

- [ ] **T001**: Добавить ветку `multi_all_failed` в orchestrator — не запускать legacy SQL если все multi_results failed
  - Файл: `src/swarm_powerbi_bot/orchestrator.py`

- [ ] **T002**: Тест: legacy SQL не вызывается при multi_all_failed
  - Файл: `tests/test_orchestrator.py`
