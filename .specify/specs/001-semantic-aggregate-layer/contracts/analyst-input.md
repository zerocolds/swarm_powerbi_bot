# Contract: AnalystAgent Input/Output

## Input

```
question: str                        — оригинальный вопрос пользователя
plan: MultiPlan                      — plan.intent определяет стиль ответа
results: list[AggregateResult]       — от SQLAgent (0..10 результатов)
model_insight: ModelInsight | None   — от PowerBIModelAgent (опционально)
```

## Output

`AnalysisResult`:
```
answer: str              — текстовый ответ на русском (max 4 предложения для single, max 6 для comparison/decomposition)
confidence: str          — "high" | "medium" | "low"
follow_ups: list[str]    — 2-3 подсказки следующих вопросов
diagnostics: dict        — debug info
```

## Behavior by intent

### single
- Стандартный ответ: описание данных, конкретные числа
- Существующая логика AnalystAgent

### comparison
- Формат: "Метрика A за период 1: X. За период 2: Y. Изменение: +/-Z%"
- Если период неполный (текущий месяц) — явно отметить
- Delta для каждой ключевой метрики

### decomposition
- Формат: "Выручка упала на X%. Основная причина: <фактор> (снижение на Y%)"
- Анализ нескольких метрик, выделение главного фактора
- Не более 3 факторов

### trend
- Формат: описание динамики ("растёт", "снижается", "стабильно")
- Конкретные числа начала и конца периода

### ranking
- Формат: "Топ-N по <метрике>: 1. X (Z руб.), 2. Y (W руб.)"

## Rules (из конституции + spec)

- Только описание данных SQL, без рекомендаций
- Числа относятся к конкретным клиентам/мастерам
- Без markdown-таблиц (Telegram не рендерит)
- Без слов "срочно", "VIP", "рекомендуем"
- LLM fallback: если LLM недоступен — структурированный текст из шаблона
