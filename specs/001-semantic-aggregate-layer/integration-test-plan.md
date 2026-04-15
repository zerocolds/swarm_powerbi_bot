# План интеграционного тестирования — Semantic Aggregate Layer

**Версия**: 1.0  
**Дата**: 2026-04-15  
**Статус**: DRAFT — ожидает утверждения  

---

## 1. Smoke Test Script (`scripts/smoke_test.py`)

### Назначение
Автоматическая проверка работоспособности всей цепочки в реальном окружении. Запускается перед деплоем или при настройке нового инстанса.

### Предусловия
- `.env` с MSSQL_* и OLLAMA_* переменными
- Сетевой доступ к MSSQL и Ollama
- `uv run python scripts/smoke_test.py`

### Шаги

#### Step 1: MSSQL Connectivity (timeout: 10s)
```
Подключиться к MSSQL через pyodbc с read-only credentials.
Ожидание: соединение установлено, cursor.execute("SELECT 1") → 1.
```

#### Step 2: Процедуры существуют (timeout: 15s)
```
Для каждой из 3 процедур (spKDO_Aggregate, spKDO_ClientList, spKDO_CommAgg):
  SELECT OBJECT_ID('dbo.<procedure>') — должен вернуть не NULL.
Ожидание: все 3 процедуры найдены.
```

#### Step 3: Каталог агрегатов валиден (timeout: 5s)
```
Загрузить catalogs/aggregate-catalog.yaml.
Проверить: 27 агрегатов, каждый ссылается на одну из 3 процедур.
Ожидание: 27/27 validated.
```

#### Step 4: Вызов каждого агрегата с тестовым ObjectId (timeout: 60s total)
```
Для каждого из 27 агрегатов:
  Вызвать execute_aggregate(aggregate_id, params={
    object_id: 506770,
    date_from: "2026-03-01",
    date_to: "2026-03-31",
    ...default params из каталога
  })
  Ожидание: status != "error", rows >= 0 (пустые допустимы для некоторых агрегатов).
  Timeout per aggregate: 5s.

Фиксируем: aggregate_id, status, row_count, duration_ms.
```

**Исключения** (допустимо 0 строк):
- `clients_birthday` — зависит от дат именинников в периоде
- `clients_forecast` — зависит от прогнозных данных
- `comm_waitlist_by_manager` — может не быть записей

#### Step 5: Ollama LLM доступен (timeout: 15s)
```
POST http://<OLLAMA_BASE_URL>/api/chat с моделью из OLLAMA_MODEL.
Prompt: "Ответь одним словом: тест."
Ожидание: HTTP 200, непустой response.
```

#### Step 6: LLM-планирование работает (timeout: 20s)
```
Вызвать PlannerAgent.run_multi(UserQuestion(
  text="Какой отток за месяц?",
  object_id=506770,
  user_id="smoke-test"
))
Ожидание: MultiPlan с intent != "", queries >= 1.
```

#### Step 7: Полный E2E цикл (timeout: 30s)
```
SwarmOrchestrator.handle_question(UserQuestion(
  text="Покажи выручку за март",
  object_id=506770,
  user_id="smoke-test"
))
Ожидание:
  - response.answer непустой, на русском
  - response.topic != "unknown"
  - response.confidence in ("low", "medium", "high")
```

### Формат отчёта (stdout JSON)
```json
{
  "timestamp": "2026-04-15T12:00:00Z",
  "overall": "PASS|FAIL",
  "steps": [
    {
      "name": "mssql_connectivity",
      "status": "PASS|FAIL|SKIP",
      "duration_ms": 150,
      "detail": "..."
    },
    ...
  ],
  "aggregates": [
    {
      "aggregate_id": "revenue_total",
      "status": "ok|error",
      "row_count": 12,
      "duration_ms": 340
    },
    ...
  ],
  "summary": {
    "total_steps": 7,
    "passed": 7,
    "failed": 0,
    "aggregates_ok": 27,
    "aggregates_error": 0
  }
}
```

### Exit codes
- 0: всё PASS
- 1: хотя бы один FAIL
- 2: ошибка конфигурации (нет .env, нет pyodbc)

---

## 2. Integration Tests (`tests/integration/`)

### Структура
```
tests/
  integration/
    conftest.py          # fixtures, skip logic, markers
    test_real_sql.py     # SQL через реальный MSSQL
    test_real_llm.py     # LLM через реальный Ollama
    test_real_e2e.py     # Полный цикл (mock только Telegram)
```

### conftest.py

```python
# Маркер: @pytest.mark.integration
# Регистрация: pytest.ini или pyproject.toml → markers = ["integration: ..."]
# Skip logic:
#   - test_real_sql: skip если MSSQL_SERVER не задан или pyodbc connect fails
#   - test_real_llm: skip если OLLAMA_BASE_URL не задан или /api/tags fails
#   - test_real_e2e: skip если любое из выше
#
# Fixtures:
#   - real_settings: Settings() из .env
#   - real_sql_client: SQLClient(real_settings)
#   - real_llm_client: LLMClient(real_settings)
#   - real_registry: AggregateRegistry с загруженным каталогом
#   - real_orchestrator: полный SwarmOrchestrator с реальными агентами
#   - test_object_id: 506770 (hardcoded test salon)
```

**Запуск**: `uv run pytest tests/integration/ -m integration -v`  
**CI**: НЕ запускается автоматически (нет доступа к MSSQL/Ollama). Только локально или в staging.

### test_real_sql.py

| # | Тест | Что проверяет | Ожидание |
|---|------|---------------|----------|
| 1 | `test_connection` | pyodbc.connect + SELECT 1 | Соединение успешно |
| 2 | `test_procedures_exist` | OBJECT_ID для 3 процедур | Все 3 не NULL |
| 3 | `test_aggregate_revenue_total` | execute_aggregate("revenue_total", {object_id: 506770, date_from/to}) | rows > 0, колонки содержат Revenue |
| 4 | `test_aggregate_clients_outflow` | execute_aggregate("clients_outflow", ...) | rows >= 0, status="ok" |
| 5 | `test_aggregate_comm_all` | execute_aggregate("comm_all_by_reason", ...) | rows >= 0, status="ok" |
| 6 | `test_all_aggregates_no_error` | Цикл по 27 агрегатам | 0 errors (пустые rows допустимы) |
| 7 | `test_invalid_object_id` | execute_aggregate с object_id=999999999 | rows=0, status="ok" (не error) |
| 8 | `test_query_timeout` | Запрос с date range 10 лет | Завершается в пределах sql_query_timeout |
| 9 | `test_whitelist_rejects_injection` | Прямой вызов с procedure="DROP TABLE" | Отклонён до SQL |
| 10 | `test_concurrent_aggregates` | 5 параллельных запросов через asyncio | Все завершаются, semaphore работает |

### test_real_llm.py

| # | Тест | Что проверяет | Ожидание |
|---|------|---------------|----------|
| 1 | `test_ollama_health` | GET /api/tags | HTTP 200, модель в списке |
| 2 | `test_simple_completion` | POST /api/chat "скажи привет" | Непустой ответ |
| 3 | `test_planner_keyword_fallback` | PlannerAgent.run(question без LLM) | Plan с topic, keyword mode |
| 4 | `test_planner_llm_mode` | PlannerAgent.run_multi("выручка за март") | MultiPlan с queries |
| 5 | `test_planner_comparison` | run_multi("сравни выручку март и апрель") | intent="comparison", 2 queries |
| 6 | `test_planner_decomposition` | run_multi("почему упала выручка?") | intent="decomposition", 2+ queries |
| 7 | `test_planner_unknown_topic` | run_multi("рецепт борща") | Graceful: fallback или пустой план |
| 8 | `test_analyst_summary` | AnalystAgent.run() с реальными данными | Ответ на русском, ≤2000 chars |
| 9 | `test_circuit_breaker` | 4 timeout-а подряд → breaker open | Следующий вызов отклонён без LLM |
| 10 | `test_llm_timeout` | Запрос с timeout=0.001s | TimeoutError, не зависание |

### test_real_e2e.py

| # | Тест | Что проверяет | Ожидание |
|---|------|---------------|----------|
| 1 | `test_e2e_revenue_question` | "Покажи выручку за март" → handle_question | answer непустой, topic in (revenue_total, revenue_by_*) |
| 2 | `test_e2e_outflow_question` | "Какой отток за месяц?" | answer содержит числа, topic=clients_outflow |
| 3 | `test_e2e_comparison` | "Сравни выручку марта и февраля" | image не None (comparison chart), mime_type="image/png" |
| 4 | `test_e2e_top_masters` | "Топ-5 мастеров по выручке" | answer содержит имена или числа |
| 5 | `test_e2e_decomposition` | "Почему упала выручка?" | answer содержит "причин" или "фактор" |
| 6 | `test_e2e_unknown_question` | "Как сварить борщ?" | topic="unknown", answer содержит "не могу" |
| 7 | `test_e2e_follow_up` | 2 вопроса подряд: "выручка за март" → "а за февраль?" | Второй использует last_topic |
| 8 | `test_e2e_chart_generation` | "Покажи график выручки по неделям" | image не None, topic=revenue_by_week |
| 9 | `test_e2e_telegram_mock` | TelegramBot._process_question через mock Update | reply_text вызван с непустым текстом |
| 10 | `test_e2e_concurrent_users` | 3 параллельных handle_question с разными user_id | Все завершились, нет cross-contamination |

---

## 3. Manual Test Checklist (`docs/test-checklist.md`)

### Тестовые вопросы (10 штук)

| # | Вопрос | Тип | Ожидаемые агрегаты | Ожидаемый результат |
|---|--------|-----|---------------------|---------------------|
| 1 | «Покажи выручку за март» | Single query | revenue_total | Число с ₽, topic=revenue |
| 2 | «Какой отток клиентов за последний месяц?» | Single query | clients_outflow | Количество клиентов, список |
| 3 | «Сравни выручку марта и февраля» | Comparison | revenue_total ×2 | Grouped bar chart, текст "выросла/упала на X%" |
| 4 | «Топ-5 мастеров по выручке за март» | Single + top | revenue_by_master | Таблица 5 строк с именами и суммами |
| 5 | «Почему упала выручка в марте?» | Decomposition | revenue_total + revenue_by_service + revenue_by_master | Факторный анализ: "основная причина: ..." |
| 6 | «Сколько записей на будущие дни?» | Single query | clients_forecast | Количество записей, дата диапазон |
| 7 | «Покажи график выручки по неделям за квартал» | Chart | revenue_by_week | PNG bar chart, подписи недель |
| 8 | «Какие клиенты скоро уходят?» | Single query | clients_leaving | Список имён/количество |
| 9 | «Статистика звонков по причинам за март» | Single query | comm_all_by_reason | Разбивка по reason: outflow, leaving, ... |
| 10 | «Именинники на этой неделе» | Single query | clients_birthday | Список или "нет именинников" |

### Чеклист для каждого вопроса

```
□ Бот ответил (не зависание, не ошибка)
□ Время ответа < 15 секунд
□ Данные корректны (числа совпадают с Power BI ±5%)
□ График правильный (если есть): оси подписаны, данные видны
□ Текст осмысленный: на русском, содержит конкретные числа
□ Topic определён верно (проверить в diagnostics)
□ Нет SQL-ошибок в логах
□ Follow-up вопрос работает ("а за февраль?")
```

### Негативные сценарии

| # | Действие | Ожидание |
|---|----------|----------|
| N1 | Отправить текст не по теме: "привет" | Вежливый отказ или общий ответ |
| N2 | Отправить очень длинный текст (>1000 символов) | Обработка без ошибки |
| N3 | Отправить SQL injection: `'; DROP TABLE --` | Отклонено, whitelist guard |
| N4 | Спросить про салон другого пользователя | ObjectId из подписки, не из текста |
| N5 | Отключить Ollama, задать вопрос | Keyword fallback, ответ без LLM |

---

## 4. Docker Compose для тестирования (`docker-compose.test.yml`)

### Архитектура
```
┌─────────────────────────────────────────────┐
│            docker-compose.test.yml           │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │   bot    │  │ selenium │  │  ollama   │  │
│  │ (Python) │  │ (Chrome) │  │ (DeepSeek)│  │
│  └────┬─────┘  └──────────┘  └─────┬─────┘  │
│       │                            │         │
└───────┼────────────────────────────┼─────────┘
        │                            │
        ▼                            │
  ┌──────────┐                       │
  │  MSSQL   │ (внешний, через .env) │
  │ (prod/   │                       │
  │  staging)│                       │
  └──────────┘                       │
                                     │
              ollama pull deepseek-v3.2:cloud
```

### Сервисы

| Сервис | Образ | Назначение | Порты |
|--------|-------|------------|-------|
| bot | build: . | Telegram бот + smoke test | — |
| selenium | selenium/standalone-chrome:124.0 | Power BI скриншоты | 4444 |
| ollama | ollama/ollama:latest | LLM inference | 11434 |

### Переменные окружения
- MSSQL_*: из `.env` (bind mount или env_file)
- OLLAMA_BASE_URL: `http://ollama:11434`
- SELENIUM_HUB_URL: `http://selenium:4444/wd/hub`
- TG_TOKEN: test token или пустой для smoke test

### Команды
```bash
# Запуск полного стека
docker compose -f docker-compose.test.yml up -d

# Smoke test (без Telegram)
docker compose -f docker-compose.test.yml exec bot python scripts/smoke_test.py

# Integration tests
docker compose -f docker-compose.test.yml exec bot pytest tests/integration/ -m integration -v

# Остановка
docker compose -f docker-compose.test.yml down
```

### Volumes
- `ollama_data`: для кэширования моделей между запусками

### Health checks
- **ollama**: `curl -f http://localhost:11434/api/tags`
- **selenium**: `curl -f http://localhost:4444/wd/hub/status`
- **bot**: depends_on: ollama (healthy), selenium (healthy)

---

## 5. Конфигурация pytest

### Новые маркеры (pyproject.toml)
```toml
[tool.pytest.ini_options]
markers = [
    "integration: тесты с реальным MSSQL/Ollama (deselect by default)",
]
addopts = "-m 'not integration'"
```

### conftest.py (tests/integration/)
```
Fixtures:
  real_settings   — Settings() из os.environ
  real_sql_client — SQLClient(real_settings), skip если connect fails
  real_llm_client — LLMClient(real_settings), skip если /api/tags fails
  real_registry   — load_catalog + AggregateRegistry
  real_orchestrator — SwarmOrchestrator с реальными агентами
  test_object_id  — 506770
  test_date_range — ("2026-03-01", "2026-03-31")
```

---

## 6. Порядок реализации

| # | Что | Зависимости | Приоритет |
|---|-----|-------------|-----------|
| 1 | `tests/integration/conftest.py` | — | P0 |
| 2 | `scripts/smoke_test.py` | conftest fixtures можно переиспользовать | P0 |
| 3 | `tests/integration/test_real_sql.py` | conftest | P1 |
| 4 | `tests/integration/test_real_llm.py` | conftest | P1 |
| 5 | `tests/integration/test_real_e2e.py` | test_real_sql + test_real_llm | P1 |
| 6 | `docker-compose.test.yml` | — | P2 |
| 7 | `docs/test-checklist.md` | — | P2 |
| 8 | pyproject.toml markers | — | P0 |

**Оценка**: ~15 файлов, ~1500 строк. Все тесты skip-safe: без MSSQL/Ollama они автоматически пропускаются.

---

## 7. Критерии приёмки

- [ ] `scripts/smoke_test.py` возвращает JSON с overall="PASS" на staging
- [ ] `pytest tests/integration/ -m integration` — все тесты PASS на staging
- [ ] `pytest -q` (без integration) — 351+ тестов по-прежнему PASS
- [ ] `docker compose -f docker-compose.test.yml up` — стек запускается
- [ ] Manual checklist: 10/10 вопросов дают осмысленные ответы
- [ ] Негативные сценарии: 5/5 корректно обработаны
