# Задачи: Улучшение fallback statistics (#9)

## Фаза 1: Словари

- [x] **T001**: Добавить `"TotalRevenue": "Выручка (₽)"` в `_METRIC_LABELS` и `_FIELD_LABELS`
  - Файл: `src/swarm_powerbi_bot/agents/analyst.py`

## Фаза 2: Форматирование

- [x] **T002**: `_format_statistics_summary()` — округление денежных полей до 2 знаков, добавить TotalRevenue в итерацию
  - Файл: `src/swarm_powerbi_bot/agents/analyst.py`

- [x] **T003**: `_fallback_summary()` — добавить строку «Период: DateFrom — DateTo» из sql_insight.params
  - Файл: `src/swarm_powerbi_bot/agents/analyst.py`

- [x] **T004**: Default ветка `_fallback_summary()` — float значения форматировать через `{val:,.2f}`
  - Файл: `src/swarm_powerbi_bot/agents/analyst.py`

## Фаза 3: Тесты

- [x] **T005**: Тесты: округление денег, период в тексте, TotalRevenue переведён
  - Файл: `tests/test_analyst_fallback.py`
