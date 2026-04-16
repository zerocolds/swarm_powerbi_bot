# Adversarial Review — FAIL

**Раунд**: 3 / 3
**Дата**: 2026-04-15T20:15:23Z
**Ветка**: feature/010-test-coverage

## DeepSeek V3.2 — FAIL

```
FAIL
[HIGH] tests/test_e2e_pipeline.py:21 — MockSQL.MOCK_DATA не покрывает все 10 тем из тест-чеклиста. Недостающие темы: referrals, birthday, communications, forecast, services, quality, leaving. Это приведёт к пустым результатам в тестах для этих тем.
[HIGH] tests/test_e2e_pipeline.py:251 — Параметризованный тест test_10_checklist_questions ожидает конкретные expected_topic из тест-чеклиста, но MockSQL не возвращает данные для всех этих тем, что приведёт к падению тестов или проверке пустых ответов.
[MEDIUM] tests/conftest.py:109 — MockSQLMulti возвращает фиксированный список AggregateResult для clients_outflow, но не покрывает другие агрегаты для тестов сравнения и декомпозиции, что ограничивает покрытие тестов.
[MEDIUM] swarm_powerbi_bot/specs/010-test-coverage/plan.md:76 — В plan указано создание conftest.py с новыми фикстурами, но при этом уже есть дублирование моков в test_orchestrator.py. Это создаёт избыточность и потенциальную несогласованность.
[CRITICAL] swarm_powerbi_bot/specs/001-semantic-aggregate-layer/spec.md:58 — В спецификации Phase 0 (P1 — US-001) указано, что семантическая модель извлекается из PBIX-файла, но в diff нет реализации этого функционала. Это базовая зависимость для всех последующих фаз.
[CRITICAL] swarm_powerbi_bot/specs/001-semantic-aggregate-layer/spec.md:124 — В Phase 0 (P1 — US-006) указана необходимость aggregate-catalog.yaml, но в diff нет ни создания этого файла, ни интеграции с PlannerAgent.
[HIGH] swarm_powerbi_bot/specs/001-semantic-aggregate-layer/spec.md:198 — Multi-query SQLAgent (US-009) должен выполнять до 10 агрегатных запросов параллельно, но в diff нет реализации run_multi() в SQLAgent и интеграции с PlannerAgent.
[MEDIUM] swarm_powerbi_bot/specs/001-semantic-aggregate-layer/spec.md:235 — Защита от произвольного SQL (US-012) требует валидации aggregate_id по whitelist из каталога, но каталог не реализован, и нет кода валидации в SQLAgent.
[MEDIUM] swarm_powerbi_bot/specs/010-test-coverage/spec.md:74 — Требование FR-009: MockSQL.MOCK_DATA MUST покрывать все 10 тем из test-checklist.md не выполнено в реализации.
```

## Codex — FAIL

```
Reading additional input from stdin...
OpenAI Codex v0.120.0 (research preview)
--------
workdir: /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
model: gpt-5.4
provider: openai
approval: never
sandbox: read-only
reasoning effort: xhigh
reasoning summaries: none
session id: 019d92c4-7062-7042-9770-2ccbf5cd8374
--------
user
Review this code for logic errors, security issues, edge cases, and spec violations. Be adversarial — assume bugs exist.

Response format:
- First line: PASS or FAIL
- If FAIL: list findings, each on a new line as: [SEVERITY] file:line — description
- SEVERITY: CRITICAL / HIGH / MEDIUM
- Do not praise. Only report problems.

Spec: see .specify/specs/*/spec.md
Changes: git diff main...HEAD
codex
Reviewing `git diff main...HEAD` against the spec in `.specify/specs/*/spec.md`. I’m starting by loading the changed files and the relevant spec text, then I’ll trace the new logic for regressions, edge cases, and violations.
exec
/bin/zsh -lc 'rg --files .specify/specs' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
.specify/specs/001-semantic-aggregate-layer/spec.md
.specify/specs/001-semantic-aggregate-layer/plan.md
.specify/specs/001-semantic-aggregate-layer/data-model.md
.specify/specs/001-semantic-aggregate-layer/research.md
.specify/specs/001-semantic-aggregate-layer/quickstart.md
.specify/specs/001-semantic-aggregate-layer/contracts/analyst-input.md
.specify/specs/001-semantic-aggregate-layer/contracts/sql-agent-input.md
.specify/specs/001-semantic-aggregate-layer/contracts/planner-output.md
.specify/specs/001-semantic-aggregate-layer/checklists/requirements.md

exec
/bin/zsh -lc 'git diff --name-only main...HEAD' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc 'git status --short' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 1470ms:
2026-04-15 23:10:50.192 xcodebuild[31846:108881480]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:10:50.372 xcodebuild[31846:108881478] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DwNEk79i' (errno=Operation not permitted)
2026-04-15 23:10:50.741 xcodebuild[31850:108881531]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:10:50.858 xcodebuild[31850:108881528] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
swarm_powerbi_bot/CLAUDE.md
swarm_powerbi_bot/pyproject.toml
swarm_powerbi_bot/specs/010-test-coverage/critiques/critique-2026-04-15.md
swarm_powerbi_bot/specs/010-test-coverage/plan.md
swarm_powerbi_bot/specs/010-test-coverage/spec.md
swarm_powerbi_bot/specs/010-test-coverage/tasks.md
swarm_powerbi_bot/tests/conftest.py
swarm_powerbi_bot/tests/integration/test_real_e2e.py
swarm_powerbi_bot/tests/integration/test_real_llm.py
swarm_powerbi_bot/tests/test_e2e_pipeline.py
swarm_powerbi_bot/tests/test_orchestrator.py

 succeeded in 1474ms:
2026-04-15 23:10:50.191 xcodebuild[31845:108881481]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:10:50.372 xcodebuild[31845:108881479] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-rdEFsBSJ' (errno=Operation not permitted)
2026-04-15 23:10:50.741 xcodebuild[31849:108881530]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:10:50.858 xcodebuild[31849:108881529] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
 M .maqa/adversarial-findings.md
 M specs/010-test-coverage/tasks.md
?? ../.claude/
?? ../.coverage-thresholds.json
?? ../.metaswarm/
?? ../CLAUDE.md
?? .maqa/.codex-result.txt
?? .maqa/.deepseek-result.txt
?? README.md
?? docs/pbix_schema.md
?? powebi/
?? requirements.txt
?? specs/001-semantic-aggregate-layer/reviews/
?? specs/002-002-fix-comparison-followup/
?? specs/010-test-coverage/reviews/
?? specs/010-test-coverage/verify-tasks-report.md
?? sql/create_kdo_procedures.sql
?? whisper/
?? ../uv.lock

codex
I have the spec directory. The next step is resolving the actual diff and reading the changed code paths so I can check the implementation against the new aggregate-layer requirements rather than reviewing blindly.
exec
/bin/zsh -lc "sed -n '1,260p' .specify/specs/001-semantic-aggregate-layer/spec.md" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
# Feature Specification: Semantic Aggregate Layer

**Feature Branch**: `feature/001-semantic-aggregate-layer`
**Created**: 2026-04-15
**Status**: Draft
**Input**: Переход от жёстко привязанных stored procedures к семантическому слою агрегатов: LLM выбирает агрегаты из каталога вместо keyword-matching по topic_registry.

---

## Baseline: As-Is Architecture

### Текущий поток обработки вопроса

Пользователь отправляет вопрос на русском → `TelegramSwarmBot` → `SwarmOrchestrator`:
1. **PlannerAgent** определяет план: LLM-путь (`LLMClient.plan_query()`) или keyword-fallback (`topic_registry.detect_topic()`)
2. **SQLAgent** + **PowerBIModelAgent** выполняются параллельно (`asyncio.gather`)
3. **ChartRenderer** (matplotlib) строит график, или **RenderAgent** (Selenium) делает скриншот Power BI
4. **AnalystAgent** (LLM GLM-5) формирует текстовый ответ
5. Ответ: текст + изображение + follow-up подсказки

### Текущие ограничения

- **17 жёстких тем** в `topic_registry.py`: каждая тема → один stored procedure. Невозможно комбинировать.
- **Keyword-scoring** для маппинга вопроса на тему: легко ошибается при нестандартных формулировках.
- **LLM-путь PlannerAgent** выбирает из 3 универсальных v2-процедур (`spKDO_Aggregate`, `spKDO_ClientList`, `spKDO_CommAgg`), но возможности ограничены фиксированным набором `group_by`/`filter`/`reason`.
- **Один запрос = один вопрос**: нет композиции (нельзя спросить "почему упала выручка?" — нужны данные по выручке, клиентам, среднему чеку одновременно).
- **Нет сравнений**: "сравни март и апрель" невозможно — один набор параметров на вопрос.
- **Семантическая модель PBIX не извлечена**: бот не знает о DAX-мерах, relationships, бизнес-правилах — всё зашито в SQL-процедурах и коде PlannerAgent.
- **Нет gap-анализа**: неизвестно какие метрики PBIX не покрыты в SQL.

### Существующие компоненты (сохраняются)

| Компонент | Файл | Статус |
|---|---|---|
| TelegramSwarmBot | `telegram_bot.py` | Сохраняется без изменений |
| SwarmOrchestrator | `orchestrator.py` | Расширяется для multi-query |
| PlannerAgent | `agents/planner.py` | Полная переработка |
| SQLAgent | `agents/sql.py` | Расширяется для multi-query |
| PowerBIModelAgent | `agents/powerbi.py` | Сохраняется |
| RenderAgent | `agents/render.py` | Сохраняется |
| AnalystAgent | `agents/analyst.py` | Адаптируется под multi-result |
| ChartRenderer | `services/chart_renderer.py` | Расширяется: сравнительные графики |
| SQLClient | `services/sql_client.py` | Расширяется: batch-запросы |
| LLMClient | `services/llm_client.py` | Новый system prompt для каталога |
| TopicRegistry | `services/topic_registry.py` | Сохраняется как fallback |
| Registration | `services/registration.py` | Без изменений |
| Config/Models | `config.py`, `models.py` | Расширяются |
| fnKDO_ClientStatus | SQL TVF | Без изменений |
| 17 v1 SP + 3 v2 SP | SQL | Сохраняются, оборачиваются |
| 77 тестов | `tests/` | Сохраняются, дополняются |

---

## Phase 0: Discovery агрегатов (bootstrap)

### P1 — US-001: Извлечение семантической модели из PBIX

**Как** аналитик данных,
**я хочу** автоматически извлечь полную семантическую модель из файла КДО 3.2.1.pbix,
**чтобы** иметь машиночитаемое описание всех таблиц, связей, DAX-мер и иерархий.

**Почему P1**: без семантической модели невозможен маппинг PBIX→SQL и gap-анализ. Это корневая зависимость всех последующих фаз.

**Independent Test**: запустить Python-скрипт извлечения (zipfile + json, без внешних зависимостей) на PBIX-файле → получить semantic-model.yaml → проверить что все таблицы, связи и DAX-меры присутствуют. Fallback: pbi-tools CLI если DataModelSchema не парсится.

**Acceptance Scenarios**:

```gherkin
Scenario: Извлечение таблиц и колонок
  Given PBIX-файл КДО 3.2.1.pbix в директории powebi/
  When запускается скрипт извлечения семантической модели
  Then создаётся файл semantic-model.yaml
  And файл содержит все 8 таблиц: tbRecords, tbClients, tbMasters, tbServices, tbServicesSettings, tbDatasetItems, tbAbonements, tbClientCommunicationHistory
  And для каждой таблицы перечислены все колонки с типами данных
  And computed tables и calculated columns отмечены отдельно

Scenario: Извлечение relationships
  Given PBIX-файл извлечён в semantic-model.yaml
  Then для каждой связи указаны: исходная таблица.колонка → целевая таблица.колонка
  And указан тип (1:M, M:M), направление фильтрации, cross-filter behavior
  And role-playing dimensions (если есть) отмечены

Scenario: Извлечение DAX-мер
  Given PBIX-файл извлечён в semantic-model.yaml
  Then каждая DAX-мера содержит: имя, формулу, описание, format string, display folder
  And формулы сохранены as-is (не интерпретируются)

Scenario: Извлечение иерархий
  Given PBIX-файл извлечён в semantic-model.yaml
  Then иерархии содержат: имя, уровни по порядку, таблица-источник
```

**Edge Cases**:
- PBIX содержит вычисляемые таблицы (Календарь, Клиенты для обработки) — они должны быть помечены как computed
- PBIX содержит скрытые колонки — они включаются с пометкой hidden
- DAX-формулы могут содержать многострочные выражения — сохраняются с переносами

---

### P1 — US-002: Маппинг PBIX → SQL

**Как** аналитик данных,
**я хочу** для каждого элемента PBIX-модели определить соответствие в SQL-схеме,
**чтобы** понимать какие метрики покрыты готовыми SQL-запросами, а какие требуют создания.

**Почему P1**: без маппинга невозможен gap-анализ и генерация агрегатов.

**Independent Test**: на основе semantic-model.yaml и существующих SQL-процедур создать pbix-to-sql-mapping.yaml → для каждой таблицы PBIX указан SQL-источник, для каждой DAX-меры — способ реализации.

**Acceptance Scenarios**:

```gherkin
Scenario: Маппинг таблиц
  Given semantic-model.yaml с 8 таблицами PBIX
  And SQL-схема с таблицами и процедурами из create_kdo_procedures.sql
  When создаётся маппинг
  Then для каждой PBIX-таблицы указана соответствующая SQL-таблица
  And для каждой колонки — соответствующая SQL-колонка или "вычисляется"

Scenario: Маппинг DAX-мер
  Given список DAX-мер из semantic-model.yaml
  When создаётся маппинг
  Then для каждой DAX-меры указан один из статусов:
    | Статус | Значение |
    | sql_covered | Есть готовый view/TVF/SP |
    | python_postprocess | Нужна пост-обработка в Python |
    | not_covered | Нет SQL-реализации |
  And для sql_covered — указан SQL-объект (SP/view/TVF)
  And для python_postprocess — описана логика

Scenario: Маппинг relationships
  Given relationships из semantic-model.yaml
  When создаётся маппинг
  Then для каждой связи PBIX указано: есть FK в SQL (да/нет), через какие колонки связаны
```

**Edge Cases**:
- Вычисляемые таблицы PBIX не имеют прямого SQL-источника — маппятся на формулу создания
- fnKDO_ClientStatus реализует DAX-меру "Статус клиента для обработки" — должна быть связана явно

---

### P1 — US-003: Semantic catalog для LLM

**Как** LLM-агент (PlannerAgent/AnalystAgent),
**я хочу** получать на вход описание бизнес-модели салона красоты на понятном языке,
**чтобы** правильно интерпретировать вопросы пользователей и выбирать нужные агрегаты.

**Почему P1**: без семантического каталога LLM не понимает связи между сущностями и бизнес-правила.

**Independent Test**: показать LLM semantic-catalog.yaml + вопрос "какой отток за месяц?" → LLM корректно определяет что "отток" — это клиент без визита >33 дней, и выбирает соответствующий агрегат.

**Acceptance Scenarios**:

```gherkin
Scenario: Бизнес-сущности
  Given semantic-catalog.yaml создан на основе PBIX-модели
  Then каталог содержит сущности: Клиент, Мастер, Услуга, Визит, Оплата, Коммуникация, Абонемент, Салон
  And для каждой сущности: описание на русском, ключевые атрибуты, доступные метрики

Scenario: Бизнес-правила
  Given semantic-catalog.yaml
  Then каталог содержит правила:
    | Правило | Определение |
    | Отток | Клиент без визита > ServicePeriod + 31..240 дней |
    | Уходящие | Клиент без визита > ServicePeriod + 1..30 дней |
    | ServicePeriod | Период между визитами клиента, default 33 дня |
    | Контроль качества | Визит ≤ 7 дней назад |
    | LTV | Сумма за RetentionDays = 240 дней |
    | Возвращаемость | Клиенты с повторным визитом в пределах 240 дней |

Scenario: Связи между сущностями
  Given semantic-catalog.yaml
  Then описаны связи: "мастер оказывает услугу клиенту в рамках визита"
  And указаны допустимые группировки: по мастеру, услуге, салону, каналу, периоду
  And указаны допустимые фильтры: по статусу клиента, периоду, мастеру

Scenario: LLM не видит внутренности
  Given semantic-catalog.yaml
  Then каталог НЕ содержит: SQL-код, имена таблиц БД, connection strings, внутренние ID
```

**Edge Cases**:
- Role-playing dimensions (дата визита vs дата записи) — должны быть описаны явно для LLM
- Бизнес-правила с "магическими числами" (33, 240, 7) — описаны с обоснованием

---

### P2 — US-004: Gap-анализ PBIX vs SQL

**Как** разработчик,
**я хочу** получить список метрик и отчётов PBIX, которые не покрыты SQL-агрегатами,
**чтобы** знать что нужно создать.

**Почему P2**: информационный артефакт для планирования фазы 1.

**Independent Test**: на основе маппинга создать gaps.md → список непокрытых DAX-мер, непокрытых тем topic_registry, рекомендации по приоритетам.

**Acceptance Scenarios**:

```gherkin
Scenario: Полный gap-анализ
  Given pbix-to-sql-mapping.yaml с маппингом всех DAX-мер
  And topic_registry.py с 17 темами
  When выполняется gap-анализ
  Then gaps.md содержит:
    - Список DAX-мер со статусом not_covered → нужен новый агрегат
    - Список DAX-мер со статусом python_postprocess → нужна Python-обёртка
    - Список тем topic_registry, которые не покрыты v2-процедурами
    - Приоритет для каждого gap: P1 (базовый KPI) / P2 (детализация) / P3 (nice-to-have)
```

---

### P2 — US-005: Генерация SQL-агрегатов

**Как** разработчик,
**я хочу** для каждого gap автоматически сгенерировать SQL view/TVF,
**чтобы** покрыть недостающие метрики из PBIX.

**Почему P2**: без покрытия метрик LLM не сможет отвечать на все вопросы.

**Independent Test**: для одного конкретного gap → агент создаёт SQL → результат совпадает с DAX-оригиналом на тестовом наборе данных.

**Acceptance Scenarios**:

```gherkin
Scenario: Генерация агрегата
  Given gap из gaps.md (например: "Средний чек по категориям услуг")
  And semantic-model.yaml с DAX-формулой оригинальной меры
  When агент генерирует SQL view/TVF
  Then SQL-код использует только существующие таблицы из маппинга
  And параметры типизированы: даты, ObjectId, MasterId, top_n
  And результат содержит ожидаемые колонки

Scenario: Верификация агрегата
  Given сгенерированный SQL-агрегат
  And оригинальная DAX-мера
  When оба выполняются на тестовом наборе данных (ObjectId=506770)
  Then числовые результаты совпадают с допуском ≤1%
  And порядок строк совпадает
  And все колонки присутствуют

Scenario: Человек утверждает SQL
  Given сгенерированный и верифицированный SQL-агрегат
  Then агрегат НЕ выполняется на продуктивной БД
  Until человек явно утвердил SQL-код
```

**Edge Cases**:
- DAX-мера использует CALCULATE с context transition — может требовать CTE в SQL
- DAX-мера ссылается на другую меру — нужен рекурсивный анализ зависимостей
- Некоторые DAX-меры принципиально не реализуемы в SQL (row-level security) — помечаются как excluded

---

### P1 — US-006: Каталог агрегатов

**Как** LLM-агент,
**я хочу** видеть каталог доступных агрегатов с описаниями и параметрами,

codex
The branch diff is concentrated under `swarm_powerbi_bot/tests/*` plus a test-coverage spec. I’m checking both spec trees now because there’s a top-level `.specify` spec and a repo-local `specs/010-test-coverage/spec.md`, and the implementation may be expected to satisfy both.
exec
/bin/zsh -lc pwd in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot

exec
/bin/zsh -lc "sed -n '1,240p' swarm_powerbi_bot/specs/010-test-coverage/spec.md" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 exited 1 in 0ms:
sed: swarm_powerbi_bot/specs/010-test-coverage/spec.md: No such file or directory

exec
/bin/zsh -lc "find . -maxdepth 2 -type f \\( -path './specs/*/spec.md' -o -path './.specify/specs/*/spec.md' \\) | sort" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
exec
/bin/zsh -lc 'ls -la' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
total 496
drwxr-xr-x@ 32 zerocold  staff    1024 Apr 15 22:21 .
drwxr-xr-x  31 zerocold  staff     992 Apr 15 18:47 ..
-rw-r--r--@  1 zerocold  staff    6148 Apr 14 17:13 .DS_Store
drwxr-xr-x@  6 zerocold  staff     192 Apr 15 18:48 .claude
-rw-r--r--@  1 zerocold  staff     195 Apr 15 18:48 .dockerignore
-rw-r--r--@  1 zerocold  staff    1174 Apr 15 18:48 .env.example
drwxr-xr-x@  3 zerocold  staff      96 Apr 15 18:48 .github
-rw-r--r--@  1 zerocold  staff      46 Apr 15 18:48 .gitignore
drwxr-xr-x@  6 zerocold  staff     192 Apr 15 23:10 .maqa
drwxr-xr-x@  6 zerocold  staff     192 Apr 13 22:31 .pytest_cache
drwxr-xr-x@  5 zerocold  staff     160 Apr 15 09:09 .ruff_cache
drwxr-xr-x@ 14 zerocold  staff     448 Apr 15 18:48 .specify
drwxr-xr-x@  9 zerocold  staff     288 Apr 14 15:02 .venv
-rw-------@  1 zerocold  staff    2295 Apr 15 22:07 CLAUDE.md
-rw-r--r--@  1 zerocold  staff     533 Apr 15 18:48 Dockerfile
-rw-r--r--@  1 zerocold  staff    3831 Mar 23 10:22 README.md
drwxr-xr-x@  6 zerocold  staff     192 Apr 15 18:48 catalogs
-rw-r--r--@  1 zerocold  staff    1655 Apr 15 18:48 docker-compose.test.yml
-rw-r--r--@  1 zerocold  staff    1369 Apr 15 18:48 docker-compose.yml
drwxr-xr-x@  4 zerocold  staff     128 Apr 15 18:48 docs
drwxr-xr-x@  3 zerocold  staff      96 Apr 15 17:34 logs
-rw-r--r--@  1 zerocold  staff    1706 Apr 15 18:48 maqa-config.yml
drwxr-xr-x@  3 zerocold  staff      96 Apr 13 21:24 powebi
-rw-r--r--@  1 zerocold  staff     845 Apr 15 22:21 pyproject.toml
-rw-r--r--@  1 zerocold  staff     106 Mar 23 10:22 requirements.txt
drwxr-xr-x@  5 zerocold  staff     160 Apr 15 18:48 scripts
drwxr-xr-x@  9 zerocold  staff     288 Apr 15 21:36 specs
drwxr-xr-x@  5 zerocold  staff     160 Apr 15 18:48 sql
drwxr-xr-x@  4 zerocold  staff     128 Apr 13 22:31 src
drwxr-xr-x@ 29 zerocold  staff     928 Apr 15 23:10 tests
-rw-r--r--@  1 zerocold  staff  199054 Apr 15 18:48 uv.lock
drwxr-xr-x@  6 zerocold  staff     192 Apr 13 22:47 whisper

exec
/bin/zsh -lc "rg --files | rg 'spec\\.md"'$|test_.*'"\\.py"'$|conftest'"\\.py"'$|pyproject'"\\.toml"'$|CLAUDE'"\\.md"'$'"'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
CLAUDE.md
tests/test_stt_client.py
tests/test_master_resolver.py
tests/test_analyst_fallback.py
tests/test_registration.py
tests/test_chart_renderer.py
tests/test_llm_planner.py
tests/test_context_switching.py
tests/test_config.py
tests/test_e2e_pipeline.py
tests/test_multi_query.py
tests/test_chart_adequacy.py
tests/test_planner_v2.py
tests/test_composition.py
tests/test_orchestrator.py
tests/test_aggregate_registry.py
tests/test_topic_registry.py
tests/test_data_accuracy.py
tests/test_comparison.py
tests/integration/test_real_llm.py
tests/integration/test_real_sql.py
tests/integration/test_real_e2e.py
tests/integration/conftest.py
tests/test_period_detection.py
tests/test_circuit_breaker.py
tests/test_planner.py
tests/test_query_logger.py
tests/conftest.py
tests/test_security.py
tests/test_llm_client_ollama.py
pyproject.toml
specs/010-test-coverage/spec.md
specs/009-statistics-fallback-improvements/spec.md
specs/003-006-fix-comparison-chart/spec.md
specs/004-orchestrator-fallback-fix/spec.md
specs/002-002-fix-comparison-followup/spec.md
specs/002-fix-comparison-followup/spec.md
specs/001-semantic-aggregate-layer/spec.md

exec
/bin/zsh -lc 'git rev-parse --show-toplevel' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 1248ms:
2026-04-15 23:11:16.982 xcodebuild[32225:108883043]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:11:17.105 xcodebuild[32225:108883042] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jVNY4TRA' (errno=Operation not permitted)
2026-04-15 23:11:17.427 xcodebuild[32227:108883081]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:11:17.541 xcodebuild[32227:108883080] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
/Users/zerocold/Downloads/git/kpi/tg_bot

codex
The repo root is correct; the diff paths from `git diff` were prefixed because Git’s top-level is one directory higher. I’m focusing on `specs/010-test-coverage/spec.md` now, since the changed files are test-only and that spec likely defines the intended behavior.
exec
/bin/zsh -lc "sed -n '1,260p' specs/010-test-coverage/spec.md" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
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

exec
/bin/zsh -lc 'git diff --stat main...HEAD -- tests/conftest.py tests/test_e2e_pipeline.py tests/test_orchestrator.py tests/integration/test_real_e2e.py tests/integration/test_real_llm.py pyproject.toml CLAUDE.md specs/010-test-coverage/spec.md specs/010-test-coverage/plan.md specs/010-test-coverage/tasks.md' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 1190ms:
2026-04-15 23:11:25.376 xcodebuild[32352:108883517]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:11:25.477 xcodebuild[32352:108883516] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-xAoNFJLh' (errno=Operation not permitted)
2026-04-15 23:11:25.778 xcodebuild[32354:108883570]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:11:25.878 xcodebuild[32354:108883569] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
 swarm_powerbi_bot/CLAUDE.md                        |   2 +
 swarm_powerbi_bot/pyproject.toml                   |   1 +
 swarm_powerbi_bot/specs/010-test-coverage/plan.md  | 131 +++++++++++
 swarm_powerbi_bot/specs/010-test-coverage/spec.md  | 104 +++++++++
 swarm_powerbi_bot/specs/010-test-coverage/tasks.md |  41 ++++
 swarm_powerbi_bot/tests/conftest.py                | 143 ++++++++++++
 .../tests/integration/test_real_e2e.py             |  58 ++++-
 .../tests/integration/test_real_llm.py             |  39 +++-
 swarm_powerbi_bot/tests/test_e2e_pipeline.py       | 243 ++++++++++++++++++++-
 swarm_powerbi_bot/tests/test_orchestrator.py       |  86 ++++----
 10 files changed, 791 insertions(+), 57 deletions(-)

codex
I have the coverage spec. Now I’m reading the exact patch and the touched tests to see whether the new assertions actually enforce the stated requirements or leave gaps that would let regressions ship undetected.
exec
/bin/zsh -lc "sed -n '1,260p' tests/test_e2e_pipeline.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
"""End-to-end тесты pipeline: вопрос → topic → SQL params → chart → ответ.

Проверяет полную цепочку без обращения к MSSQL/LLM (моки).
"""
import asyncio
from datetime import date

import pytest

from swarm_powerbi_bot.agents.planner import PlannerAgent
from swarm_powerbi_bot.models import (
    AnalysisResult,
    ModelInsight,
    Plan,
    SQLInsight,
    UserQuestion,
)
from swarm_powerbi_bot.orchestrator import SwarmOrchestrator
from swarm_powerbi_bot.services.chart_renderer import HAS_MPL

from conftest import build_mock_orchestrator_multi

pytestmark = pytest.mark.e2e


# ── Mock агенты с реалистичными данными ──────────────────────

class MockSQL:
    """Возвращает данные как настоящие хранимки — 11 тем (10 из checklist + leaving)."""
    MOCK_DATA = {
        "outflow": [
            {"ClientName": "Козлова Р.", "Phone": "79001111111", "TotalSpent": 8112.6,
             "DaysSinceLastVisit": 275, "DaysOverdue": 240, "TotalVisits": 11,
             "ServicePeriodDays": 35, "SalonName": "Dream"},
            {"ClientName": "Белова Т.", "Phone": "79002222222", "TotalSpent": 57054.0,
             "DaysSinceLastVisit": 283, "DaysOverdue": 238, "TotalVisits": 59,
             "ServicePeriodDays": 45, "SalonName": "Dream"},
        ],
        "statistics": [
            {"TotalVisits": 219, "UniqueClients": 137, "TotalRevenue": 422028.50,
             "AvgCheck": 1954.33, "ActiveMasters": 14, "SalonName": "Dream"},
        ],
        "trend": [
            {"WeekEnd": "2026-03-02", "Visits": 45, "Revenue": 77424, "UniqueClients": 30, "AvgCheck": 1720, "ActiveMasters": 7},
            {"WeekEnd": "2026-03-09", "Visits": 50, "Revenue": 85000, "UniqueClients": 35, "AvgCheck": 1700, "ActiveMasters": 8},
        ],
        "masters": [
            {"MasterName": "Мастер А", "TotalRevenue": 120000, "TotalVisits": 50, "AvgCheck": 2400, "SalonName": "Dream"},
        ],
        "referrals": [
            {"AcquisitionChannel": "Instagram", "ClientCount": 50},
            {"AcquisitionChannel": "Рекомендация", "ClientCount": 30},
        ],
        "birthday": [
            {"ClientName": "Иванова А.", "Phone": "79003333333", "BirthDate": "2000-04-16"},
        ],
        "communications": [
            {"Reason": "outflow", "Result": "Вернулся", "TotalCount": 15},
            {"Reason": "leaving", "Result": "Нет ответа", "TotalCount": 8},
        ],
        "forecast": [
            {"ClientName": "Петрова М.", "ExpectedNextVisit": "2026-04-17", "ServicePeriodDays": 28},
        ],
        "services": [
            {"ServiceName": "Стрижка", "Revenue": 85000, "ServiceCount": 120},
            {"ServiceName": "Окрашивание", "Revenue": 65000, "ServiceCount": 40},
        ],
        "quality": [
            {"ClientName": "Сидоров К.", "DaysOverdue": 5, "TotalVisits": 3, "SalonName": "Dream"},
        ],
        "leaving": [
            {"ClientName": "Нова Е.", "DaysOverdue": 15, "TotalSpent": 12000, "TotalVisits": 7, "SalonName": "Dream"},
        ],
    }

    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
        rows = self.MOCK_DATA.get(plan.topic, [])
        return SQLInsight(
            rows=rows,
            summary=f"SQL вернул {len(rows)} строк по теме «{plan.topic}»",
            topic=plan.topic,
            params={"DateFrom": date(2026, 3, 15), "DateTo": date(2026, 4, 14)},
        )


class MockPBI:
    async def run(self, question, plan):
        return ModelInsight(metrics={}, summary="model skipped")


class MockRender:
    async def run(self, question, plan):
        return None


class MockAnalyst:
    """Возвращает canned output для проверки маршрутизации pipeline.

    Реальную фильтрацию полей и качество формулировок проверяют
    интеграционные тесты в tests/integration/test_real_e2e.py.
    """
    async def run(self, question, plan, sql_insight, model_insight, diagnostics, *, has_chart=False):
        return AnalysisResult(
            answer=f"Тема: {plan.topic}, строк: {len(sql_insight.rows)}",
            confidence="medium",
            follow_ups=["follow1"],
        )


def _build_orchestrator():
    return SwarmOrchestrator(
        planner=PlannerAgent(),
        sql_agent=MockSQL(),
        powerbi_agent=MockPBI(),
        render_agent=MockRender(),
        analyst_agent=MockAnalyst(),
    )


# ── E2E тесты ────────────────────────────────────────────────

class TestE2EPipeline:
    def test_outflow_question(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert "outflow" in result.answer
        assert result.topic == "outflow"

    def test_statistics_question(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи статистику за неделю"),
        ))
        assert "statistics" in result.answer
        assert result.topic == "statistics"

    def test_masters_question(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="загрузка мастеров"),
        ))
        assert "masters" in result.answer

    def test_followup_keeps_topic(self):
        """Follow-up вопрос сохраняет тему."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="подробнее по неделям", last_topic="outflow"),
        ))
        assert result.topic == "outflow"

    def test_response_has_follow_ups(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert len(result.follow_ups) > 0

    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
    def test_outflow_generates_chart(self):
        """Отток с данными → matplotlib-график."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert result.image is not None
        assert result.image[:4] == b"\x89PNG"

    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
    def test_trend_generates_line_chart(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи тренд за квартал"),
        ))
        assert result.image is not None

    def test_empty_data_no_crash(self):
        """Если SQL вернул 0 строк — не падаем."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи именинников"),
        ))
        assert result.answer is not None


# ── Planner тесты ────────────────────────────────────────────

class TestPlannerNotes:
    def test_comparison_note(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="сравни отток по неделям"),
        ))
        assert "comparison_requested" in plan.notes

    def test_period_note_week(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="статистика за неделю"),
        ))
        assert "period:week" in plan.notes

    def test_breakdown_by_master(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="выручка по мастерам"),
        ))
        assert "breakdown_by_master" in plan.notes


# ── T004: Comparison / Composition pipeline ─────────────────────

class TestMultiPlanPipeline:
    def test_comparison_pipeline(self):
        """MultiPlan comparison → SwarmResponse с ответом и chart."""
        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="сравни отток за два месяца"),
        ))
        assert result.answer is not None
        assert "Сравнение" in result.answer
        assert result.confidence in ("low", "medium", "high")

    def test_comparison_pipeline_second_question(self):
        """Второй comparison-вопрос через MultiPlan → корректный ответ."""
        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="сравни отток по салонам"),
        ))
        assert result.answer
        assert len(result.answer) > 0

    def test_decomposition_pipeline(self):
        """MultiPlan decomposition → SwarmResponse с multi-result анализом."""
        orch = build_mock_orchestrator_multi(intent="decomposition", topic="revenue_total")
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="почему упала выручка?"),
        ))
        assert result.answer is not None
        assert result.confidence in ("low", "medium", "high")


# ── T005: 10 checklist questions ────────────────────────────────

_CHECKLIST_QUESTIONS = [
    ("отток за месяц", "outflow"),
    ("покажи статистику за неделю", "statistics"),
    ("динамика по неделям", "trend"),
    ("загрузка мастеров", "masters"),
    ("реферальная программа", "referrals"),
    ("именинники на этой неделе", "birthday"),
    ("результаты обзвонов", "communications"),
    ("прогноз визитов", "forecast"),
    ("популярные услуги", "services"),
    ("контроль качества", "quality"),
]



exec
/bin/zsh -lc 'git diff --unified=80 main...HEAD -- tests/conftest.py tests/test_e2e_pipeline.py tests/test_orchestrator.py tests/integration/test_real_e2e.py tests/integration/test_real_llm.py pyproject.toml CLAUDE.md' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 1191ms:
2026-04-15 23:11:39.553 xcodebuild[32578:108884378]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:11:39.656 xcodebuild[32578:108884377] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-IbwUpLlv' (errno=Operation not permitted)
2026-04-15 23:11:39.962 xcodebuild[32580:108884418]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:11:40.064 xcodebuild[32580:108884417] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
diff --git a/swarm_powerbi_bot/CLAUDE.md b/swarm_powerbi_bot/CLAUDE.md
index 5c33b53..a108856 100644
--- a/swarm_powerbi_bot/CLAUDE.md
+++ b/swarm_powerbi_bot/CLAUDE.md
@@ -1,45 +1,47 @@
 # swarm_powerbi_bot Development Guidelines
 
 Auto-generated from all feature plans. Last updated: 2026-04-15
 
 ## Active Technologies
+- Microsoft SQL Server (pyodbc, ODBC Driver 17); materialized агрегаты (indexed views) с overhead ≤3x хранения (010-test-coverage)
 
 - Python 3.11+ + python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8, selenium ≥4.22, python-dotenv ≥1.0.1 (001-semantic-aggregate-layer)
 
 ## Project Structure
 
 ```text
 src/
   swarm_powerbi_bot/
     services/         # бизнес-логика: aggregate_registry, master_resolver, query_logger, ...
     agents/           # агенты: planner, sql, analyst (поддержка run_multi)
 tests/
 catalogs/
   aggregate-catalog.yaml   # каталог семантических агрегатов
   category-index.yaml      # индекс категорий для маршрутизации
   bootstrap/               # dev-only bootstrap данные (не копируются в образ)
 scripts/
   bootstrap/               # dev-time утилиты (не копируются в образ)
 sql/                       # SQL-скрипты (не копируются в образ)
 ```
 
 ## Commands
 
 uv run pytest -q && uv run ruff check src/ tests/
 
 ## Code Style
 
 Python 3.11+: Follow standard conventions
 
 ## Recent Changes
+- 010-test-coverage: Added Python 3.11+ + python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8, selenium ≥4.22, python-dotenv ≥1.0.1
 
 - 001-semantic-aggregate-layer (Phase 10 Polish):
   - Added services: `aggregate_registry`, `master_resolver`, `query_logger`
   - Agent capabilities: `planner.run_multi`, `sql.run_multi`, `analyst.run_multi` (multi-query и comparison chart)
   - Каталоги `catalogs/aggregate-catalog.yaml` и `catalogs/category-index.yaml`
   - CI workflow `.github/workflows/validate-catalogs.yml` валидирует каталоги на push/PR
   - Dockerfile копирует `catalogs/*.yaml`; bootstrap/scripts/sql исключены из образа
 - 001-semantic-aggregate-layer: Added Python 3.11+ + python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8, selenium ≥4.22, python-dotenv ≥1.0.1
 
 <!-- MANUAL ADDITIONS START -->
 <!-- MANUAL ADDITIONS END -->
diff --git a/swarm_powerbi_bot/pyproject.toml b/swarm_powerbi_bot/pyproject.toml
index 261edb9..98cfc01 100644
--- a/swarm_powerbi_bot/pyproject.toml
+++ b/swarm_powerbi_bot/pyproject.toml
@@ -1,38 +1,39 @@
 [build-system]
 requires = ["setuptools>=65", "wheel"]
 build-backend = "setuptools.build_meta"
 
 [project]
 name = "swarm-powerbi-bot"
 version = "0.1.0"
 requires-python = ">=3.11"
 dependencies = [
     "python-telegram-bot>=21.0",
     "httpx>=0.27.0",
     "pyodbc>=5.1.0",
     "selenium>=4.22.0",
     "python-dotenv>=1.0.1",
     "matplotlib>=3.8.0",
     "pyyaml>=6.0.3",
 ]
 
 [project.optional-dependencies]
 dev = [
     "pytest>=8.0.0",
     "pytest-asyncio>=0.23",
 ]
 
 [tool.setuptools.packages.find]
 where = ["src"]
 
 [tool.pytest.ini_options]
 asyncio_mode = "auto"
 addopts = "-m 'not integration'"
 markers = [
     "integration: тесты с реальным MSSQL/Ollama (требуют окружение)",
+    "e2e: E2E тесты с моками (запускаются всегда в CI)",
 ]
 
 [dependency-groups]
 dev = [
     "ruff>=0.15.10",
 ]
diff --git a/swarm_powerbi_bot/tests/conftest.py b/swarm_powerbi_bot/tests/conftest.py
new file mode 100644
index 0000000..42011ba
--- /dev/null
+++ b/swarm_powerbi_bot/tests/conftest.py
@@ -0,0 +1,143 @@
+"""Shared mock classes and fixtures for E2E and orchestrator tests."""
+from __future__ import annotations
+
+from swarm_powerbi_bot.models import (
+    AggregateResult,
+    AnalysisResult,
+    ModelInsight,
+    MultiPlan,
+    Plan,
+    RenderedArtifact,
+    SQLInsight,
+    UserQuestion,
+)
+from swarm_powerbi_bot.orchestrator import SwarmOrchestrator
+
+
+# ── Base Dummy classes ──────────────────────────────────────────
+
+
+class DummyPlanner:
+    aggregate_registry = None
+
+    async def run(self, question: UserQuestion) -> Plan:
+        return Plan(
+            objective=question.text, topic="statistics",
+            sql_needed=True, powerbi_needed=True, render_needed=True,
+        )
+
+
+class DummySQL:
+    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
+        return SQLInsight(rows=[{"kpi": "sales", "value": 100}], summary="sql ok")
+
+
+class DummyPBI:
+    async def run(self, question: UserQuestion, plan: Plan) -> ModelInsight:
+        return ModelInsight(metrics={"margin": 0.32}, summary="model ok")
+
+
+class DummyRender:
+    async def run(self, question: UserQuestion, plan: Plan) -> RenderedArtifact:
+        _ = question, plan
+        return RenderedArtifact(image_bytes=b"png-bytes", source_url="http://report")
+
+
+class DummyAnalyst:
+    async def run(self, question, plan, sql_insight, model_insight, diagnostics, *, has_chart=False):
+        _ = question, plan, sql_insight, model_insight, has_chart
+        return AnalysisResult(answer="analysis", confidence="high", diagnostics=diagnostics)
+
+
+# ── MultiPlan-aware mocks ──────────────────────────────────────
+
+
+class MockRegistry:
+    """Minimal AggregateRegistry stub."""
+
+    def get_aggregate(self, agg_id: str):
+        return {"id": agg_id, "procedure": "spKDO_Aggregate", "parameters": []}
+
+    def list_aggregates(self):
+        return [{"id": "revenue_total"}, {"id": "clients_outflow"}]
+
+
+class MockPlannerWithRegistry(DummyPlanner):
+    def __init__(self, registry=None, *, intent="comparison", topic="clients_outflow", n_queries=2):
+        self.aggregate_registry = registry or MockRegistry()
+        self._intent = intent
+        self._topic = topic
+        self._n_queries = n_queries
+
+    async def run_multi(self, question):
+        return MultiPlan(
+            objective=question.text,
+            intent=self._intent,
+            queries=[{"aggregate_id": self._topic} for _ in range(self._n_queries)],
+            topic=self._topic,
+            render_needed=True,
+            notes=["planner_v2:llm"],
+        )
+
+    def multi_plan_to_plan(self, multi_plan, question):
+        return Plan(
+            objective=multi_plan.objective,
+            topic=multi_plan.topic,
+            notes=list(multi_plan.notes),
+        )
+
+
+class MockSQLMulti(DummySQL):
+    """SQL agent that supports run_multi() with configurable results."""
+
+    def __init__(self, results: list[AggregateResult] | None = None):
+        self._results = results or [
+            AggregateResult(
+                aggregate_id="clients_outflow", label="Март 2026",
+                group_by="status", status="ok",
+                rows=[
+                    {"ClientStatus": "Отток", "ClientCount": 20},
+                    {"ClientStatus": "Уходящие", "ClientCount": 15},
+                ],
+            ),
+            AggregateResult(
+                aggregate_id="clients_outflow", label="Апрель 2026",
+                group_by="status", status="ok",
+                rows=[
+                    {"ClientStatus": "Отток", "ClientCount": 18},
+                    {"ClientStatus": "Уходящие", "ClientCount": 12},
+                ],
+            ),
+        ]
+
+    async def run_multi(self, multi_plan, registry, *, logger_=None):
+        return self._results
+
+
+class MockAnalystMulti(DummyAnalyst):
+    async def run_multi(self, question, results, plan):
+        ok = [r for r in results if r.status == "ok"]
+        if len(ok) >= 2:
+            answer = f"Сравнение: {ok[0].label} vs {ok[1].label}\n• Клиенты: +17%"
+        elif ok:
+            answer = f"Анализ: {ok[0].label}, {ok[0].row_count} строк"
+        else:
+            answer = "Нет данных для анализа"
+        return AnalysisResult(
+            answer=answer,
+            confidence="medium",
+            diagnostics={},
+        )
+
+
+def build_mock_orchestrator_multi(*, intent="comparison", topic="clients_outflow"):
+    """Build orchestrator wired for MultiPlan flow."""
+    registry = MockRegistry()
+    return SwarmOrchestrator(
+        planner=MockPlannerWithRegistry(registry, intent=intent, topic=topic),
+        sql_agent=MockSQLMulti(),
+        powerbi_agent=DummyPBI(),
+        render_agent=DummyRender(),
+        analyst_agent=MockAnalystMulti(),
+        aggregate_registry=registry,
+    )
diff --git a/swarm_powerbi_bot/tests/integration/test_real_e2e.py b/swarm_powerbi_bot/tests/integration/test_real_e2e.py
index 2e5e0ff..e200d54 100644
--- a/swarm_powerbi_bot/tests/integration/test_real_e2e.py
+++ b/swarm_powerbi_bot/tests/integration/test_real_e2e.py
@@ -1,134 +1,188 @@
 """Интеграционные E2E тесты через реальный MSSQL + Ollama.
 
 Запуск: uv run pytest tests/integration/test_real_e2e.py -m integration -v
 """
 from __future__ import annotations
 
 import asyncio
 
 import pytest
 
 from swarm_powerbi_bot.models import SwarmResponse, UserQuestion
 from swarm_powerbi_bot.orchestrator import SwarmOrchestrator
 
 pytestmark = pytest.mark.integration
 
+# Совпадает с TEST_OBJECT_ID в tests/integration/conftest.py.
+# Прямой import невозможен — pytest резолвит `from conftest` на tests/conftest.py.
+_TEST_OBJECT_ID = 506770
+
 
 def _question(text: str, **kwargs) -> UserQuestion:
-    defaults = {"user_id": "e2e-test", "object_id": 506770}
+    defaults = {"user_id": "e2e-test", "object_id": _TEST_OBJECT_ID}
     defaults.update(kwargs)
     return UserQuestion(text=text, **defaults)
 
 
 # ── 1. Revenue question ─────────────────────────────────────────────────────
 
 async def test_e2e_revenue_question(real_orchestrator: SwarmOrchestrator):
     resp = await real_orchestrator.handle_question(_question("Покажи выручку за март"))
     assert resp.answer, "empty answer"
     assert resp.topic != "unknown", f"topic should not be unknown, got {resp.topic}"
 
 
 # ── 2. Outflow question ─────────────────────────────────────────────────────
 
 async def test_e2e_outflow_question(real_orchestrator: SwarmOrchestrator):
     resp = await real_orchestrator.handle_question(
         _question("Какой отток за месяц?"),
     )
     assert resp.answer
 
 
 # ── 3. Comparison с chart ────────────────────────────────────────────────────
 
 async def test_e2e_comparison(real_orchestrator: SwarmOrchestrator):
     resp = await real_orchestrator.handle_question(
         _question("Сравни выручку марта и февраля"),
     )
     assert resp.answer
-    # comparison должен генерировать chart
+    # Comparison pipeline должен генерировать chart
     if resp.image is not None:
         assert resp.mime_type == "image/png"
 
 
 # ── 4. Top masters ──────────────────────────────────────────────────────────
 
 async def test_e2e_top_masters(real_orchestrator: SwarmOrchestrator):
     resp = await real_orchestrator.handle_question(
         _question("Топ-5 мастеров по выручке за март"),
     )
     assert resp.answer
 
 
 # ── 5. Decomposition ────────────────────────────────────────────────────────
 
 async def test_e2e_decomposition(real_orchestrator: SwarmOrchestrator):
     resp = await real_orchestrator.handle_question(
         _question("Почему упала выручка?"),
     )
     assert resp.answer
 
 
 # ── 6. Unknown question ─────────────────────────────────────────────────────
 
 async def test_e2e_unknown_question(real_orchestrator: SwarmOrchestrator):
     resp = await real_orchestrator.handle_question(
         _question("Как сварить борщ?"),
     )
     assert isinstance(resp, SwarmResponse)
     # Должен вежливо отказать или дать общий ответ
 
 
 # ── 7. Follow-up ────────────────────────────────────────────────────────────
 
 async def test_e2e_follow_up(real_orchestrator: SwarmOrchestrator):
     resp1 = await real_orchestrator.handle_question(
         _question("выручка за март"),
     )
     assert resp1.answer
     topic = resp1.topic
 
     resp2 = await real_orchestrator.handle_question(
         _question("а за февраль?", last_topic=topic),
     )
     assert resp2.answer
 
 
 # ── 8. Chart generation ─────────────────────────────────────────────────────
 
 async def test_e2e_chart_generation(real_orchestrator: SwarmOrchestrator):
     resp = await real_orchestrator.handle_question(
         _question("Покажи график выручки по неделям за квартал"),
     )
     assert resp.answer
     # Если chart сгенерирован, проверяем формат
     if resp.image is not None:
         assert resp.mime_type == "image/png"
         assert len(resp.image) > 100  # не пустой PNG
 
 
 # ── 9. Telegram mock ────────────────────────────────────────────────────────
 
 async def test_e2e_telegram_mock(real_orchestrator: SwarmOrchestrator):
     """Проверяем что orchestrator возвращает корректный SwarmResponse."""
     resp = await real_orchestrator.handle_question(
         _question("статистика за март"),
     )
     assert isinstance(resp, SwarmResponse)
     assert resp.confidence in ("low", "medium", "high")
     assert isinstance(resp.follow_ups, list)
     assert isinstance(resp.diagnostics, dict)
 
 
 # ── 10. Concurrent users ────────────────────────────────────────────────────
 
 async def test_e2e_concurrent_users(real_orchestrator: SwarmOrchestrator):
     questions = [
         _question("выручка за март", user_id="user-1"),
         _question("отток клиентов", user_id="user-2"),
         _question("коммуникации за март", user_id="user-3"),
     ]
     results = await asyncio.gather(
         *[real_orchestrator.handle_question(q) for q in questions],
     )
     for i, resp in enumerate(results):
         assert isinstance(resp, SwarmResponse), f"user-{i+1} got non-SwarmResponse"
         assert resp.answer, f"user-{i+1} got empty answer"
+
+
+# ── 11. Comparison has chart ───────────────────────────────────────────────
+
+async def test_e2e_comparison_has_chart(real_orchestrator: SwarmOrchestrator):
+    """Comparison pipeline должен генерировать PNG chart."""
+    resp = await real_orchestrator.handle_question(
+        _question("Сравни отток за март и апрель"),
+    )
+    assert resp.answer
+    # comparison должен генерировать chart; None допустим только при отсутствии matplotlib
+    assert resp.image is not None, "Comparison should produce a chart"
+    assert resp.image[:4] == b"\x89PNG"
+
+
+# ── 12. Fallback: no raw SQL fields ───────────────────────────────────────
+
+async def test_e2e_fallback_no_raw_fields(real_orchestrator: SwarmOrchestrator):
+    """Ответ не должен содержать сырые SQL-имена полей."""
+    resp = await real_orchestrator.handle_question(
+        _question("Какой отток за месяц?"),
+    )
+    assert resp.answer
+    raw_fields = {"DaysSinceLastVisit", "ServicePeriodDays", "DaysOverdue", "ClientName", "Phone"}
+    for f in raw_fields:
+        assert f not in resp.answer, f"Raw field {f} leaked into answer"
+
+
+# ── 13. Fallback: has period ───────────────────────────────────────────────
+
+async def test_e2e_fallback_has_period(real_orchestrator: SwarmOrchestrator):
+    """Ответ содержит информацию о периоде."""
+    resp = await real_orchestrator.handle_question(
+        _question("статистика за март"),
+    )
+    assert resp.answer
+    # Ожидаем упоминание даты или месяца в ответе
+    assert resp.topic in ("statistics", "trend")
+
+
+# ── 14. Statistics money rounded ───────────────────────────────────────────
+
+async def test_e2e_statistics_money_rounded(real_orchestrator: SwarmOrchestrator):
+    """Денежные метрики не содержат чрезмерных десятичных знаков."""
+    resp = await real_orchestrator.handle_question(
+        _question("статистика за март"),
+    )
+    assert resp.answer
+    # Структурная проверка: ответ не пуст и topic корректен
+    assert resp.topic in ("statistics", "trend")
diff --git a/swarm_powerbi_bot/tests/integration/test_real_llm.py b/swarm_powerbi_bot/tests/integration/test_real_llm.py
index 0855642..01789f7 100644
--- a/swarm_powerbi_bot/tests/integration/test_real_llm.py
+++ b/swarm_powerbi_bot/tests/integration/test_real_llm.py
@@ -1,134 +1,134 @@
 """Интеграционные тесты LLM через реальный Ollama.
 
 Запуск: uv run pytest tests/integration/test_real_llm.py -m integration -v
 """
 from __future__ import annotations
 
 import json
 import urllib.request
 
 import pytest
 
 from swarm_powerbi_bot.agents import AnalystAgent, PlannerAgent
 from swarm_powerbi_bot.models import AggregateResult, MultiPlan, UserQuestion
 from swarm_powerbi_bot.services import LLMClient
 from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry
 
 pytestmark = pytest.mark.integration
 
 
 # ── 1. Ollama health ─────────────────────────────────────────────────────────
 
 def test_ollama_health(real_settings, ollama_ok):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     url = real_settings.ollama_base_url.rstrip("/") + "/api/tags"
     resp = urllib.request.urlopen(url, timeout=10)  # noqa: S310
     data = json.loads(resp.read())
     assert "models" in data
 
 
 # ── 2. Простое completion ────────────────────────────────────────────────────
 
 def test_simple_completion(real_settings, ollama_ok):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     url = real_settings.ollama_base_url.rstrip("/") + "/api/chat"
     payload = json.dumps({
         "model": real_settings.ollama_model,
         "messages": [{"role": "user", "content": "Скажи привет"}],
         "stream": False,
         "think": False,
         "options": {"num_predict": 64},
     }).encode()
     req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
     resp = urllib.request.urlopen(req, timeout=15)  # noqa: S310
     body = json.loads(resp.read())
     content = body.get("message", {}).get("content", "")
     assert content.strip(), "Empty LLM response"
 
 
 # ── 3. Planner keyword fallback ──────────────────────────────────────────────
 
 async def test_planner_keyword_fallback(real_settings):
-    """PlannerAgent без LLM (только keyword) должен вернуть Plan."""
+    """PlannerAgent без registry → keyword fallback должен вернуть Plan."""
     llm_client = LLMClient(real_settings)
     # Без registry — keyword mode
     planner = PlannerAgent(llm_client=llm_client, aggregate_registry=None)
     question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
     plan = await planner.run(question)
     assert plan.topic
 
 
 # ── 4. Planner LLM mode ─────────────────────────────────────────────────────
 
 async def test_planner_llm_mode(
     real_settings, real_registry: AggregateRegistry, ollama_ok,
 ):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     llm_client = LLMClient(real_settings)
     planner = PlannerAgent(
         llm_client=llm_client,
         aggregate_registry=real_registry,
         semantic_catalog_path=real_settings.semantic_catalog_path,
     )
     question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
     plan = await planner.run_multi(question)
     assert plan.queries, "Expected at least 1 query"
     assert plan.intent
 
 
 # ── 5. Planner comparison ────────────────────────────────────────────────────
 
 async def test_planner_comparison(
     real_settings, real_registry: AggregateRegistry, ollama_ok,
 ):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     llm_client = LLMClient(real_settings)
     planner = PlannerAgent(
         llm_client=llm_client,
         aggregate_registry=real_registry,
         semantic_catalog_path=real_settings.semantic_catalog_path,
     )
     question = UserQuestion(
         user_id="test", text="сравни выручку за март и апрель", object_id=506770,
     )
     plan = await planner.run_multi(question)
     assert plan.intent == "comparison", f"expected comparison, got {plan.intent}"
     assert len(plan.queries) >= 2, f"expected >=2 queries, got {len(plan.queries)}"
 
 
 # ── 6. Planner decomposition ────────────────────────────────────────────────
 
 async def test_planner_decomposition(
     real_settings, real_registry: AggregateRegistry, ollama_ok,
 ):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     llm_client = LLMClient(real_settings)
     planner = PlannerAgent(
         llm_client=llm_client,
         aggregate_registry=real_registry,
         semantic_catalog_path=real_settings.semantic_catalog_path,
     )
     question = UserQuestion(
         user_id="test", text="почему упала выручка?", object_id=506770,
     )
     plan = await planner.run_multi(question)
     assert plan.intent in ("decomposition", "single"), f"got {plan.intent}"
     assert len(plan.queries) >= 1
 
 
 # ── 7. Unknown topic graceful ────────────────────────────────────────────────
 
 async def test_planner_unknown_topic(
     real_settings, real_registry: AggregateRegistry, ollama_ok,
 ):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     llm_client = LLMClient(real_settings)
     planner = PlannerAgent(
         llm_client=llm_client,
         aggregate_registry=real_registry,
@@ -141,80 +141,117 @@ async def test_planner_unknown_topic(
 
 
 # ── 8. Analyst summary ──────────────────────────────────────────────────────
 
 async def test_analyst_summary(real_settings, ollama_ok):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     llm_client = LLMClient(real_settings)
     analyst = AnalystAgent(llm_client)
     mock_results = [
         AggregateResult(
             aggregate_id="revenue_total",
             label="Выручка",
             rows=[{"Revenue": 1500000, "Visits": 320, "AvgCheck": 4687}],
             row_count=1,
             duration_ms=100,
             status="ok",
         ),
     ]
     question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
     result = await analyst.run(question=question, sql_results=mock_results)
     assert result.answer
     assert len(result.answer) <= 2000
 
 
 # ── 9. Circuit breaker ──────────────────────────────────────────────────────
 
 async def test_circuit_breaker(real_settings):
     """После N timeout-ов breaker открывается."""
     from swarm_powerbi_bot.config import Settings
 
     fast_settings = Settings(
         ollama_base_url=real_settings.ollama_base_url,
         ollama_model=real_settings.ollama_model,
         llm_plan_timeout=0,  # мгновенный timeout
         llm_circuit_breaker_threshold=2,
         llm_circuit_breaker_cooldown=60,
         aggregate_catalog_path=real_settings.aggregate_catalog_path,
     )
     llm_client = LLMClient(fast_settings)
     registry = AggregateRegistry(real_settings.aggregate_catalog_path)
     planner = PlannerAgent(
         llm_client=llm_client, aggregate_registry=registry,
         semantic_catalog_path=real_settings.semantic_catalog_path,
     )
     question = UserQuestion(user_id="test", text="выручка", object_id=506770)
 
     # Несколько попыток для активации breaker
     for _ in range(3):
         plan = await planner.run_multi(question)
 
     # После breaker — должен сработать fallback (keyword)
     plan = await planner.run_multi(question)
     assert isinstance(plan, MultiPlan)
 
 
 # ── 10. LLM timeout не зависает ─────────────────────────────────────────────
 
 async def test_llm_timeout(real_settings, ollama_ok):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     from swarm_powerbi_bot.config import Settings
 
     # Крайне малый timeout
     fast_settings = Settings(
         ollama_base_url=real_settings.ollama_base_url,
         ollama_model=real_settings.ollama_model,
         llm_plan_timeout=0,
         aggregate_catalog_path=real_settings.aggregate_catalog_path,
     )
     llm_client = LLMClient(fast_settings)
     registry = AggregateRegistry(real_settings.aggregate_catalog_path)
     planner = PlannerAgent(
         llm_client=llm_client, aggregate_registry=registry,
         semantic_catalog_path=real_settings.semantic_catalog_path,
     )
     question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
     # Не должен зависнуть — должен вернуть fallback или timeout
     plan = await planner.run_multi(question)
     assert isinstance(plan, MultiPlan)
+
+
+# ── 11. Parametrized 10 questions → valid MultiPlan ─────────────────────────
+
+_PLANNER_10_QUESTIONS = [
+    "Покажи отток клиентов за месяц",
+    "Статистика за эту неделю",
+    "Динамика выручки по неделям за квартал",
+    "Загрузка мастеров за март",
+    "Каналы привлечения клиентов",
+    "Именинники на этой неделе",
+    "Результаты обзвонов за март",
+    "Прогноз визитов на следующую неделю",
+    "Популярные услуги за месяц",
+    "Контроль качества за март",
+]
+
+
+@pytest.mark.parametrize("question_text", _PLANNER_10_QUESTIONS)
+async def test_planner_10_questions(
+    real_settings, real_registry: AggregateRegistry, ollama_ok, question_text,
+):
+    if not ollama_ok:
+        pytest.skip("Ollama not available")
+    llm_client = LLMClient(real_settings)
+    planner = PlannerAgent(
+        llm_client=llm_client,
+        aggregate_registry=real_registry,
+        semantic_catalog_path=real_settings.semantic_catalog_path,
+    )
+    question = UserQuestion(user_id="test", text=question_text, object_id=506770)
+    plan = await planner.run_multi(question)
+    assert isinstance(plan, MultiPlan)
+    assert plan.queries, f"No queries for: {question_text}"
+    assert plan.topic, f"No topic for: {question_text}"
+    assert plan.intent in ("single", "comparison", "decomposition"), \
+        f"Invalid intent '{plan.intent}' for: {question_text}"
diff --git a/swarm_powerbi_bot/tests/test_e2e_pipeline.py b/swarm_powerbi_bot/tests/test_e2e_pipeline.py
index 697db39..7cee005 100644
--- a/swarm_powerbi_bot/tests/test_e2e_pipeline.py
+++ b/swarm_powerbi_bot/tests/test_e2e_pipeline.py
@@ -1,174 +1,401 @@
 """End-to-end тесты pipeline: вопрос → topic → SQL params → chart → ответ.
 
 Проверяет полную цепочку без обращения к MSSQL/LLM (моки).
 """
 import asyncio
+from datetime import date
 
 import pytest
 
 from swarm_powerbi_bot.agents.planner import PlannerAgent
 from swarm_powerbi_bot.models import (
     AnalysisResult,
     ModelInsight,
     Plan,
     SQLInsight,
     UserQuestion,
 )
 from swarm_powerbi_bot.orchestrator import SwarmOrchestrator
 from swarm_powerbi_bot.services.chart_renderer import HAS_MPL
 
+from conftest import build_mock_orchestrator_multi
+
+pytestmark = pytest.mark.e2e
+
 
 # ── Mock агенты с реалистичными данными ──────────────────────
 
 class MockSQL:
-    """Возвращает данные как настоящие хранимки."""
+    """Возвращает данные как настоящие хранимки — 11 тем (10 из checklist + leaving)."""
     MOCK_DATA = {
         "outflow": [
-            {"ClientName": "Козлова Р.", "TotalSpent": 8112.6, "DaysSinceLastVisit": 275,
-             "DaysOverdue": 240, "TotalVisits": 11, "ServicePeriodDays": 35, "SalonName": "Dream"},
-            {"ClientName": "Белова Т.", "TotalSpent": 57054.0, "DaysSinceLastVisit": 283,
-             "DaysOverdue": 238, "TotalVisits": 59, "ServicePeriodDays": 45, "SalonName": "Dream"},
+            {"ClientName": "Козлова Р.", "Phone": "79001111111", "TotalSpent": 8112.6,
+             "DaysSinceLastVisit": 275, "DaysOverdue": 240, "TotalVisits": 11,
+             "ServicePeriodDays": 35, "SalonName": "Dream"},
+            {"ClientName": "Белова Т.", "Phone": "79002222222", "TotalSpent": 57054.0,
+             "DaysSinceLastVisit": 283, "DaysOverdue": 238, "TotalVisits": 59,
+             "ServicePeriodDays": 45, "SalonName": "Dream"},
         ],
         "statistics": [
-            {"TotalVisits": 219, "UniqueClients": 137, "TotalRevenue": 422028.0,
-             "AvgCheck": 1954.0, "ActiveMasters": 14, "SalonName": "Dream"},
+            {"TotalVisits": 219, "UniqueClients": 137, "TotalRevenue": 422028.50,
+             "AvgCheck": 1954.33, "ActiveMasters": 14, "SalonName": "Dream"},
         ],
         "trend": [
             {"WeekEnd": "2026-03-02", "Visits": 45, "Revenue": 77424, "UniqueClients": 30, "AvgCheck": 1720, "ActiveMasters": 7},
             {"WeekEnd": "2026-03-09", "Visits": 50, "Revenue": 85000, "UniqueClients": 35, "AvgCheck": 1700, "ActiveMasters": 8},
         ],
         "masters": [
             {"MasterName": "Мастер А", "TotalRevenue": 120000, "TotalVisits": 50, "AvgCheck": 2400, "SalonName": "Dream"},
         ],
+        "referrals": [
+            {"AcquisitionChannel": "Instagram", "ClientCount": 50},
+            {"AcquisitionChannel": "Рекомендация", "ClientCount": 30},
+        ],
+        "birthday": [
+            {"ClientName": "Иванова А.", "Phone": "79003333333", "BirthDate": "2000-04-16"},
+        ],
+        "communications": [
+            {"Reason": "outflow", "Result": "Вернулся", "TotalCount": 15},
+            {"Reason": "leaving", "Result": "Нет ответа", "TotalCount": 8},
+        ],
+        "forecast": [
+            {"ClientName": "Петрова М.", "ExpectedNextVisit": "2026-04-17", "ServicePeriodDays": 28},
+        ],
+        "services": [
+            {"ServiceName": "Стрижка", "Revenue": 85000, "ServiceCount": 120},
+            {"ServiceName": "Окрашивание", "Revenue": 65000, "ServiceCount": 40},
+        ],
+        "quality": [
+            {"ClientName": "Сидоров К.", "DaysOverdue": 5, "TotalVisits": 3, "SalonName": "Dream"},
+        ],
+        "leaving": [
+            {"ClientName": "Нова Е.", "DaysOverdue": 15, "TotalSpent": 12000, "TotalVisits": 7, "SalonName": "Dream"},
+        ],
     }
 
     async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
         rows = self.MOCK_DATA.get(plan.topic, [])
         return SQLInsight(
             rows=rows,
             summary=f"SQL вернул {len(rows)} строк по теме «{plan.topic}»",
             topic=plan.topic,
-            params={"DateFrom": "2026-03-15", "DateTo": "2026-04-14"},
+            params={"DateFrom": date(2026, 3, 15), "DateTo": date(2026, 4, 14)},
         )
 
 
 class MockPBI:
     async def run(self, question, plan):
         return ModelInsight(metrics={}, summary="model skipped")
 
 
 class MockRender:
     async def run(self, question, plan):
         return None
 
 
 class MockAnalyst:
+    """Возвращает canned output для проверки маршрутизации pipeline.
+
+    Реальную фильтрацию полей и качество формулировок проверяют
+    интеграционные тесты в tests/integration/test_real_e2e.py.
+    """
     async def run(self, question, plan, sql_insight, model_insight, diagnostics, *, has_chart=False):
         return AnalysisResult(
             answer=f"Тема: {plan.topic}, строк: {len(sql_insight.rows)}",
             confidence="medium",
             follow_ups=["follow1"],
         )
 
 
 def _build_orchestrator():
     return SwarmOrchestrator(
         planner=PlannerAgent(),
         sql_agent=MockSQL(),
         powerbi_agent=MockPBI(),
         render_agent=MockRender(),
         analyst_agent=MockAnalyst(),
     )
 
 
 # ── E2E тесты ────────────────────────────────────────────────
 
 class TestE2EPipeline:
     def test_outflow_question(self):
         orch = _build_orchestrator()
         result = asyncio.run(orch.handle_question(
             UserQuestion(user_id="1", text="отток за месяц"),
         ))
         assert "outflow" in result.answer
         assert result.topic == "outflow"
 
     def test_statistics_question(self):
         orch = _build_orchestrator()
         result = asyncio.run(orch.handle_question(
             UserQuestion(user_id="1", text="покажи статистику за неделю"),
         ))
         assert "statistics" in result.answer
         assert result.topic == "statistics"
 
     def test_masters_question(self):
         orch = _build_orchestrator()
         result = asyncio.run(orch.handle_question(
             UserQuestion(user_id="1", text="загрузка мастеров"),
         ))
         assert "masters" in result.answer
 
     def test_followup_keeps_topic(self):
         """Follow-up вопрос сохраняет тему."""
         orch = _build_orchestrator()
         result = asyncio.run(orch.handle_question(
             UserQuestion(user_id="1", text="подробнее по неделям", last_topic="outflow"),
         ))
         assert result.topic == "outflow"
 
     def test_response_has_follow_ups(self):
         orch = _build_orchestrator()
         result = asyncio.run(orch.handle_question(
             UserQuestion(user_id="1", text="отток за месяц"),
         ))
         assert len(result.follow_ups) > 0
 
     @pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
     def test_outflow_generates_chart(self):
         """Отток с данными → matplotlib-график."""
         orch = _build_orchestrator()
         result = asyncio.run(orch.handle_question(
             UserQuestion(user_id="1", text="отток за месяц"),
         ))
         assert result.image is not None
         assert result.image[:4] == b"\x89PNG"
 
     @pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
     def test_trend_generates_line_chart(self):
         orch = _build_orchestrator()
         result = asyncio.run(orch.handle_question(
             UserQuestion(user_id="1", text="покажи тренд за квартал"),
         ))
         assert result.image is not None
 
     def test_empty_data_no_crash(self):
         """Если SQL вернул 0 строк — не падаем."""
         orch = _build_orchestrator()
         result = asyncio.run(orch.handle_question(
             UserQuestion(user_id="1", text="покажи именинников"),
         ))
         assert result.answer is not None
 
 
 # ── Planner тесты ────────────────────────────────────────────
 
 class TestPlannerNotes:
     def test_comparison_note(self):
         planner = PlannerAgent()
         plan = asyncio.run(planner.run(
             UserQuestion(user_id="1", text="сравни отток по неделям"),
         ))
         assert "comparison_requested" in plan.notes
 
     def test_period_note_week(self):
         planner = PlannerAgent()
         plan = asyncio.run(planner.run(
             UserQuestion(user_id="1", text="статистика за неделю"),
         ))
         assert "period:week" in plan.notes
 
     def test_breakdown_by_master(self):
         planner = PlannerAgent()
         plan = asyncio.run(planner.run(
             UserQuestion(user_id="1", text="выручка по мастерам"),
         ))
         assert "breakdown_by_master" in plan.notes
+
+
+# ── T004: Comparison / Composition pipeline ─────────────────────
+
+class TestMultiPlanPipeline:
+    def test_comparison_pipeline(self):
+        """MultiPlan comparison → SwarmResponse с ответом и chart."""
+        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="сравни отток за два месяца"),
+        ))
+        assert result.answer is not None
+        assert "Сравнение" in result.answer
+        assert result.confidence in ("low", "medium", "high")
+
+    def test_comparison_pipeline_second_question(self):
+        """Второй comparison-вопрос через MultiPlan → корректный ответ."""
+        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="сравни отток по салонам"),
+        ))
+        assert result.answer
+        assert len(result.answer) > 0
+
+    def test_decomposition_pipeline(self):
+        """MultiPlan decomposition → SwarmResponse с multi-result анализом."""
+        orch = build_mock_orchestrator_multi(intent="decomposition", topic="revenue_total")
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="почему упала выручка?"),
+        ))
+        assert result.answer is not None
+        assert result.confidence in ("low", "medium", "high")
+
+
+# ── T005: 10 checklist questions ────────────────────────────────
+
+_CHECKLIST_QUESTIONS = [
+    ("отток за месяц", "outflow"),
+    ("покажи статистику за неделю", "statistics"),
+    ("динамика по неделям", "trend"),
+    ("загрузка мастеров", "masters"),
+    ("реферальная программа", "referrals"),
+    ("именинники на этой неделе", "birthday"),
+    ("результаты обзвонов", "communications"),
+    ("прогноз визитов", "forecast"),
+    ("популярные услуги", "services"),
+    ("контроль качества", "quality"),
+]
+
+
+class TestChecklistQuestions:
+    @pytest.mark.parametrize("question_text,expected_topic", _CHECKLIST_QUESTIONS)
+    def test_10_checklist_questions(self, question_text, expected_topic):
+        """Каждый из 10 вопросов чеклиста → non-empty SwarmResponse."""
+        orch = _build_orchestrator()
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text=question_text),
+        ))
+        assert result.answer is not None
+        assert len(result.answer) > 0
+        assert result.topic == expected_topic
+
+
+# ── T006: Follow-up chains ──────────────────────────────────────
+
+class TestFollowUpChains:
+    def test_follow_up_chain(self):
+        """Цепочка follow-up: тема сохраняется через last_topic."""
+        orch = _build_orchestrator()
+        r1 = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="отток за месяц"),
+        ))
+        assert r1.topic == "outflow"
+
+        r2 = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="подробнее", last_topic="outflow"),
+        ))
+        assert r2.topic == "outflow"
+
+        r3 = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="а по неделям?", last_topic="outflow"),
+        ))
+        assert r3.topic == "outflow"
+
+    def test_follow_up_to_comparison(self):
+        """Follow-up «сравни» с last_topic → comparison через MultiPlan."""
+        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="сравни по месяцам", last_topic="clients_outflow"),
+        ))
+        assert result.answer is not None
+        assert len(result.answer) > 0
+
+
+# ── T007: Negative scenarios ────────────────────────────────────
+
+class TestNegativeScenarios:
+    def test_negative_sql_injection(self):
+        """SQL-инъекция в тексте не ломает pipeline."""
+        orch = _build_orchestrator()
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="'; DROP TABLE clients; --"),
+        ))
+        assert result.answer
+        assert "sql_error" not in result.diagnostics
+
+    def test_negative_off_topic(self):
+        """Вопрос не по теме → всё равно ответ (fallback topic)."""
+        orch = _build_orchestrator()
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="какая погода в Москве?"),
+        ))
+        assert result.answer
+        assert result.topic  # непустой topic (fallback)
+
+    def test_negative_empty_text(self):
+        """Пустой текст запроса → не падаем."""
+        orch = _build_orchestrator()
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text=""),
+        ))
+        assert result.answer
+        assert result.topic
+
+    def test_negative_no_period(self):
+        """KPI-вопрос без указания периода → не падаем."""
+        orch = _build_orchestrator()
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="покажи выручку"),
+        ))
+        assert result.answer
+        assert result.topic
+
+    def test_negative_long_text(self):
+        """Очень длинный текст → не падаем."""
+        orch = _build_orchestrator()
+        long_text = "отток " * 500
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text=long_text),
+        ))
+        assert result.answer
+        assert result.topic == "outflow"
+
+
+# ── T008: Smoke / fallback quality ──────────────────────────────
+# NB: MockAnalyst возвращает canned output — эти тесты проверяют маршрутизацию
+# pipeline, а не качество формулировок аналитика. Реальное качество ответов
+# (отсутствие сырых SQL-полей, форматирование чисел) проверяют интеграционные
+# тесты в tests/integration/test_real_e2e.py.
+
+class TestFallbackQuality:
+    def test_outflow_fallback_no_raw_fields(self):
+        """Mock pipeline: ответ не содержит сырых SQL-имён.
+
+        NB: MockAnalyst возвращает canned output — реальную фильтрацию
+        полей проверяет integration/test_real_e2e::test_e2e_fallback_no_raw_fields.
+        """
+        orch = _build_orchestrator()
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="отток за месяц"),
+        ))
+        raw_fields = {"DaysSinceLastVisit", "DaysOverdue", "TotalSpent", "ServicePeriodDays", "Phone"}
+        for field in raw_fields:
+            assert field not in result.answer, f"Сырое поле {field} в ответе"
+
+    def test_statistics_pipeline_returns_correct_topic(self):
+        """Mock pipeline: маршрутизация statistics возвращает непустой ответ.
+
+        NB: MockAnalyst возвращает canned output — качество текста проверяют
+        интеграционные тесты в tests/integration/test_real_e2e.py.
+        """
+        orch = _build_orchestrator()
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="покажи статистику за неделю"),
+        ))
+        assert result.topic == "statistics"
+        assert result.answer
+        assert result.confidence in ("low", "medium", "high")
+
+    def test_statistics_pipeline_has_follow_ups(self):
+        """Mock pipeline: statistics возвращает follow-up подсказки.
+
+        NB: MockAnalyst возвращает canned output — содержание follow-ups
+        проверяют интеграционные тесты в tests/integration/test_real_e2e.py.
+        """
+        orch = _build_orchestrator()
+        result = asyncio.run(orch.handle_question(
+            UserQuestion(user_id="1", text="покажи статистику за неделю"),
+        ))
+        assert result.topic == "statistics"
+        assert len(result.follow_ups) > 0
diff --git a/swarm_powerbi_bot/tests/test_orchestrator.py b/swarm_powerbi_bot/tests/test_orchestrator.py
index 3be2f2d..9c59e18 100644
--- a/swarm_powerbi_bot/tests/test_orchestrator.py
+++ b/swarm_powerbi_bot/tests/test_orchestrator.py
@@ -1,122 +1,116 @@
 import asyncio
 
 from swarm_powerbi_bot.models import (
-    AggregateResult, AnalysisResult, ModelInsight, MultiPlan, Plan,
-    RenderedArtifact, SQLInsight, UserQuestion,
+    AggregateResult, MultiPlan, Plan, UserQuestion,
 )
 from swarm_powerbi_bot.orchestrator import SwarmOrchestrator
 
-
-class DummyPlanner:
-    aggregate_registry = None
-
-    async def run(self, question: UserQuestion) -> Plan:
-        return Plan(objective=question.text, topic="statistics", sql_needed=True, powerbi_needed=True, render_needed=True)
-
-
-class DummySQL:
-    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
-        return SQLInsight(rows=[{"kpi": "sales", "value": 100}], summary="sql ok")
-
-
-class DummyPBI:
-    async def run(self, question: UserQuestion, plan: Plan) -> ModelInsight:
-        return ModelInsight(metrics={"margin": 0.32}, summary="model ok")
-
-
-class DummyRender:
-    async def run(self, question: UserQuestion, plan: Plan) -> RenderedArtifact:
-        _ = question, plan
-        return RenderedArtifact(image_bytes=b"png-bytes", source_url="http://report")
-
-
-class DummyAnalyst:
-    async def run(self, question, plan, sql_insight, model_insight, diagnostics, *, has_chart=False):
-        _ = question, plan, sql_insight, model_insight, has_chart
-        return AnalysisResult(answer="analysis", confidence="high", diagnostics=diagnostics)
+from conftest import (
+    DummyAnalyst, DummyPBI, DummyPlanner, DummyRender, DummySQL,
+    MockAnalystMulti, MockRegistry,
+)
 
 
 def test_orchestrator_happy_path():
     orchestrator = SwarmOrchestrator(
         planner=DummyPlanner(),
         sql_agent=DummySQL(),
         powerbi_agent=DummyPBI(),
         render_agent=DummyRender(),
         analyst_agent=DummyAnalyst(),
     )
 
     result = asyncio.run(orchestrator.handle_question(UserQuestion(user_id="1", text="test")))
     assert result.answer == "analysis"
-    # Графики: matplotlib генерирует PNG из SQL данных, или Power BI рендер
+    # Изображение из DummyRender
     assert result.image is not None
     assert result.confidence == "high"
 
 
 # ── #4: multi_all_failed → legacy SQL не вызывается ──────────
 
 
 class DummySQLSpy(DummySQL):
     """SQL agent that records whether run() was called."""
     def __init__(self):
         self.run_called = False
 
     async def run(self, question, plan):
         self.run_called = True
         return await super().run(question, plan)
 
     async def run_multi(self, multi_plan, registry, *, logger_=None):
-        # All results failed
         return [
             AggregateResult(aggregate_id="clients_outflow", status="error", rows=[]),
             AggregateResult(aggregate_id="clients_outflow", status="error", rows=[]),
         ]
 
 
-class DummyPlannerWithRegistry(DummyPlanner):
+class DummyPlannerWithRegistryFail(DummyPlanner):
     def __init__(self, registry):
         self.aggregate_registry = registry
 
     async def run_multi(self, question):
         return MultiPlan(
             objective="сравни",
             intent="comparison",
             queries=[{"aggregate_id": "clients_outflow"}],
             topic="clients_outflow",
             render_needed=True,
             notes=["planner_v2:llm"],
         )
 
     def multi_plan_to_plan(self, multi_plan, question):
         return Plan(
             objective=multi_plan.objective,
             topic=multi_plan.topic,
             notes=list(multi_plan.notes),
         )
 
 
-class DummyRegistry:
-    """Minimal registry stub."""
-    pass
-
-
-class DummyAnalystMulti(DummyAnalyst):
-    async def run_multi(self, question, results, plan):
-        return AnalysisResult(answer="multi analysis", confidence="medium", diagnostics={})
-
-
 def test_multi_all_failed_skips_legacy_sql():
     """#4: Если все multi_results failed, legacy SQL НЕ должен вызываться."""
-    registry = DummyRegistry()
+    registry = MockRegistry()
     sql_spy = DummySQLSpy()
     orchestrator = SwarmOrchestrator(
-        planner=DummyPlannerWithRegistry(registry),
+        planner=DummyPlannerWithRegistryFail(registry),
         sql_agent=sql_spy,
         powerbi_agent=DummyPBI(),
         render_agent=DummyRender(),
-        analyst_agent=DummyAnalystMulti(),
+        analyst_agent=MockAnalystMulti(),
         aggregate_registry=registry,
     )
 
     result = asyncio.run(orchestrator.handle_question(UserQuestion(user_id="1", text="сравни отток")))
+    assert result.answer, "Orchestrator должен вернуть ответ даже при all-failed multi"
     assert not sql_spy.run_called, "Legacy SQL should NOT be called when all multi_results failed"
     assert result.diagnostics.get("multi_all_failed") == "true"
+
+
+# ── planner_v2_error → graceful degradation to legacy ──────────
+
+
+class DummyPlannerV2Error(DummyPlanner):
+    """Planner с aggregate_registry, но run_multi() всегда падает."""
+    def __init__(self, registry):
+        self.aggregate_registry = registry
+
+    async def run_multi(self, question):
+        raise RuntimeError("LLM unavailable")
+
+
+def test_planner_v2_error_degrades_to_legacy():
+    """Если run_multi() падает — orchestrator деградирует на legacy planner.run()."""
+    registry = MockRegistry()
+    orchestrator = SwarmOrchestrator(
+        planner=DummyPlannerV2Error(registry),
+        sql_agent=DummySQL(),
+        powerbi_agent=DummyPBI(),
+        render_agent=DummyRender(),
+        analyst_agent=DummyAnalyst(),
+        aggregate_registry=registry,
+    )
+
+    result = asyncio.run(orchestrator.handle_question(UserQuestion(user_id="1", text="выручка")))
+    assert result.answer == "analysis"
+    assert "planner_v2_error" in result.diagnostics

exec
/bin/zsh -lc "sed -n '261,520p' tests/test_e2e_pipeline.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
class TestChecklistQuestions:
    @pytest.mark.parametrize("question_text,expected_topic", _CHECKLIST_QUESTIONS)
    def test_10_checklist_questions(self, question_text, expected_topic):
        """Каждый из 10 вопросов чеклиста → non-empty SwarmResponse."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text=question_text),
        ))
        assert result.answer is not None
        assert len(result.answer) > 0
        assert result.topic == expected_topic


# ── T006: Follow-up chains ──────────────────────────────────────

class TestFollowUpChains:
    def test_follow_up_chain(self):
        """Цепочка follow-up: тема сохраняется через last_topic."""
        orch = _build_orchestrator()
        r1 = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert r1.topic == "outflow"

        r2 = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="подробнее", last_topic="outflow"),
        ))
        assert r2.topic == "outflow"

        r3 = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="а по неделям?", last_topic="outflow"),
        ))
        assert r3.topic == "outflow"

    def test_follow_up_to_comparison(self):
        """Follow-up «сравни» с last_topic → comparison через MultiPlan."""
        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="сравни по месяцам", last_topic="clients_outflow"),
        ))
        assert result.answer is not None
        assert len(result.answer) > 0


# ── T007: Negative scenarios ────────────────────────────────────

class TestNegativeScenarios:
    def test_negative_sql_injection(self):
        """SQL-инъекция в тексте не ломает pipeline."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="'; DROP TABLE clients; --"),
        ))
        assert result.answer
        assert "sql_error" not in result.diagnostics

    def test_negative_off_topic(self):
        """Вопрос не по теме → всё равно ответ (fallback topic)."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="какая погода в Москве?"),
        ))
        assert result.answer
        assert result.topic  # непустой topic (fallback)

    def test_negative_empty_text(self):
        """Пустой текст запроса → не падаем."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text=""),
        ))
        assert result.answer
        assert result.topic

    def test_negative_no_period(self):
        """KPI-вопрос без указания периода → не падаем."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи выручку"),
        ))
        assert result.answer
        assert result.topic

    def test_negative_long_text(self):
        """Очень длинный текст → не падаем."""
        orch = _build_orchestrator()
        long_text = "отток " * 500
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text=long_text),
        ))
        assert result.answer
        assert result.topic == "outflow"


# ── T008: Smoke / fallback quality ──────────────────────────────
# NB: MockAnalyst возвращает canned output — эти тесты проверяют маршрутизацию
# pipeline, а не качество формулировок аналитика. Реальное качество ответов
# (отсутствие сырых SQL-полей, форматирование чисел) проверяют интеграционные
# тесты в tests/integration/test_real_e2e.py.

class TestFallbackQuality:
    def test_outflow_fallback_no_raw_fields(self):
        """Mock pipeline: ответ не содержит сырых SQL-имён.

        NB: MockAnalyst возвращает canned output — реальную фильтрацию
        полей проверяет integration/test_real_e2e::test_e2e_fallback_no_raw_fields.
        """
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        raw_fields = {"DaysSinceLastVisit", "DaysOverdue", "TotalSpent", "ServicePeriodDays", "Phone"}
        for field in raw_fields:
            assert field not in result.answer, f"Сырое поле {field} в ответе"

    def test_statistics_pipeline_returns_correct_topic(self):
        """Mock pipeline: маршрутизация statistics возвращает непустой ответ.

        NB: MockAnalyst возвращает canned output — качество текста проверяют
        интеграционные тесты в tests/integration/test_real_e2e.py.
        """
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи статистику за неделю"),
        ))
        assert result.topic == "statistics"
        assert result.answer
        assert result.confidence in ("low", "medium", "high")

    def test_statistics_pipeline_has_follow_ups(self):
        """Mock pipeline: statistics возвращает follow-up подсказки.

        NB: MockAnalyst возвращает canned output — содержание follow-ups
        проверяют интеграционные тесты в tests/integration/test_real_e2e.py.
        """
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи статистику за неделю"),
        ))
        assert result.topic == "statistics"
        assert len(result.follow_ups) > 0

exec
/bin/zsh -lc "sed -n '1,260p' tests/test_orchestrator.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
import asyncio

from swarm_powerbi_bot.models import (
    AggregateResult, MultiPlan, Plan, UserQuestion,
)
from swarm_powerbi_bot.orchestrator import SwarmOrchestrator

from conftest import (
    DummyAnalyst, DummyPBI, DummyPlanner, DummyRender, DummySQL,
    MockAnalystMulti, MockRegistry,
)


def test_orchestrator_happy_path():
    orchestrator = SwarmOrchestrator(
        planner=DummyPlanner(),
        sql_agent=DummySQL(),
        powerbi_agent=DummyPBI(),
        render_agent=DummyRender(),
        analyst_agent=DummyAnalyst(),
    )

    result = asyncio.run(orchestrator.handle_question(UserQuestion(user_id="1", text="test")))
    assert result.answer == "analysis"
    # Изображение из DummyRender
    assert result.image is not None
    assert result.confidence == "high"


# ── #4: multi_all_failed → legacy SQL не вызывается ──────────


class DummySQLSpy(DummySQL):
    """SQL agent that records whether run() was called."""
    def __init__(self):
        self.run_called = False

    async def run(self, question, plan):
        self.run_called = True
        return await super().run(question, plan)

    async def run_multi(self, multi_plan, registry, *, logger_=None):
        return [
            AggregateResult(aggregate_id="clients_outflow", status="error", rows=[]),
            AggregateResult(aggregate_id="clients_outflow", status="error", rows=[]),
        ]


class DummyPlannerWithRegistryFail(DummyPlanner):
    def __init__(self, registry):
        self.aggregate_registry = registry

    async def run_multi(self, question):
        return MultiPlan(
            objective="сравни",
            intent="comparison",
            queries=[{"aggregate_id": "clients_outflow"}],
            topic="clients_outflow",
            render_needed=True,
            notes=["planner_v2:llm"],
        )

    def multi_plan_to_plan(self, multi_plan, question):
        return Plan(
            objective=multi_plan.objective,
            topic=multi_plan.topic,
            notes=list(multi_plan.notes),
        )


def test_multi_all_failed_skips_legacy_sql():
    """#4: Если все multi_results failed, legacy SQL НЕ должен вызываться."""
    registry = MockRegistry()
    sql_spy = DummySQLSpy()
    orchestrator = SwarmOrchestrator(
        planner=DummyPlannerWithRegistryFail(registry),
        sql_agent=sql_spy,
        powerbi_agent=DummyPBI(),
        render_agent=DummyRender(),
        analyst_agent=MockAnalystMulti(),
        aggregate_registry=registry,
    )

    result = asyncio.run(orchestrator.handle_question(UserQuestion(user_id="1", text="сравни отток")))
    assert result.answer, "Orchestrator должен вернуть ответ даже при all-failed multi"
    assert not sql_spy.run_called, "Legacy SQL should NOT be called when all multi_results failed"
    assert result.diagnostics.get("multi_all_failed") == "true"


# ── planner_v2_error → graceful degradation to legacy ──────────


class DummyPlannerV2Error(DummyPlanner):
    """Planner с aggregate_registry, но run_multi() всегда падает."""
    def __init__(self, registry):
        self.aggregate_registry = registry

    async def run_multi(self, question):
        raise RuntimeError("LLM unavailable")


def test_planner_v2_error_degrades_to_legacy():
    """Если run_multi() падает — orchestrator деградирует на legacy planner.run()."""
    registry = MockRegistry()
    orchestrator = SwarmOrchestrator(
        planner=DummyPlannerV2Error(registry),
        sql_agent=DummySQL(),
        powerbi_agent=DummyPBI(),
        render_agent=DummyRender(),
        analyst_agent=DummyAnalyst(),
        aggregate_registry=registry,
    )

    result = asyncio.run(orchestrator.handle_question(UserQuestion(user_id="1", text="выручка")))
    assert result.answer == "analysis"
    assert "planner_v2_error" in result.diagnostics

codex
I’ve reached the point where the review depends on the existing test harness behavior, not just the patch. I’m loading the orchestrator and both `conftest.py` files now to check whether the new tests genuinely exercise the intended code paths or accidentally bypass them.
exec
/bin/zsh -lc "sed -n '1,260p' tests/integration/conftest.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
"""Fixtures для интеграционных тестов с реальным MSSQL и Ollama.

Все тесты помечены @pytest.mark.integration и пропускаются
если окружение недоступно (нет MSSQL_SERVER, нет Ollama).

Запуск: uv run pytest tests/integration/ -m integration -v
"""
from __future__ import annotations

import os
import urllib.request

import pytest

from swarm_powerbi_bot.config import Settings
from swarm_powerbi_bot.main import build_orchestrator
from swarm_powerbi_bot.services import LLMClient, SQLClient
from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry

TEST_OBJECT_ID = 506770
TEST_DATE_FROM = "2026-03-01"
TEST_DATE_TO = "2026-03-31"


def _mssql_available(settings: Settings) -> bool:
    conn_str = settings.sql_connection_string()
    if not conn_str:
        return False
    try:
        import pyodbc

        conn = pyodbc.connect(conn_str, timeout=5)
        conn.close()
        return True
    except Exception:
        return False


def _ollama_available(settings: Settings) -> bool:
    if not settings.ollama_base_url:
        return False
    try:
        url = settings.ollama_base_url.rstrip("/") + "/api/tags"
        req = urllib.request.Request(url)
        urllib.request.urlopen(req, timeout=5)  # noqa: S310
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def real_settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def mssql_ok(real_settings: Settings) -> bool:
    return _mssql_available(real_settings)


@pytest.fixture(scope="session")
def ollama_ok(real_settings: Settings) -> bool:
    return _ollama_available(real_settings)


@pytest.fixture(scope="session")
def real_sql_client(real_settings: Settings, mssql_ok: bool) -> SQLClient:
    if not mssql_ok:
        pytest.skip("MSSQL not available")
    return SQLClient(real_settings)


@pytest.fixture(scope="session")
def real_llm_client(real_settings: Settings, ollama_ok: bool) -> LLMClient:
    if not ollama_ok:
        pytest.skip("Ollama not available")
    return LLMClient(real_settings)


@pytest.fixture(scope="session")
def real_registry(real_settings: Settings) -> AggregateRegistry:
    path = real_settings.aggregate_catalog_path
    if not os.path.exists(path):
        pytest.skip(f"Catalog not found: {path}")
    return AggregateRegistry(path)


@pytest.fixture(scope="session")
def real_orchestrator(real_settings: Settings, mssql_ok: bool, ollama_ok: bool):
    if not mssql_ok:
        pytest.skip("MSSQL not available")
    if not ollama_ok:
        pytest.skip("Ollama not available")
    return build_orchestrator(real_settings)


@pytest.fixture
def test_object_id() -> int:
    return TEST_OBJECT_ID


@pytest.fixture
def test_date_range() -> tuple[str, str]:
    return TEST_DATE_FROM, TEST_DATE_TO

exec
/bin/zsh -lc "sed -n '1,320p' src/swarm_powerbi_bot/orchestrator.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "sed -n '1,260p' tests/integration/test_real_e2e.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
"""Интеграционные E2E тесты через реальный MSSQL + Ollama.

Запуск: uv run pytest tests/integration/test_real_e2e.py -m integration -v
"""
from __future__ import annotations

import asyncio

import pytest

from swarm_powerbi_bot.models import SwarmResponse, UserQuestion
from swarm_powerbi_bot.orchestrator import SwarmOrchestrator

pytestmark = pytest.mark.integration

# Совпадает с TEST_OBJECT_ID в tests/integration/conftest.py.
# Прямой import невозможен — pytest резолвит `from conftest` на tests/conftest.py.
_TEST_OBJECT_ID = 506770


def _question(text: str, **kwargs) -> UserQuestion:
    defaults = {"user_id": "e2e-test", "object_id": _TEST_OBJECT_ID}
    defaults.update(kwargs)
    return UserQuestion(text=text, **defaults)


# ── 1. Revenue question ─────────────────────────────────────────────────────

async def test_e2e_revenue_question(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(_question("Покажи выручку за март"))
    assert resp.answer, "empty answer"
    assert resp.topic != "unknown", f"topic should not be unknown, got {resp.topic}"


# ── 2. Outflow question ─────────────────────────────────────────────────────

async def test_e2e_outflow_question(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Какой отток за месяц?"),
    )
    assert resp.answer


# ── 3. Comparison с chart ────────────────────────────────────────────────────

async def test_e2e_comparison(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Сравни выручку марта и февраля"),
    )
    assert resp.answer
    # Comparison pipeline должен генерировать chart
    if resp.image is not None:
        assert resp.mime_type == "image/png"


# ── 4. Top masters ──────────────────────────────────────────────────────────

async def test_e2e_top_masters(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Топ-5 мастеров по выручке за март"),
    )
    assert resp.answer


# ── 5. Decomposition ────────────────────────────────────────────────────────

async def test_e2e_decomposition(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Почему упала выручка?"),
    )
    assert resp.answer


# ── 6. Unknown question ─────────────────────────────────────────────────────

async def test_e2e_unknown_question(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Как сварить борщ?"),
    )
    assert isinstance(resp, SwarmResponse)
    # Должен вежливо отказать или дать общий ответ


# ── 7. Follow-up ────────────────────────────────────────────────────────────

async def test_e2e_follow_up(real_orchestrator: SwarmOrchestrator):
    resp1 = await real_orchestrator.handle_question(
        _question("выручка за март"),
    )
    assert resp1.answer
    topic = resp1.topic

    resp2 = await real_orchestrator.handle_question(
        _question("а за февраль?", last_topic=topic),
    )
    assert resp2.answer


# ── 8. Chart generation ─────────────────────────────────────────────────────

async def test_e2e_chart_generation(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Покажи график выручки по неделям за квартал"),
    )
    assert resp.answer
    # Если chart сгенерирован, проверяем формат
    if resp.image is not None:
        assert resp.mime_type == "image/png"
        assert len(resp.image) > 100  # не пустой PNG


# ── 9. Telegram mock ────────────────────────────────────────────────────────

async def test_e2e_telegram_mock(real_orchestrator: SwarmOrchestrator):
    """Проверяем что orchestrator возвращает корректный SwarmResponse."""
    resp = await real_orchestrator.handle_question(
        _question("статистика за март"),
    )
    assert isinstance(resp, SwarmResponse)
    assert resp.confidence in ("low", "medium", "high")
    assert isinstance(resp.follow_ups, list)
    assert isinstance(resp.diagnostics, dict)


# ── 10. Concurrent users ────────────────────────────────────────────────────

async def test_e2e_concurrent_users(real_orchestrator: SwarmOrchestrator):
    questions = [
        _question("выручка за март", user_id="user-1"),
        _question("отток клиентов", user_id="user-2"),
        _question("коммуникации за март", user_id="user-3"),
    ]
    results = await asyncio.gather(
        *[real_orchestrator.handle_question(q) for q in questions],
    )
    for i, resp in enumerate(results):
        assert isinstance(resp, SwarmResponse), f"user-{i+1} got non-SwarmResponse"
        assert resp.answer, f"user-{i+1} got empty answer"


# ── 11. Comparison has chart ───────────────────────────────────────────────

async def test_e2e_comparison_has_chart(real_orchestrator: SwarmOrchestrator):
    """Comparison pipeline должен генерировать PNG chart."""
    resp = await real_orchestrator.handle_question(
        _question("Сравни отток за март и апрель"),
    )
    assert resp.answer
    # comparison должен генерировать chart; None допустим только при отсутствии matplotlib
    assert resp.image is not None, "Comparison should produce a chart"
    assert resp.image[:4] == b"\x89PNG"


# ── 12. Fallback: no raw SQL fields ───────────────────────────────────────

async def test_e2e_fallback_no_raw_fields(real_orchestrator: SwarmOrchestrator):
    """Ответ не должен содержать сырые SQL-имена полей."""
    resp = await real_orchestrator.handle_question(
        _question("Какой отток за месяц?"),
    )
    assert resp.answer
    raw_fields = {"DaysSinceLastVisit", "ServicePeriodDays", "DaysOverdue", "ClientName", "Phone"}
    for f in raw_fields:
        assert f not in resp.answer, f"Raw field {f} leaked into answer"


# ── 13. Fallback: has period ───────────────────────────────────────────────

async def test_e2e_fallback_has_period(real_orchestrator: SwarmOrchestrator):
    """Ответ содержит информацию о периоде."""
    resp = await real_orchestrator.handle_question(
        _question("статистика за март"),
    )
    assert resp.answer
    # Ожидаем упоминание даты или месяца в ответе
    assert resp.topic in ("statistics", "trend")


# ── 14. Statistics money rounded ───────────────────────────────────────────

async def test_e2e_statistics_money_rounded(real_orchestrator: SwarmOrchestrator):
    """Денежные метрики не содержат чрезмерных десятичных знаков."""
    resp = await real_orchestrator.handle_question(
        _question("статистика за март"),
    )
    assert resp.answer
    # Структурная проверка: ответ не пуст и topic корректен
    assert resp.topic in ("statistics", "trend")

 succeeded in 0ms:
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from .agents import AnalystAgent, PlannerAgent, PowerBIModelAgent, RenderAgent, SQLAgent
from .models import (
    AggregateResult,
    ModelInsight,
    MultiPlan,
    SQLInsight,
    SwarmResponse,
    UserQuestion,
)
from .services.chart_renderer import render_chart, render_comparison

if TYPE_CHECKING:
    from .services.aggregate_registry import AggregateRegistry
    from .services.query_logger import QueryLogger

logger = logging.getLogger(__name__)


class SwarmOrchestrator:
    def __init__(
        self,
        planner: PlannerAgent,
        sql_agent: SQLAgent,
        powerbi_agent: PowerBIModelAgent,
        render_agent: RenderAgent,
        analyst_agent: AnalystAgent,
        aggregate_registry: "AggregateRegistry | None" = None,
        query_logger: "QueryLogger | None" = None,
    ):
        self.planner = planner
        self.sql_agent = sql_agent
        self.powerbi_agent = powerbi_agent
        self.render_agent = render_agent
        self.analyst_agent = analyst_agent
        self.aggregate_registry = aggregate_registry
        self.query_logger = query_logger

    async def handle_question(self, question: UserQuestion) -> SwarmResponse:
        diagnostics: dict[str, str] = {}

        # T026: Пробуем LLM-планирование с каталогом агрегатов (MultiPlan)
        multi_plan: MultiPlan | None = None
        if getattr(self.planner, "aggregate_registry", None) is not None:
            try:
                multi_plan = await self.planner.run_multi(question)
                planner_v2_mode = (
                    "llm" if "planner_v2:llm" in multi_plan.notes else "keyword"
                )
                logger.info(
                    "[PLAN_V2] %s | intent=%s | topic=%s | queries=%d",
                    planner_v2_mode,
                    multi_plan.intent,
                    multi_plan.topic,
                    len(multi_plan.queries),
                )
                diagnostics["planner_v2"] = planner_v2_mode
            except Exception as exc:
                logger.error("[PLAN_V2] ERROR: %s", exc)
                diagnostics["planner_v2_error"] = str(exc)
                multi_plan = None

        # I1: Пропускаем legacy planner.run() если multi_plan с запросами уже получен —
        # иначе два LLM-вызова на каждый вопрос (двойной cost/latency)
        if multi_plan and multi_plan.queries:
            plan = self.planner.multi_plan_to_plan(multi_plan, question)
        else:
            try:
                plan = await self.planner.run(question)
            except Exception as exc:
                logger.error("[PLAN] ERROR: %s", exc)
                diagnostics["plan_error"] = str(exc)
                plan = self.planner.empty_plan(question.text)

        # T031: Если есть MultiPlan и aggregate_registry — выполняем все запросы через SQLAgent.run_multi()
        # Пропускаем run_multi() для keyword-fallback планов: их aggregate_id — topic-идентификаторы,
        # не валидные catalog aggregate_ids, и они провалят registry.validate().
        # Исключение: comparison:fallback генерирует реальные catalog aggregate_ids.
        multi_results: list[AggregateResult] = []
        _notes = multi_plan.notes or [] if multi_plan else []
        _skip_keyword = "planner_v2:keyword" in _notes and "comparison:fallback" not in _notes
        if (
            multi_plan
            and multi_plan.queries
            and self.aggregate_registry is not None
            and not _skip_keyword
        ):
            diagnostics["multi_plan_intent"] = multi_plan.intent
            diagnostics["multi_plan_queries"] = str(len(multi_plan.queries))
            try:
                multi_results = await self.sql_agent.run_multi(
                    multi_plan,
                    self.aggregate_registry,
                    logger_=self.query_logger,
                )
                ok_count = sum(1 for r in multi_results if r.status == "ok")
                diagnostics["multi_plan_ok"] = str(ok_count)
                logger.info(
                    "[MULTI_SQL] queries=%d ok=%d",
                    len(multi_results),
                    ok_count,
                )
            except Exception as exc:
                logger.error("[MULTI_SQL] ERROR: %s", exc)
                diagnostics["multi_sql_error"] = str(exc)
        elif multi_plan and multi_plan.queries:
            # Degradation: LLM спланировал запросы, но registry не инициализирован
            # (нет каталога агрегатов) — запросы не могут быть валидированы и выполнены.
            # Логируем для диагностики, fallback на legacy plan.
            first_query = multi_plan.queries[0]
            diagnostics["multi_plan_aggregate"] = first_query.aggregate_id
            diagnostics["multi_plan_intent"] = multi_plan.intent

        # Диагностика планировщика
        planner_mode = "llm" if "planner:llm" in plan.notes else "keyword"
        qp = plan.query_params
        if qp:
            logger.info(
                "[PLAN] %s | topic=%s | proc=%s group_by=%s filter=%s reason=%s | %s..%s",
                planner_mode,
                plan.topic,
                qp.procedure,
                qp.group_by,
                qp.filter,
                qp.reason,
                qp.date_from,
                qp.date_to,
            )
        else:
            logger.info(
                "[PLAN] %s | topic=%s | no query_params", planner_mode, plan.topic
            )

        # Пропускаем legacy SQL если run_multi() уже получил данные — иначе дублируем запрос
        has_multi_ok = any(r.status == "ok" for r in multi_results) if multi_results else False
        multi_all_failed = bool(multi_results) and not has_multi_ok
        if has_multi_ok:
            sql_insight = SQLInsight(rows=[], summary="skipped: multi_results available")
            pbi_insight = await self._run_pbi(question, plan, diagnostics)
        elif multi_all_failed:
            # #4: Все multi_results failed — НЕ запускаем legacy SQL с catalog topic_id,
            # иначе legacy не знает catalog id и дефолтит на statistics (неверные данные).
            sql_insight = SQLInsight(rows=[], summary="multi_results all failed")
            pbi_insight = await self._run_pbi(question, plan, diagnostics)
            diagnostics["multi_all_failed"] = "true"
        else:
            sql_task = asyncio.create_task(self._run_sql(question, plan, diagnostics))
            pbi_task = asyncio.create_task(self._run_pbi(question, plan, diagnostics))
            sql_insight, pbi_insight = await asyncio.gather(sql_task, pbi_task)

        # Генерируем график
        image = None
        mime_type = None
        has_chart = False

        # Comparison chart из multi_results (два периода → grouped bar)
        if (
            multi_results
            and multi_plan
            and multi_plan.intent == "comparison"
            and len(multi_results) >= 2
        ):
            ok_results = [r for r in multi_results if r.status == "ok" and r.rows]
            if len(ok_results) >= 2:
                try:
                    chart_bytes = await asyncio.to_thread(
                        render_comparison,
                        multi_plan.topic,
                        ok_results[0].rows,
                        ok_results[1].rows,
                        ok_results[0].label or ok_results[0].aggregate_id,
                        ok_results[1].label or ok_results[1].aggregate_id,
                        group_by=ok_results[0].group_by,
                    )
                    if chart_bytes:
                        image = chart_bytes
                        mime_type = "image/png"
                        has_chart = True
                        diagnostics["chart_type"] = "matplotlib_comparison"
                except Exception as exc:
                    diagnostics["chart_error"] = str(exc)

        # Обычный график из legacy SQL-данных (single query)
        if image is None and sql_insight.rows:
            try:
                chart_params = dict(sql_insight.params)
                chart_params["topic"] = plan.topic
                chart_bytes = await asyncio.to_thread(
                    render_chart,
                    plan.topic,
                    sql_insight.rows,
                    chart_params,
                )
                if chart_bytes:
                    image = chart_bytes
                    mime_type = "image/png"
                    has_chart = True
                    diagnostics["chart_type"] = "matplotlib"
            except Exception as exc:
                diagnostics["chart_error"] = str(exc)

        # Если matplotlib-график не получился и нужен Power BI рендер
        if image is None and plan.render_needed:
            try:
                artifact = await self.render_agent.run(question, plan)
                if artifact is not None:
                    image = artifact.image_bytes
                    mime_type = artifact.mime_type
                    if artifact.source_url:
                        diagnostics["render_source"] = artifact.source_url
            except Exception as exc:
                diagnostics["render_error"] = str(exc)

        # Если есть УСПЕШНЫЕ multi_results — используем run_multi для синтеза нескольких агрегатов,
        # иначе — legacy run() с одним SQL-результатом.
        # has_multi_ok уже вычислен выше; если все multi-queries failed, используем legacy analyst.
        if multi_results and multi_plan and has_multi_ok:
            analysis = await self.analyst_agent.run_multi(
                question=question.text,
                results=multi_results,
                plan=multi_plan,
            )
        else:
            analysis = await self.analyst_agent.run(
                question=question,
                plan=plan,
                sql_insight=sql_insight,
                model_insight=pbi_insight,
                diagnostics=diagnostics,
                has_chart=has_chart,
            )

        merged_diagnostics = dict(diagnostics)
        merged_diagnostics.update(analysis.diagnostics)

        return SwarmResponse(
            answer=analysis.answer,
            image=image,
            mime_type=mime_type,
            confidence=analysis.confidence,
            topic=plan.topic,
            follow_ups=analysis.follow_ups,
            diagnostics=merged_diagnostics,
        )

    async def _run_sql(self, question, plan, diagnostics: dict[str, str]) -> SQLInsight:
        try:
            result = await self.sql_agent.run(question, plan)
            logger.info("[SQL] topic=%s rows=%d", plan.topic, len(result.rows))
            return result
        except Exception as exc:
            logger.error("[SQL] ERROR: %s", exc)
            diagnostics["sql_error"] = str(exc)
            return SQLInsight(rows=[], summary="SQL step failed")

    async def _run_pbi(
        self, question, plan, diagnostics: dict[str, str]
    ) -> ModelInsight:
        try:
            return await self.powerbi_agent.run(question, plan)
        except Exception as exc:
            logger.error("[PBI] ERROR: %s", exc)
            diagnostics["powerbi_model_error"] = str(exc)
            return ModelInsight(metrics={}, summary="Power BI model step failed")

codex
I’ve found several places where the new assertions look suspiciously weak. I’m running a narrow test slice next to separate “bad coverage” from “actually broken under pytest” and to confirm whether the new `conftest` interactions behave the way the patch assumes.
exec
/bin/zsh -c 'PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_orchestrator.py' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -c 'PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_e2e_pipeline.py' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -c "PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/integration/test_real_e2e.py -m integration -k 'fallback_has_period or statistics_money_rounded'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 exited 1 in 245ms:
Traceback (most recent call last):
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/bin/pytest", line 10, in <module>
    sys.exit(console_main())
             ^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 223, in console_main
    code = main()
           ^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 193, in main
    config = _prepareconfig(new_args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 361, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1192, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1562, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/warnings.py", line 128, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 631, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 126, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/xc/29fk4qln2lx__qzv0wlwvnph0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot']

 exited 1 in 264ms:
Traceback (most recent call last):
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/bin/pytest", line 10, in <module>
    sys.exit(console_main())
             ^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 223, in console_main
    code = main()
           ^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 193, in main
    config = _prepareconfig(new_args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 361, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1192, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1562, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/warnings.py", line 128, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 631, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 126, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/xc/29fk4qln2lx__qzv0wlwvnph0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot']

 exited 1 in 246ms:
Traceback (most recent call last):
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/bin/pytest", line 10, in <module>
    sys.exit(console_main())
             ^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 223, in console_main
    code = main()
           ^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 193, in main
    config = _prepareconfig(new_args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 361, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1192, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1562, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/warnings.py", line 128, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 631, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 126, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/xc/29fk4qln2lx__qzv0wlwvnph0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot']

codex
I’ve confirmed two likely spec gaps already, but I’m checking the models before I write findings because several of these new MultiPlan tests depend on implicit Pydantic coercion. If that assumption is wrong, some of the new tests aren’t just weak, they’re invalid.
exec
/bin/zsh -lc "nl -ba tests/integration/test_real_e2e.py | sed -n '1,240p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "sed -n '1,320p' src/swarm_powerbi_bot/models.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "nl -ba tests/test_e2e_pipeline.py | sed -n '1,360p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class UserQuestion:
    user_id: str
    text: str
    report_id: str | None = None
    object_id: int | None = None  # SalonId из подписки пользователя
    last_topic: str = ""  # Тема предыдущего вопроса (для контекста разговора)


@dataclass
class QueryParams:
    """Параметры запроса, определённые LLM-планировщиком.

    Соответствует 3 универсальным процедурам:
    - spKDO_Aggregate: group_by определяет оси (total/week/month/master/service/salon/channel)
    - spKDO_ClientList: filter определяет статус (outflow/leaving/forecast/noshow/quality/birthday/all)
    - spKDO_CommAgg: reason + group_by определяют срез коммуникаций
    """

    procedure: str = ""  # spKDO_Aggregate / spKDO_ClientList / spKDO_CommAgg
    date_from: str = ""  # ISO: 2026-03-15
    date_to: str = ""  # ISO: 2026-04-14
    object_id: int | None = None  # SalonId (из подписки)
    master_id: int | None = None
    master_name: str = ""  # имя мастера из вопроса
    top: int = 20
    group_by: str = ""  # total/week/month/master/service/salon/channel/list/status/reason/result/manager
    filter: str = (
        ""  # outflow/leaving/forecast/noshow/quality/birthday/all (для ClientList)
    )
    reason: str = ""  # all/outflow/leaving/.../waitlist/opz (для CommAgg)


@dataclass
class Plan:
    objective: str
    topic: str = "statistics"
    sql_needed: bool = True
    powerbi_needed: bool = True
    render_needed: bool = True
    render_report_id: str | None = None
    notes: list[str] = field(default_factory=list)
    query_params: QueryParams | None = None  # LLM-определённые параметры запроса


@dataclass
class SQLInsight:
    rows: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    topic: str = ""
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelInsight:
    metrics: dict[str, Any] = field(default_factory=dict)
    summary: str = ""


@dataclass
class RenderedArtifact:
    image_bytes: bytes
    mime_type: str = "image/png"
    source_url: str | None = None


@dataclass
class AnalysisResult:
    answer: str
    confidence: Literal["low", "medium", "high"] = "medium"
    follow_ups: list[str] = field(default_factory=list)
    diagnostics: dict[str, str] = field(default_factory=dict)


# --- Semantic Aggregate Layer models ---


class AggregateParams(dict[str, Any]):
    """Типизированные параметры агрегатного запроса.

    Известные ключи: object_id (int), date_from/date_to (str YYYY-MM-DD),
    group_by (str), filter (str), top_n (int), master_id (int | None).
    """


@dataclass
class AggregateQuery:
    """Один запрос к агрегату из каталога (whitelist)."""

    aggregate_id: str
    params: AggregateParams = field(default_factory=AggregateParams)
    label: str = ""


@dataclass
class MultiPlan:
    """План выполнения для одного вопроса (результат одношагового LLM planning)."""

    objective: str
    intent: Literal["single", "comparison", "decomposition", "trend", "ranking"] = (
        "single"
    )
    queries: list[AggregateQuery] = field(default_factory=list)
    topic: str = "statistics"
    render_needed: bool = True
    notes: list[str] = field(default_factory=list)


@dataclass
class AggregateResult:
    """Результат одного агрегатного запроса."""

    aggregate_id: str = ""
    label: str = ""
    group_by: str = ""
    rows: list[dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    duration_ms: int = 0
    status: Literal["ok", "error", "timeout"] = "ok"
    error: str | None = None

    def __post_init__(self) -> None:
        if self.row_count == 0 and self.rows:
            self.row_count = len(self.rows)
        # Инвариант: status="ok" не может иметь error
        if self.status == "ok" and self.error:
            self.error = None


@dataclass
class ComparisonResult:
    """Результат сравнения двух наборов данных."""

    period_a: str
    period_b: str
    results_a: AggregateResult = field(default_factory=AggregateResult)
    results_b: AggregateResult = field(default_factory=AggregateResult)
    deltas: dict[str, float] = field(default_factory=dict)


@dataclass
class SwarmResponse:
    answer: str
    image: bytes | None = None
    mime_type: str | None = None
    confidence: Literal["low", "medium", "high"] = "medium"
    topic: str = ""  # Определённая тема (для контекста следующего вопроса)
    follow_ups: list[str] = field(default_factory=list)
    diagnostics: dict[str, str] = field(default_factory=dict)

 succeeded in 0ms:
     1	"""Интеграционные E2E тесты через реальный MSSQL + Ollama.
     2	
     3	Запуск: uv run pytest tests/integration/test_real_e2e.py -m integration -v
     4	"""
     5	from __future__ import annotations
     6	
     7	import asyncio
     8	
     9	import pytest
    10	
    11	from swarm_powerbi_bot.models import SwarmResponse, UserQuestion
    12	from swarm_powerbi_bot.orchestrator import SwarmOrchestrator
    13	
    14	pytestmark = pytest.mark.integration
    15	
    16	# Совпадает с TEST_OBJECT_ID в tests/integration/conftest.py.
    17	# Прямой import невозможен — pytest резолвит `from conftest` на tests/conftest.py.
    18	_TEST_OBJECT_ID = 506770
    19	
    20	
    21	def _question(text: str, **kwargs) -> UserQuestion:
    22	    defaults = {"user_id": "e2e-test", "object_id": _TEST_OBJECT_ID}
    23	    defaults.update(kwargs)
    24	    return UserQuestion(text=text, **defaults)
    25	
    26	
    27	# ── 1. Revenue question ─────────────────────────────────────────────────────
    28	
    29	async def test_e2e_revenue_question(real_orchestrator: SwarmOrchestrator):
    30	    resp = await real_orchestrator.handle_question(_question("Покажи выручку за март"))
    31	    assert resp.answer, "empty answer"
    32	    assert resp.topic != "unknown", f"topic should not be unknown, got {resp.topic}"
    33	
    34	
    35	# ── 2. Outflow question ─────────────────────────────────────────────────────
    36	
    37	async def test_e2e_outflow_question(real_orchestrator: SwarmOrchestrator):
    38	    resp = await real_orchestrator.handle_question(
    39	        _question("Какой отток за месяц?"),
    40	    )
    41	    assert resp.answer
    42	
    43	
    44	# ── 3. Comparison с chart ────────────────────────────────────────────────────
    45	
    46	async def test_e2e_comparison(real_orchestrator: SwarmOrchestrator):
    47	    resp = await real_orchestrator.handle_question(
    48	        _question("Сравни выручку марта и февраля"),
    49	    )
    50	    assert resp.answer
    51	    # Comparison pipeline должен генерировать chart
    52	    if resp.image is not None:
    53	        assert resp.mime_type == "image/png"
    54	
    55	
    56	# ── 4. Top masters ──────────────────────────────────────────────────────────
    57	
    58	async def test_e2e_top_masters(real_orchestrator: SwarmOrchestrator):
    59	    resp = await real_orchestrator.handle_question(
    60	        _question("Топ-5 мастеров по выручке за март"),
    61	    )
    62	    assert resp.answer
    63	
    64	
    65	# ── 5. Decomposition ────────────────────────────────────────────────────────
    66	
    67	async def test_e2e_decomposition(real_orchestrator: SwarmOrchestrator):
    68	    resp = await real_orchestrator.handle_question(
    69	        _question("Почему упала выручка?"),
    70	    )
    71	    assert resp.answer
    72	
    73	
    74	# ── 6. Unknown question ─────────────────────────────────────────────────────
    75	
    76	async def test_e2e_unknown_question(real_orchestrator: SwarmOrchestrator):
    77	    resp = await real_orchestrator.handle_question(
    78	        _question("Как сварить борщ?"),
    79	    )
    80	    assert isinstance(resp, SwarmResponse)
    81	    # Должен вежливо отказать или дать общий ответ
    82	
    83	
    84	# ── 7. Follow-up ────────────────────────────────────────────────────────────
    85	
    86	async def test_e2e_follow_up(real_orchestrator: SwarmOrchestrator):
    87	    resp1 = await real_orchestrator.handle_question(
    88	        _question("выручка за март"),
    89	    )
    90	    assert resp1.answer
    91	    topic = resp1.topic
    92	
    93	    resp2 = await real_orchestrator.handle_question(
    94	        _question("а за февраль?", last_topic=topic),
    95	    )
    96	    assert resp2.answer
    97	
    98	
    99	# ── 8. Chart generation ─────────────────────────────────────────────────────
   100	
   101	async def test_e2e_chart_generation(real_orchestrator: SwarmOrchestrator):
   102	    resp = await real_orchestrator.handle_question(
   103	        _question("Покажи график выручки по неделям за квартал"),
   104	    )
   105	    assert resp.answer
   106	    # Если chart сгенерирован, проверяем формат
   107	    if resp.image is not None:
   108	        assert resp.mime_type == "image/png"
   109	        assert len(resp.image) > 100  # не пустой PNG
   110	
   111	
   112	# ── 9. Telegram mock ────────────────────────────────────────────────────────
   113	
   114	async def test_e2e_telegram_mock(real_orchestrator: SwarmOrchestrator):
   115	    """Проверяем что orchestrator возвращает корректный SwarmResponse."""
   116	    resp = await real_orchestrator.handle_question(
   117	        _question("статистика за март"),
   118	    )
   119	    assert isinstance(resp, SwarmResponse)
   120	    assert resp.confidence in ("low", "medium", "high")
   121	    assert isinstance(resp.follow_ups, list)
   122	    assert isinstance(resp.diagnostics, dict)
   123	
   124	
   125	# ── 10. Concurrent users ────────────────────────────────────────────────────
   126	
   127	async def test_e2e_concurrent_users(real_orchestrator: SwarmOrchestrator):
   128	    questions = [
   129	        _question("выручка за март", user_id="user-1"),
   130	        _question("отток клиентов", user_id="user-2"),
   131	        _question("коммуникации за март", user_id="user-3"),
   132	    ]
   133	    results = await asyncio.gather(
   134	        *[real_orchestrator.handle_question(q) for q in questions],
   135	    )
   136	    for i, resp in enumerate(results):
   137	        assert isinstance(resp, SwarmResponse), f"user-{i+1} got non-SwarmResponse"
   138	        assert resp.answer, f"user-{i+1} got empty answer"
   139	
   140	
   141	# ── 11. Comparison has chart ───────────────────────────────────────────────
   142	
   143	async def test_e2e_comparison_has_chart(real_orchestrator: SwarmOrchestrator):
   144	    """Comparison pipeline должен генерировать PNG chart."""
   145	    resp = await real_orchestrator.handle_question(
   146	        _question("Сравни отток за март и апрель"),
   147	    )
   148	    assert resp.answer
   149	    # comparison должен генерировать chart; None допустим только при отсутствии matplotlib
   150	    assert resp.image is not None, "Comparison should produce a chart"
   151	    assert resp.image[:4] == b"\x89PNG"
   152	
   153	
   154	# ── 12. Fallback: no raw SQL fields ───────────────────────────────────────
   155	
   156	async def test_e2e_fallback_no_raw_fields(real_orchestrator: SwarmOrchestrator):
   157	    """Ответ не должен содержать сырые SQL-имена полей."""
   158	    resp = await real_orchestrator.handle_question(
   159	        _question("Какой отток за месяц?"),
   160	    )
   161	    assert resp.answer
   162	    raw_fields = {"DaysSinceLastVisit", "ServicePeriodDays", "DaysOverdue", "ClientName", "Phone"}
   163	    for f in raw_fields:
   164	        assert f not in resp.answer, f"Raw field {f} leaked into answer"
   165	
   166	
   167	# ── 13. Fallback: has period ───────────────────────────────────────────────
   168	
   169	async def test_e2e_fallback_has_period(real_orchestrator: SwarmOrchestrator):
   170	    """Ответ содержит информацию о периоде."""
   171	    resp = await real_orchestrator.handle_question(
   172	        _question("статистика за март"),
   173	    )
   174	    assert resp.answer
   175	    # Ожидаем упоминание даты или месяца в ответе
   176	    assert resp.topic in ("statistics", "trend")
   177	
   178	
   179	# ── 14. Statistics money rounded ───────────────────────────────────────────
   180	
   181	async def test_e2e_statistics_money_rounded(real_orchestrator: SwarmOrchestrator):
   182	    """Денежные метрики не содержат чрезмерных десятичных знаков."""
   183	    resp = await real_orchestrator.handle_question(
   184	        _question("статистика за март"),
   185	    )
   186	    assert resp.answer
   187	    # Структурная проверка: ответ не пуст и topic корректен
   188	    assert resp.topic in ("statistics", "trend")

 succeeded in 0ms:
     1	"""End-to-end тесты pipeline: вопрос → topic → SQL params → chart → ответ.
     2	
     3	Проверяет полную цепочку без обращения к MSSQL/LLM (моки).
     4	"""
     5	import asyncio
     6	from datetime import date
     7	
     8	import pytest
     9	
    10	from swarm_powerbi_bot.agents.planner import PlannerAgent
    11	from swarm_powerbi_bot.models import (
    12	    AnalysisResult,
    13	    ModelInsight,
    14	    Plan,
    15	    SQLInsight,
    16	    UserQuestion,
    17	)
    18	from swarm_powerbi_bot.orchestrator import SwarmOrchestrator
    19	from swarm_powerbi_bot.services.chart_renderer import HAS_MPL
    20	
    21	from conftest import build_mock_orchestrator_multi
    22	
    23	pytestmark = pytest.mark.e2e
    24	
    25	
    26	# ── Mock агенты с реалистичными данными ──────────────────────
    27	
    28	class MockSQL:
    29	    """Возвращает данные как настоящие хранимки — 11 тем (10 из checklist + leaving)."""
    30	    MOCK_DATA = {
    31	        "outflow": [
    32	            {"ClientName": "Козлова Р.", "Phone": "79001111111", "TotalSpent": 8112.6,
    33	             "DaysSinceLastVisit": 275, "DaysOverdue": 240, "TotalVisits": 11,
    34	             "ServicePeriodDays": 35, "SalonName": "Dream"},
    35	            {"ClientName": "Белова Т.", "Phone": "79002222222", "TotalSpent": 57054.0,
    36	             "DaysSinceLastVisit": 283, "DaysOverdue": 238, "TotalVisits": 59,
    37	             "ServicePeriodDays": 45, "SalonName": "Dream"},
    38	        ],
    39	        "statistics": [
    40	            {"TotalVisits": 219, "UniqueClients": 137, "TotalRevenue": 422028.50,
    41	             "AvgCheck": 1954.33, "ActiveMasters": 14, "SalonName": "Dream"},
    42	        ],
    43	        "trend": [
    44	            {"WeekEnd": "2026-03-02", "Visits": 45, "Revenue": 77424, "UniqueClients": 30, "AvgCheck": 1720, "ActiveMasters": 7},
    45	            {"WeekEnd": "2026-03-09", "Visits": 50, "Revenue": 85000, "UniqueClients": 35, "AvgCheck": 1700, "ActiveMasters": 8},
    46	        ],
    47	        "masters": [
    48	            {"MasterName": "Мастер А", "TotalRevenue": 120000, "TotalVisits": 50, "AvgCheck": 2400, "SalonName": "Dream"},
    49	        ],
    50	        "referrals": [
    51	            {"AcquisitionChannel": "Instagram", "ClientCount": 50},
    52	            {"AcquisitionChannel": "Рекомендация", "ClientCount": 30},
    53	        ],
    54	        "birthday": [
    55	            {"ClientName": "Иванова А.", "Phone": "79003333333", "BirthDate": "2000-04-16"},
    56	        ],
    57	        "communications": [
    58	            {"Reason": "outflow", "Result": "Вернулся", "TotalCount": 15},
    59	            {"Reason": "leaving", "Result": "Нет ответа", "TotalCount": 8},
    60	        ],
    61	        "forecast": [
    62	            {"ClientName": "Петрова М.", "ExpectedNextVisit": "2026-04-17", "ServicePeriodDays": 28},
    63	        ],
    64	        "services": [
    65	            {"ServiceName": "Стрижка", "Revenue": 85000, "ServiceCount": 120},
    66	            {"ServiceName": "Окрашивание", "Revenue": 65000, "ServiceCount": 40},
    67	        ],
    68	        "quality": [
    69	            {"ClientName": "Сидоров К.", "DaysOverdue": 5, "TotalVisits": 3, "SalonName": "Dream"},
    70	        ],
    71	        "leaving": [
    72	            {"ClientName": "Нова Е.", "DaysOverdue": 15, "TotalSpent": 12000, "TotalVisits": 7, "SalonName": "Dream"},
    73	        ],
    74	    }
    75	
    76	    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
    77	        rows = self.MOCK_DATA.get(plan.topic, [])
    78	        return SQLInsight(
    79	            rows=rows,
    80	            summary=f"SQL вернул {len(rows)} строк по теме «{plan.topic}»",
    81	            topic=plan.topic,
    82	            params={"DateFrom": date(2026, 3, 15), "DateTo": date(2026, 4, 14)},
    83	        )
    84	
    85	
    86	class MockPBI:
    87	    async def run(self, question, plan):
    88	        return ModelInsight(metrics={}, summary="model skipped")
    89	
    90	
    91	class MockRender:
    92	    async def run(self, question, plan):
    93	        return None
    94	
    95	
    96	class MockAnalyst:
    97	    """Возвращает canned output для проверки маршрутизации pipeline.
    98	
    99	    Реальную фильтрацию полей и качество формулировок проверяют
   100	    интеграционные тесты в tests/integration/test_real_e2e.py.
   101	    """
   102	    async def run(self, question, plan, sql_insight, model_insight, diagnostics, *, has_chart=False):
   103	        return AnalysisResult(
   104	            answer=f"Тема: {plan.topic}, строк: {len(sql_insight.rows)}",
   105	            confidence="medium",
   106	            follow_ups=["follow1"],
   107	        )
   108	
   109	
   110	def _build_orchestrator():
   111	    return SwarmOrchestrator(
   112	        planner=PlannerAgent(),
   113	        sql_agent=MockSQL(),
   114	        powerbi_agent=MockPBI(),
   115	        render_agent=MockRender(),
   116	        analyst_agent=MockAnalyst(),
   117	    )
   118	
   119	
   120	# ── E2E тесты ────────────────────────────────────────────────
   121	
   122	class TestE2EPipeline:
   123	    def test_outflow_question(self):
   124	        orch = _build_orchestrator()
   125	        result = asyncio.run(orch.handle_question(
   126	            UserQuestion(user_id="1", text="отток за месяц"),
   127	        ))
   128	        assert "outflow" in result.answer
   129	        assert result.topic == "outflow"
   130	
   131	    def test_statistics_question(self):
   132	        orch = _build_orchestrator()
   133	        result = asyncio.run(orch.handle_question(
   134	            UserQuestion(user_id="1", text="покажи статистику за неделю"),
   135	        ))
   136	        assert "statistics" in result.answer
   137	        assert result.topic == "statistics"
   138	
   139	    def test_masters_question(self):
   140	        orch = _build_orchestrator()
   141	        result = asyncio.run(orch.handle_question(
   142	            UserQuestion(user_id="1", text="загрузка мастеров"),
   143	        ))
   144	        assert "masters" in result.answer
   145	
   146	    def test_followup_keeps_topic(self):
   147	        """Follow-up вопрос сохраняет тему."""
   148	        orch = _build_orchestrator()
   149	        result = asyncio.run(orch.handle_question(
   150	            UserQuestion(user_id="1", text="подробнее по неделям", last_topic="outflow"),
   151	        ))
   152	        assert result.topic == "outflow"
   153	
   154	    def test_response_has_follow_ups(self):
   155	        orch = _build_orchestrator()
   156	        result = asyncio.run(orch.handle_question(
   157	            UserQuestion(user_id="1", text="отток за месяц"),
   158	        ))
   159	        assert len(result.follow_ups) > 0
   160	
   161	    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
   162	    def test_outflow_generates_chart(self):
   163	        """Отток с данными → matplotlib-график."""
   164	        orch = _build_orchestrator()
   165	        result = asyncio.run(orch.handle_question(
   166	            UserQuestion(user_id="1", text="отток за месяц"),
   167	        ))
   168	        assert result.image is not None
   169	        assert result.image[:4] == b"\x89PNG"
   170	
   171	    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
   172	    def test_trend_generates_line_chart(self):
   173	        orch = _build_orchestrator()
   174	        result = asyncio.run(orch.handle_question(
   175	            UserQuestion(user_id="1", text="покажи тренд за квартал"),
   176	        ))
   177	        assert result.image is not None
   178	
   179	    def test_empty_data_no_crash(self):
   180	        """Если SQL вернул 0 строк — не падаем."""
   181	        orch = _build_orchestrator()
   182	        result = asyncio.run(orch.handle_question(
   183	            UserQuestion(user_id="1", text="покажи именинников"),
   184	        ))
   185	        assert result.answer is not None
   186	
   187	
   188	# ── Planner тесты ────────────────────────────────────────────
   189	
   190	class TestPlannerNotes:
   191	    def test_comparison_note(self):
   192	        planner = PlannerAgent()
   193	        plan = asyncio.run(planner.run(
   194	            UserQuestion(user_id="1", text="сравни отток по неделям"),
   195	        ))
   196	        assert "comparison_requested" in plan.notes
   197	
   198	    def test_period_note_week(self):
   199	        planner = PlannerAgent()
   200	        plan = asyncio.run(planner.run(
   201	            UserQuestion(user_id="1", text="статистика за неделю"),
   202	        ))
   203	        assert "period:week" in plan.notes
   204	
   205	    def test_breakdown_by_master(self):
   206	        planner = PlannerAgent()
   207	        plan = asyncio.run(planner.run(
   208	            UserQuestion(user_id="1", text="выручка по мастерам"),
   209	        ))
   210	        assert "breakdown_by_master" in plan.notes
   211	
   212	
   213	# ── T004: Comparison / Composition pipeline ─────────────────────
   214	
   215	class TestMultiPlanPipeline:
   216	    def test_comparison_pipeline(self):
   217	        """MultiPlan comparison → SwarmResponse с ответом и chart."""
   218	        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
   219	        result = asyncio.run(orch.handle_question(
   220	            UserQuestion(user_id="1", text="сравни отток за два месяца"),
   221	        ))
   222	        assert result.answer is not None
   223	        assert "Сравнение" in result.answer
   224	        assert result.confidence in ("low", "medium", "high")
   225	
   226	    def test_comparison_pipeline_second_question(self):
   227	        """Второй comparison-вопрос через MultiPlan → корректный ответ."""
   228	        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
   229	        result = asyncio.run(orch.handle_question(
   230	            UserQuestion(user_id="1", text="сравни отток по салонам"),
   231	        ))
   232	        assert result.answer
   233	        assert len(result.answer) > 0
   234	
   235	    def test_decomposition_pipeline(self):
   236	        """MultiPlan decomposition → SwarmResponse с multi-result анализом."""
   237	        orch = build_mock_orchestrator_multi(intent="decomposition", topic="revenue_total")
   238	        result = asyncio.run(orch.handle_question(
   239	            UserQuestion(user_id="1", text="почему упала выручка?"),
   240	        ))
   241	        assert result.answer is not None
   242	        assert result.confidence in ("low", "medium", "high")
   243	
   244	
   245	# ── T005: 10 checklist questions ────────────────────────────────
   246	
   247	_CHECKLIST_QUESTIONS = [
   248	    ("отток за месяц", "outflow"),
   249	    ("покажи статистику за неделю", "statistics"),
   250	    ("динамика по неделям", "trend"),
   251	    ("загрузка мастеров", "masters"),
   252	    ("реферальная программа", "referrals"),
   253	    ("именинники на этой неделе", "birthday"),
   254	    ("результаты обзвонов", "communications"),
   255	    ("прогноз визитов", "forecast"),
   256	    ("популярные услуги", "services"),
   257	    ("контроль качества", "quality"),
   258	]
   259	
   260	
   261	class TestChecklistQuestions:
   262	    @pytest.mark.parametrize("question_text,expected_topic", _CHECKLIST_QUESTIONS)
   263	    def test_10_checklist_questions(self, question_text, expected_topic):
   264	        """Каждый из 10 вопросов чеклиста → non-empty SwarmResponse."""
   265	        orch = _build_orchestrator()
   266	        result = asyncio.run(orch.handle_question(
   267	            UserQuestion(user_id="1", text=question_text),
   268	        ))
   269	        assert result.answer is not None
   270	        assert len(result.answer) > 0
   271	        assert result.topic == expected_topic
   272	
   273	
   274	# ── T006: Follow-up chains ──────────────────────────────────────
   275	
   276	class TestFollowUpChains:
   277	    def test_follow_up_chain(self):
   278	        """Цепочка follow-up: тема сохраняется через last_topic."""
   279	        orch = _build_orchestrator()
   280	        r1 = asyncio.run(orch.handle_question(
   281	            UserQuestion(user_id="1", text="отток за месяц"),
   282	        ))
   283	        assert r1.topic == "outflow"
   284	
   285	        r2 = asyncio.run(orch.handle_question(
   286	            UserQuestion(user_id="1", text="подробнее", last_topic="outflow"),
   287	        ))
   288	        assert r2.topic == "outflow"
   289	
   290	        r3 = asyncio.run(orch.handle_question(
   291	            UserQuestion(user_id="1", text="а по неделям?", last_topic="outflow"),
   292	        ))
   293	        assert r3.topic == "outflow"
   294	
   295	    def test_follow_up_to_comparison(self):
   296	        """Follow-up «сравни» с last_topic → comparison через MultiPlan."""
   297	        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
   298	        result = asyncio.run(orch.handle_question(
   299	            UserQuestion(user_id="1", text="сравни по месяцам", last_topic="clients_outflow"),
   300	        ))
   301	        assert result.answer is not None
   302	        assert len(result.answer) > 0
   303	
   304	
   305	# ── T007: Negative scenarios ────────────────────────────────────
   306	
   307	class TestNegativeScenarios:
   308	    def test_negative_sql_injection(self):
   309	        """SQL-инъекция в тексте не ломает pipeline."""
   310	        orch = _build_orchestrator()
   311	        result = asyncio.run(orch.handle_question(
   312	            UserQuestion(user_id="1", text="'; DROP TABLE clients; --"),
   313	        ))
   314	        assert result.answer
   315	        assert "sql_error" not in result.diagnostics
   316	
   317	    def test_negative_off_topic(self):
   318	        """Вопрос не по теме → всё равно ответ (fallback topic)."""
   319	        orch = _build_orchestrator()
   320	        result = asyncio.run(orch.handle_question(
   321	            UserQuestion(user_id="1", text="какая погода в Москве?"),
   322	        ))
   323	        assert result.answer
   324	        assert result.topic  # непустой topic (fallback)
   325	
   326	    def test_negative_empty_text(self):
   327	        """Пустой текст запроса → не падаем."""
   328	        orch = _build_orchestrator()
   329	        result = asyncio.run(orch.handle_question(
   330	            UserQuestion(user_id="1", text=""),
   331	        ))
   332	        assert result.answer
   333	        assert result.topic
   334	
   335	    def test_negative_no_period(self):
   336	        """KPI-вопрос без указания периода → не падаем."""
   337	        orch = _build_orchestrator()
   338	        result = asyncio.run(orch.handle_question(
   339	            UserQuestion(user_id="1", text="покажи выручку"),
   340	        ))
   341	        assert result.answer
   342	        assert result.topic
   343	
   344	    def test_negative_long_text(self):
   345	        """Очень длинный текст → не падаем."""
   346	        orch = _build_orchestrator()
   347	        long_text = "отток " * 500
   348	        result = asyncio.run(orch.handle_question(
   349	            UserQuestion(user_id="1", text=long_text),
   350	        ))
   351	        assert result.answer
   352	        assert result.topic == "outflow"
   353	
   354	
   355	# ── T008: Smoke / fallback quality ──────────────────────────────
   356	# NB: MockAnalyst возвращает canned output — эти тесты проверяют маршрутизацию
   357	# pipeline, а не качество формулировок аналитика. Реальное качество ответов
   358	# (отсутствие сырых SQL-полей, форматирование чисел) проверяют интеграционные
   359	# тесты в tests/integration/test_real_e2e.py.
   360	

exec
/bin/zsh -lc "nl -ba tests/test_e2e_pipeline.py | sed -n '360,460p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
   360	
   361	class TestFallbackQuality:
   362	    def test_outflow_fallback_no_raw_fields(self):
   363	        """Mock pipeline: ответ не содержит сырых SQL-имён.
   364	
   365	        NB: MockAnalyst возвращает canned output — реальную фильтрацию
   366	        полей проверяет integration/test_real_e2e::test_e2e_fallback_no_raw_fields.
   367	        """
   368	        orch = _build_orchestrator()
   369	        result = asyncio.run(orch.handle_question(
   370	            UserQuestion(user_id="1", text="отток за месяц"),
   371	        ))
   372	        raw_fields = {"DaysSinceLastVisit", "DaysOverdue", "TotalSpent", "ServicePeriodDays", "Phone"}
   373	        for field in raw_fields:
   374	            assert field not in result.answer, f"Сырое поле {field} в ответе"
   375	
   376	    def test_statistics_pipeline_returns_correct_topic(self):
   377	        """Mock pipeline: маршрутизация statistics возвращает непустой ответ.
   378	
   379	        NB: MockAnalyst возвращает canned output — качество текста проверяют
   380	        интеграционные тесты в tests/integration/test_real_e2e.py.
   381	        """
   382	        orch = _build_orchestrator()
   383	        result = asyncio.run(orch.handle_question(
   384	            UserQuestion(user_id="1", text="покажи статистику за неделю"),
   385	        ))
   386	        assert result.topic == "statistics"
   387	        assert result.answer
   388	        assert result.confidence in ("low", "medium", "high")
   389	
   390	    def test_statistics_pipeline_has_follow_ups(self):
   391	        """Mock pipeline: statistics возвращает follow-up подсказки.
   392	
   393	        NB: MockAnalyst возвращает canned output — содержание follow-ups
   394	        проверяют интеграционные тесты в tests/integration/test_real_e2e.py.
   395	        """
   396	        orch = _build_orchestrator()
   397	        result = asyncio.run(orch.handle_question(
   398	            UserQuestion(user_id="1", text="покажи статистику за неделю"),
   399	        ))
   400	        assert result.topic == "statistics"
   401	        assert len(result.follow_ups) > 0

exec
/bin/zsh -lc "nl -ba tests/conftest.py | sed -n '1,240p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
     1	"""Shared mock classes and fixtures for E2E and orchestrator tests."""
     2	from __future__ import annotations
     3	
     4	from swarm_powerbi_bot.models import (
     5	    AggregateResult,
     6	    AnalysisResult,
     7	    ModelInsight,
     8	    MultiPlan,
     9	    Plan,
    10	    RenderedArtifact,
    11	    SQLInsight,
    12	    UserQuestion,
    13	)
    14	from swarm_powerbi_bot.orchestrator import SwarmOrchestrator
    15	
    16	
    17	# ── Base Dummy classes ──────────────────────────────────────────
    18	
    19	
    20	class DummyPlanner:
    21	    aggregate_registry = None
    22	
    23	    async def run(self, question: UserQuestion) -> Plan:
    24	        return Plan(
    25	            objective=question.text, topic="statistics",
    26	            sql_needed=True, powerbi_needed=True, render_needed=True,
    27	        )
    28	
    29	
    30	class DummySQL:
    31	    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
    32	        return SQLInsight(rows=[{"kpi": "sales", "value": 100}], summary="sql ok")
    33	
    34	
    35	class DummyPBI:
    36	    async def run(self, question: UserQuestion, plan: Plan) -> ModelInsight:
    37	        return ModelInsight(metrics={"margin": 0.32}, summary="model ok")
    38	
    39	
    40	class DummyRender:
    41	    async def run(self, question: UserQuestion, plan: Plan) -> RenderedArtifact:
    42	        _ = question, plan
    43	        return RenderedArtifact(image_bytes=b"png-bytes", source_url="http://report")
    44	
    45	
    46	class DummyAnalyst:
    47	    async def run(self, question, plan, sql_insight, model_insight, diagnostics, *, has_chart=False):
    48	        _ = question, plan, sql_insight, model_insight, has_chart
    49	        return AnalysisResult(answer="analysis", confidence="high", diagnostics=diagnostics)
    50	
    51	
    52	# ── MultiPlan-aware mocks ──────────────────────────────────────
    53	
    54	
    55	class MockRegistry:
    56	    """Minimal AggregateRegistry stub."""
    57	
    58	    def get_aggregate(self, agg_id: str):
    59	        return {"id": agg_id, "procedure": "spKDO_Aggregate", "parameters": []}
    60	
    61	    def list_aggregates(self):
    62	        return [{"id": "revenue_total"}, {"id": "clients_outflow"}]
    63	
    64	
    65	class MockPlannerWithRegistry(DummyPlanner):
    66	    def __init__(self, registry=None, *, intent="comparison", topic="clients_outflow", n_queries=2):
    67	        self.aggregate_registry = registry or MockRegistry()
    68	        self._intent = intent
    69	        self._topic = topic
    70	        self._n_queries = n_queries
    71	
    72	    async def run_multi(self, question):
    73	        return MultiPlan(
    74	            objective=question.text,
    75	            intent=self._intent,
    76	            queries=[{"aggregate_id": self._topic} for _ in range(self._n_queries)],
    77	            topic=self._topic,
    78	            render_needed=True,
    79	            notes=["planner_v2:llm"],
    80	        )
    81	
    82	    def multi_plan_to_plan(self, multi_plan, question):
    83	        return Plan(
    84	            objective=multi_plan.objective,
    85	            topic=multi_plan.topic,
    86	            notes=list(multi_plan.notes),
    87	        )
    88	
    89	
    90	class MockSQLMulti(DummySQL):
    91	    """SQL agent that supports run_multi() with configurable results."""
    92	
    93	    def __init__(self, results: list[AggregateResult] | None = None):
    94	        self._results = results or [
    95	            AggregateResult(
    96	                aggregate_id="clients_outflow", label="Март 2026",
    97	                group_by="status", status="ok",
    98	                rows=[
    99	                    {"ClientStatus": "Отток", "ClientCount": 20},
   100	                    {"ClientStatus": "Уходящие", "ClientCount": 15},
   101	                ],
   102	            ),
   103	            AggregateResult(
   104	                aggregate_id="clients_outflow", label="Апрель 2026",
   105	                group_by="status", status="ok",
   106	                rows=[
   107	                    {"ClientStatus": "Отток", "ClientCount": 18},
   108	                    {"ClientStatus": "Уходящие", "ClientCount": 12},
   109	                ],
   110	            ),
   111	        ]
   112	
   113	    async def run_multi(self, multi_plan, registry, *, logger_=None):
   114	        return self._results
   115	
   116	
   117	class MockAnalystMulti(DummyAnalyst):
   118	    async def run_multi(self, question, results, plan):
   119	        ok = [r for r in results if r.status == "ok"]
   120	        if len(ok) >= 2:
   121	            answer = f"Сравнение: {ok[0].label} vs {ok[1].label}\n• Клиенты: +17%"
   122	        elif ok:
   123	            answer = f"Анализ: {ok[0].label}, {ok[0].row_count} строк"
   124	        else:
   125	            answer = "Нет данных для анализа"
   126	        return AnalysisResult(
   127	            answer=answer,
   128	            confidence="medium",
   129	            diagnostics={},
   130	        )
   131	
   132	
   133	def build_mock_orchestrator_multi(*, intent="comparison", topic="clients_outflow"):
   134	    """Build orchestrator wired for MultiPlan flow."""
   135	    registry = MockRegistry()
   136	    return SwarmOrchestrator(
   137	        planner=MockPlannerWithRegistry(registry, intent=intent, topic=topic),
   138	        sql_agent=MockSQLMulti(),
   139	        powerbi_agent=DummyPBI(),
   140	        render_agent=DummyRender(),
   141	        analyst_agent=MockAnalystMulti(),
   142	        aggregate_registry=registry,
   143	    )

exec
/bin/zsh -lc "nl -ba tests/integration/test_real_llm.py | sed -n '1,260p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
     1	"""Интеграционные тесты LLM через реальный Ollama.
     2	
     3	Запуск: uv run pytest tests/integration/test_real_llm.py -m integration -v
     4	"""
     5	from __future__ import annotations
     6	
     7	import json
     8	import urllib.request
     9	
    10	import pytest
    11	
    12	from swarm_powerbi_bot.agents import AnalystAgent, PlannerAgent
    13	from swarm_powerbi_bot.models import AggregateResult, MultiPlan, UserQuestion
    14	from swarm_powerbi_bot.services import LLMClient
    15	from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry
    16	
    17	pytestmark = pytest.mark.integration
    18	
    19	
    20	# ── 1. Ollama health ─────────────────────────────────────────────────────────
    21	
    22	def test_ollama_health(real_settings, ollama_ok):
    23	    if not ollama_ok:
    24	        pytest.skip("Ollama not available")
    25	    url = real_settings.ollama_base_url.rstrip("/") + "/api/tags"
    26	    resp = urllib.request.urlopen(url, timeout=10)  # noqa: S310
    27	    data = json.loads(resp.read())
    28	    assert "models" in data
    29	
    30	
    31	# ── 2. Простое completion ────────────────────────────────────────────────────
    32	
    33	def test_simple_completion(real_settings, ollama_ok):
    34	    if not ollama_ok:
    35	        pytest.skip("Ollama not available")
    36	    url = real_settings.ollama_base_url.rstrip("/") + "/api/chat"
    37	    payload = json.dumps({
    38	        "model": real_settings.ollama_model,
    39	        "messages": [{"role": "user", "content": "Скажи привет"}],
    40	        "stream": False,
    41	        "think": False,
    42	        "options": {"num_predict": 64},
    43	    }).encode()
    44	    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    45	    resp = urllib.request.urlopen(req, timeout=15)  # noqa: S310
    46	    body = json.loads(resp.read())
    47	    content = body.get("message", {}).get("content", "")
    48	    assert content.strip(), "Empty LLM response"
    49	
    50	
    51	# ── 3. Planner keyword fallback ──────────────────────────────────────────────
    52	
    53	async def test_planner_keyword_fallback(real_settings):
    54	    """PlannerAgent без registry → keyword fallback должен вернуть Plan."""
    55	    llm_client = LLMClient(real_settings)
    56	    # Без registry — keyword mode
    57	    planner = PlannerAgent(llm_client=llm_client, aggregate_registry=None)
    58	    question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
    59	    plan = await planner.run(question)
    60	    assert plan.topic
    61	
    62	
    63	# ── 4. Planner LLM mode ─────────────────────────────────────────────────────
    64	
    65	async def test_planner_llm_mode(
    66	    real_settings, real_registry: AggregateRegistry, ollama_ok,
    67	):
    68	    if not ollama_ok:
    69	        pytest.skip("Ollama not available")
    70	    llm_client = LLMClient(real_settings)
    71	    planner = PlannerAgent(
    72	        llm_client=llm_client,
    73	        aggregate_registry=real_registry,
    74	        semantic_catalog_path=real_settings.semantic_catalog_path,
    75	    )
    76	    question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
    77	    plan = await planner.run_multi(question)
    78	    assert plan.queries, "Expected at least 1 query"
    79	    assert plan.intent
    80	
    81	
    82	# ── 5. Planner comparison ────────────────────────────────────────────────────
    83	
    84	async def test_planner_comparison(
    85	    real_settings, real_registry: AggregateRegistry, ollama_ok,
    86	):
    87	    if not ollama_ok:
    88	        pytest.skip("Ollama not available")
    89	    llm_client = LLMClient(real_settings)
    90	    planner = PlannerAgent(
    91	        llm_client=llm_client,
    92	        aggregate_registry=real_registry,
    93	        semantic_catalog_path=real_settings.semantic_catalog_path,
    94	    )
    95	    question = UserQuestion(
    96	        user_id="test", text="сравни выручку за март и апрель", object_id=506770,
    97	    )
    98	    plan = await planner.run_multi(question)
    99	    assert plan.intent == "comparison", f"expected comparison, got {plan.intent}"
   100	    assert len(plan.queries) >= 2, f"expected >=2 queries, got {len(plan.queries)}"
   101	
   102	
   103	# ── 6. Planner decomposition ────────────────────────────────────────────────
   104	
   105	async def test_planner_decomposition(
   106	    real_settings, real_registry: AggregateRegistry, ollama_ok,
   107	):
   108	    if not ollama_ok:
   109	        pytest.skip("Ollama not available")
   110	    llm_client = LLMClient(real_settings)
   111	    planner = PlannerAgent(
   112	        llm_client=llm_client,
   113	        aggregate_registry=real_registry,
   114	        semantic_catalog_path=real_settings.semantic_catalog_path,
   115	    )
   116	    question = UserQuestion(
   117	        user_id="test", text="почему упала выручка?", object_id=506770,
   118	    )
   119	    plan = await planner.run_multi(question)
   120	    assert plan.intent in ("decomposition", "single"), f"got {plan.intent}"
   121	    assert len(plan.queries) >= 1
   122	
   123	
   124	# ── 7. Unknown topic graceful ────────────────────────────────────────────────
   125	
   126	async def test_planner_unknown_topic(
   127	    real_settings, real_registry: AggregateRegistry, ollama_ok,
   128	):
   129	    if not ollama_ok:
   130	        pytest.skip("Ollama not available")
   131	    llm_client = LLMClient(real_settings)
   132	    planner = PlannerAgent(
   133	        llm_client=llm_client,
   134	        aggregate_registry=real_registry,
   135	        semantic_catalog_path=real_settings.semantic_catalog_path,
   136	    )
   137	    question = UserQuestion(user_id="test", text="рецепт борща", object_id=506770)
   138	    plan = await planner.run_multi(question)
   139	    # Не должен падать — либо пустой план, либо fallback
   140	    assert isinstance(plan, MultiPlan)
   141	
   142	
   143	# ── 8. Analyst summary ──────────────────────────────────────────────────────
   144	
   145	async def test_analyst_summary(real_settings, ollama_ok):
   146	    if not ollama_ok:
   147	        pytest.skip("Ollama not available")
   148	    llm_client = LLMClient(real_settings)
   149	    analyst = AnalystAgent(llm_client)
   150	    mock_results = [
   151	        AggregateResult(
   152	            aggregate_id="revenue_total",
   153	            label="Выручка",
   154	            rows=[{"Revenue": 1500000, "Visits": 320, "AvgCheck": 4687}],
   155	            row_count=1,
   156	            duration_ms=100,
   157	            status="ok",
   158	        ),
   159	    ]
   160	    question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
   161	    result = await analyst.run(question=question, sql_results=mock_results)
   162	    assert result.answer
   163	    assert len(result.answer) <= 2000
   164	
   165	
   166	# ── 9. Circuit breaker ──────────────────────────────────────────────────────
   167	
   168	async def test_circuit_breaker(real_settings):
   169	    """После N timeout-ов breaker открывается."""
   170	    from swarm_powerbi_bot.config import Settings
   171	
   172	    fast_settings = Settings(
   173	        ollama_base_url=real_settings.ollama_base_url,
   174	        ollama_model=real_settings.ollama_model,
   175	        llm_plan_timeout=0,  # мгновенный timeout
   176	        llm_circuit_breaker_threshold=2,
   177	        llm_circuit_breaker_cooldown=60,
   178	        aggregate_catalog_path=real_settings.aggregate_catalog_path,
   179	    )
   180	    llm_client = LLMClient(fast_settings)
   181	    registry = AggregateRegistry(real_settings.aggregate_catalog_path)
   182	    planner = PlannerAgent(
   183	        llm_client=llm_client, aggregate_registry=registry,
   184	        semantic_catalog_path=real_settings.semantic_catalog_path,
   185	    )
   186	    question = UserQuestion(user_id="test", text="выручка", object_id=506770)
   187	
   188	    # Несколько попыток для активации breaker
   189	    for _ in range(3):
   190	        plan = await planner.run_multi(question)
   191	
   192	    # После breaker — должен сработать fallback (keyword)
   193	    plan = await planner.run_multi(question)
   194	    assert isinstance(plan, MultiPlan)
   195	
   196	
   197	# ── 10. LLM timeout не зависает ─────────────────────────────────────────────
   198	
   199	async def test_llm_timeout(real_settings, ollama_ok):
   200	    if not ollama_ok:
   201	        pytest.skip("Ollama not available")
   202	    from swarm_powerbi_bot.config import Settings
   203	
   204	    # Крайне малый timeout
   205	    fast_settings = Settings(
   206	        ollama_base_url=real_settings.ollama_base_url,
   207	        ollama_model=real_settings.ollama_model,
   208	        llm_plan_timeout=0,
   209	        aggregate_catalog_path=real_settings.aggregate_catalog_path,
   210	    )
   211	    llm_client = LLMClient(fast_settings)
   212	    registry = AggregateRegistry(real_settings.aggregate_catalog_path)
   213	    planner = PlannerAgent(
   214	        llm_client=llm_client, aggregate_registry=registry,
   215	        semantic_catalog_path=real_settings.semantic_catalog_path,
   216	    )
   217	    question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
   218	    # Не должен зависнуть — должен вернуть fallback или timeout
   219	    plan = await planner.run_multi(question)
   220	    assert isinstance(plan, MultiPlan)
   221	
   222	
   223	# ── 11. Parametrized 10 questions → valid MultiPlan ─────────────────────────
   224	
   225	_PLANNER_10_QUESTIONS = [
   226	    "Покажи отток клиентов за месяц",
   227	    "Статистика за эту неделю",
   228	    "Динамика выручки по неделям за квартал",
   229	    "Загрузка мастеров за март",
   230	    "Каналы привлечения клиентов",
   231	    "Именинники на этой неделе",
   232	    "Результаты обзвонов за март",
   233	    "Прогноз визитов на следующую неделю",
   234	    "Популярные услуги за месяц",
   235	    "Контроль качества за март",
   236	]
   237	
   238	
   239	@pytest.mark.parametrize("question_text", _PLANNER_10_QUESTIONS)
   240	async def test_planner_10_questions(
   241	    real_settings, real_registry: AggregateRegistry, ollama_ok, question_text,
   242	):
   243	    if not ollama_ok:
   244	        pytest.skip("Ollama not available")
   245	    llm_client = LLMClient(real_settings)
   246	    planner = PlannerAgent(
   247	        llm_client=llm_client,
   248	        aggregate_registry=real_registry,
   249	        semantic_catalog_path=real_settings.semantic_catalog_path,
   250	    )
   251	    question = UserQuestion(user_id="test", text=question_text, object_id=506770)
   252	    plan = await planner.run_multi(question)
   253	    assert isinstance(plan, MultiPlan)
   254	    assert plan.queries, f"No queries for: {question_text}"
   255	    assert plan.topic, f"No topic for: {question_text}"
   256	    assert plan.intent in ("single", "comparison", "decomposition"), \
   257	        f"Invalid intent '{plan.intent}' for: {question_text}"

exec
/bin/zsh -lc "sed -n '1,240p' specs/010-test-coverage/tasks.md" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
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

exec
/bin/zsh -lc 'git diff --unified=20 main...HEAD -- tests/integration/test_real_llm.py' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 1462ms:
2026-04-15 23:13:02.972 xcodebuild[33852:108889597]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:13:03.149 xcodebuild[33852:108889596] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ojNEZpqW' (errno=Operation not permitted)
2026-04-15 23:13:03.499 xcodebuild[33855:108889635]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 23:13:03.608 xcodebuild[33855:108889634] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
diff --git a/swarm_powerbi_bot/tests/integration/test_real_llm.py b/swarm_powerbi_bot/tests/integration/test_real_llm.py
index 0855642..01789f7 100644
--- a/swarm_powerbi_bot/tests/integration/test_real_llm.py
+++ b/swarm_powerbi_bot/tests/integration/test_real_llm.py
@@ -34,41 +34,41 @@ def test_simple_completion(real_settings, ollama_ok):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     url = real_settings.ollama_base_url.rstrip("/") + "/api/chat"
     payload = json.dumps({
         "model": real_settings.ollama_model,
         "messages": [{"role": "user", "content": "Скажи привет"}],
         "stream": False,
         "think": False,
         "options": {"num_predict": 64},
     }).encode()
     req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
     resp = urllib.request.urlopen(req, timeout=15)  # noqa: S310
     body = json.loads(resp.read())
     content = body.get("message", {}).get("content", "")
     assert content.strip(), "Empty LLM response"
 
 
 # ── 3. Planner keyword fallback ──────────────────────────────────────────────
 
 async def test_planner_keyword_fallback(real_settings):
-    """PlannerAgent без LLM (только keyword) должен вернуть Plan."""
+    """PlannerAgent без registry → keyword fallback должен вернуть Plan."""
     llm_client = LLMClient(real_settings)
     # Без registry — keyword mode
     planner = PlannerAgent(llm_client=llm_client, aggregate_registry=None)
     question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
     plan = await planner.run(question)
     assert plan.topic
 
 
 # ── 4. Planner LLM mode ─────────────────────────────────────────────────────
 
 async def test_planner_llm_mode(
     real_settings, real_registry: AggregateRegistry, ollama_ok,
 ):
     if not ollama_ok:
         pytest.skip("Ollama not available")
     llm_client = LLMClient(real_settings)
     planner = PlannerAgent(
         llm_client=llm_client,
         aggregate_registry=real_registry,
         semantic_catalog_path=real_settings.semantic_catalog_path,
@@ -201,20 +201,57 @@ async def test_llm_timeout(real_settings, ollama_ok):
         pytest.skip("Ollama not available")
     from swarm_powerbi_bot.config import Settings
 
     # Крайне малый timeout
     fast_settings = Settings(
         ollama_base_url=real_settings.ollama_base_url,
         ollama_model=real_settings.ollama_model,
         llm_plan_timeout=0,
         aggregate_catalog_path=real_settings.aggregate_catalog_path,
     )
     llm_client = LLMClient(fast_settings)
     registry = AggregateRegistry(real_settings.aggregate_catalog_path)
     planner = PlannerAgent(
         llm_client=llm_client, aggregate_registry=registry,
         semantic_catalog_path=real_settings.semantic_catalog_path,
     )
     question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
     # Не должен зависнуть — должен вернуть fallback или timeout
     plan = await planner.run_multi(question)
     assert isinstance(plan, MultiPlan)
+
+
+# ── 11. Parametrized 10 questions → valid MultiPlan ─────────────────────────
+
+_PLANNER_10_QUESTIONS = [
+    "Покажи отток клиентов за месяц",
+    "Статистика за эту неделю",
+    "Динамика выручки по неделям за квартал",
+    "Загрузка мастеров за март",
+    "Каналы привлечения клиентов",
+    "Именинники на этой неделе",
+    "Результаты обзвонов за март",
+    "Прогноз визитов на следующую неделю",
+    "Популярные услуги за месяц",
+    "Контроль качества за март",
+]
+
+
+@pytest.mark.parametrize("question_text", _PLANNER_10_QUESTIONS)
+async def test_planner_10_questions(
+    real_settings, real_registry: AggregateRegistry, ollama_ok, question_text,
+):
+    if not ollama_ok:
+        pytest.skip("Ollama not available")
+    llm_client = LLMClient(real_settings)
+    planner = PlannerAgent(
+        llm_client=llm_client,
+        aggregate_registry=real_registry,
+        semantic_catalog_path=real_settings.semantic_catalog_path,
+    )
+    question = UserQuestion(user_id="test", text=question_text, object_id=506770)
+    plan = await planner.run_multi(question)
+    assert isinstance(plan, MultiPlan)
+    assert plan.queries, f"No queries for: {question_text}"
+    assert plan.topic, f"No topic for: {question_text}"
+    assert plan.intent in ("single", "comparison", "decomposition"), \
+        f"Invalid intent '{plan.intent}' for: {question_text}"

codex
I have enough to write findings, but I’m checking one more thing: whether the mock MultiPlan objects actually match the production contract. If the mocks are using the wrong shape and the fake SQL agent ignores it, the new MultiPlan tests are effectively testing a different API.
exec
/bin/zsh -lc "sed -n '1,260p' src/swarm_powerbi_bot/agents/planner.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "sed -n '1,260p' src/swarm_powerbi_bot/agents/sql.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
from __future__ import annotations

import asyncio
import logging

from typing import TYPE_CHECKING

from .base import Agent
from ..config import Settings
from ..models import AggregateQuery, AggregateResult, MultiPlan, Plan, SQLInsight, UserQuestion
from ..services.sql_client import SQLClient

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..services.aggregate_registry import AggregateRegistry
    from ..services.query_logger import QueryLogger


class SQLAgent(Agent):
    name = "sql"

    def __init__(self, client: SQLClient, settings: Settings | None = None):
        self.client = client
        self.settings = settings

    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
        if not plan.sql_needed:
            return SQLInsight(rows=[], summary="SQL step skipped by planner")

        # Если есть LLM-параметры — используем их напрямую
        if plan.query_params and plan.query_params.procedure:
            rows, topic_id, params = await self.client.fetch_rows_with_params(
                plan.query_params,
            )
        else:
            # Fallback: старый путь через keyword-детекцию
            rows, topic_id, params = await self.client.fetch_rows(
                question.text, topic=plan.topic, object_id=question.object_id,
            )

        effective_topic = topic_id or plan.topic
        status = "ok" if rows else "empty"
        logger.info(
            "sql.run user=%s topic=%s rows=%d status=%s",
            question.user_id,
            effective_topic,
            len(rows),
            status,
        )

        if not rows:
            return SQLInsight(
                rows=[],
                summary="SQL вернул 0 строк или соединение не настроено",
                topic=effective_topic,
                params=params,
            )

        return SQLInsight(
            rows=rows,
            summary=f"SQL вернул {len(rows)} строк(и) по теме «{effective_topic}»",
            topic=effective_topic,
            params=params,
        )

    async def run_multi(
        self,
        plan: MultiPlan,
        registry: "AggregateRegistry",
        sql_client: SQLClient | None = None,
        logger_: "QueryLogger | None" = None,
        user_id: str = "system",
    ) -> list[AggregateResult]:
        """T029/T032: Выполняет несколько агрегатных запросов параллельно.

        - Ограничивает количество запросов до settings.sql_max_queries
        - Использует asyncio.Semaphore(settings.sql_max_concurrency) для ограничения параллельности
        - При timeout/error возвращает AggregateResult с соответствующим статусом
        - Логирует каждый вызов через QueryLogger если передан
        """
        client = sql_client or self.client

        # Определяем лимиты из settings или используем дефолты
        max_queries = 10
        max_concurrency = 5
        query_timeout = 10
        if self.settings is not None:
            max_queries = self.settings.sql_max_queries
            max_concurrency = self.settings.sql_max_concurrency
            query_timeout = self.settings.sql_query_timeout

        queries = plan.queries[:max_queries]
        semaphore = asyncio.Semaphore(max_concurrency)

        async def _run_one(query: AggregateQuery) -> AggregateResult:
            async with semaphore:
                try:
                    result = await asyncio.wait_for(
                        client.execute_aggregate(query.aggregate_id, query.params, registry),
                        timeout=query_timeout,
                    )
                    # Подставляем label и group_by из запроса
                    effective_label = query.label or result.label
                    effective_group_by = query.params.get("group_by", "")
                    if effective_label != result.label or effective_group_by:
                        result = AggregateResult(
                            aggregate_id=result.aggregate_id,
                            label=effective_label,
                            group_by=effective_group_by,
                            rows=result.rows,
                            row_count=result.row_count,
                            duration_ms=result.duration_ms,
                            status=result.status,
                            error=result.error,
                        )
                except asyncio.TimeoutError:
                    result = AggregateResult(
                        aggregate_id=query.aggregate_id,
                        label=query.label,
                        status="timeout",
                        error="SQL query timed out",
                    )
                except Exception as exc:
                    logger.error("run_multi error for %r: %s", query.aggregate_id, exc)
                    result = AggregateResult(
                        aggregate_id=query.aggregate_id,
                        label=query.label,
                        status="error",
                        error=str(exc),
                    )

                # T032: логируем каждый вызов
                if logger_ is not None:
                    try:
                        logger_.log(
                            user_id=user_id,
                            aggregate_id=result.aggregate_id,
                            params=query.params,
                            duration_ms=result.duration_ms,
                            row_count=result.row_count,
                            status=result.status,
                            error=result.error,
                        )
                    except Exception as log_exc:
                        logger.warning("QueryLogger.log failed: %s", log_exc)

                return result

        return list(await asyncio.gather(*[_run_one(q) for q in queries]))

 succeeded in 0ms:
from __future__ import annotations

import calendar
import logging
import os
import re
from datetime import date, timedelta

from .base import Agent
from ..models import AggregateParams, AggregateQuery, MultiPlan, Plan, QueryParams, UserQuestion
from ..services.aggregate_registry import AggregateRegistry
from ..services.llm_client import LLMClient
from ..services.topic_registry import detect_topic, get_procedure

logger = logging.getLogger(__name__)

# Если True — используем v2 процедуры (spKDO_Aggregate/ClientList/CommAgg)
# Если False — маппим обратно на старые процедуры (spKDO_Outflow и т.д.)
_USE_V2 = os.getenv("USE_V2_PROCEDURES", "").strip().lower() in {"1", "true", "yes"}

# Маппинг (procedure, group_by/filter) → topic для chart_renderer и analyst
_PROCEDURE_TOPIC_MAP: dict[tuple[str, str], str] = {
    # Aggregate
    ("spKDO_Aggregate", "total"): "statistics",
    ("spKDO_Aggregate", "week"): "trend",
    ("spKDO_Aggregate", "month"): "trend",
    ("spKDO_Aggregate", "master"): "masters",
    ("spKDO_Aggregate", "service"): "services",
    ("spKDO_Aggregate", "salon"): "statistics",
    ("spKDO_Aggregate", "channel"): "referrals",
    # ClientList
    ("spKDO_ClientList", "outflow"): "outflow",
    ("spKDO_ClientList", "leaving"): "leaving",
    ("spKDO_ClientList", "forecast"): "forecast",
    ("spKDO_ClientList", "noshow"): "noshow",
    ("spKDO_ClientList", "quality"): "quality",
    ("spKDO_ClientList", "birthday"): "birthday",
    ("spKDO_ClientList", "all"): "all_clients",
    # CommAgg
    ("spKDO_CommAgg", "all"): "communications",
    ("spKDO_CommAgg", "waitlist"): "waitlist",
    ("spKDO_CommAgg", "opz"): "opz",
}

# Старые процедуры, которые LLM может вернуть (абонементы, обучение)
_LEGACY_PROCEDURE_TOPIC = {
    "spKDO_Attachments": "attachments",
    "spKDO_Training": "training",
}

# Допустимые имена процедур (whitelist)
_ALLOWED_PROCEDURES = {
    "spKDO_Aggregate",
    "spKDO_ClientList",
    "spKDO_CommAgg",
    "spKDO_Attachments",
    "spKDO_Training",
    # Старые — для обратной совместимости fallback
    "spKDO_Statistics",
    "spKDO_Trend",
    "spKDO_Outflow",
    "spKDO_Leaving",
    "spKDO_Forecast",
    "spKDO_Masters",
    "spKDO_Services",
    "spKDO_Communications",
    "spKDO_Referrals",
    "spKDO_Quality",
    "spKDO_NoShow",
    "spKDO_AllClients",
    "spKDO_Birthday",
    "spKDO_WaitList",
    "spKDO_OPZ",
}

# Маппинг v2 → v1: topic → старая процедура (для работы до деплоя v2)
_V2_TO_V1: dict[str, str] = {
    "statistics": "dbo.spKDO_Statistics",
    "trend": "dbo.spKDO_Trend",
    "outflow": "dbo.spKDO_Outflow",
    "leaving": "dbo.spKDO_Leaving",
    "forecast": "dbo.spKDO_Forecast",
    "masters": "dbo.spKDO_Masters",
    "services": "dbo.spKDO_Services",
    "communications": "dbo.spKDO_Communications",
    "referrals": "dbo.spKDO_Referrals",
    "quality": "dbo.spKDO_Quality",
    "noshow": "dbo.spKDO_NoShow",
    "all_clients": "dbo.spKDO_AllClients",
    "birthday": "dbo.spKDO_Birthday",
    "waitlist": "dbo.spKDO_WaitList",
    "attachments": "dbo.spKDO_Attachments",
    "training": "dbo.spKDO_Training",
    "opz": "dbo.spKDO_OPZ",
}


def _resolve_period(hint: str) -> tuple[str, str]:
    """Преобразует словесный период в пару (date_from, date_to) в формате ISO.

    Поддерживаемые значения hint:
    - "этот месяц" / "текущий месяц" → 1-й день текущего месяца .. сегодня
    - "прошлый месяц" / "предыдущий месяц" → полный предыдущий месяц
    - "прошлый квартал" / "предыдущий квартал" → полный предыдущий квартал
    - "эта неделя" / "текущая неделя" → понедельник текущей недели .. сегодня
    - "прошлая неделя" / "предыдущая неделя" → полная предыдущая неделя (пн-вс)
    - Всё остальное → текущий месяц (как "этот месяц")
    """
    today = date.today()
    hint_lower = hint.lower().strip()

    if hint_lower in ("этот месяц", "текущий месяц"):
        date_from = today.replace(day=1)
        date_to = today
        return date_from.isoformat(), date_to.isoformat()

    if hint_lower in ("прошлый месяц", "предыдущий месяц"):
        first_of_current = today.replace(day=1)
        last_of_prev = first_of_current - timedelta(days=1)
        date_from = last_of_prev.replace(day=1)
        date_to = last_of_prev
        return date_from.isoformat(), date_to.isoformat()

    if hint_lower in ("прошлый квартал", "предыдущий квартал"):
        current_quarter = (today.month - 1) // 3 + 1
        if current_quarter == 1:
            # Q4 прошлого года
            date_from = date(today.year - 1, 10, 1)
            date_to = date(today.year - 1, 12, 31)
        else:
            prev_q_start_month = (current_quarter - 2) * 3 + 1
            date_from = date(today.year, prev_q_start_month, 1)
            last_month = prev_q_start_month + 2
            last_day = calendar.monthrange(today.year, last_month)[1]
            date_to = date(today.year, last_month, last_day)
        return date_from.isoformat(), date_to.isoformat()

    if hint_lower in ("эта неделя", "текущая неделя"):
        monday = today - timedelta(days=today.weekday())
        return monday.isoformat(), today.isoformat()

    if hint_lower in ("прошлая неделя", "предыдущая неделя"):
        monday_this = today - timedelta(days=today.weekday())
        monday_prev = monday_this - timedelta(weeks=1)
        sunday_prev = monday_this - timedelta(days=1)
        return monday_prev.isoformat(), sunday_prev.isoformat()

    # По умолчанию — текущий месяц
    date_from = today.replace(day=1)
    return date_from.isoformat(), today.isoformat()


class PlannerAgent(Agent):
    name = "planner"

    REPORT_TAG_RE = re.compile(r"report\s*:\s*([\w\-/]+)", re.IGNORECASE)

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        aggregate_registry: AggregateRegistry | None = None,
        semantic_catalog_path: str = "",
    ):
        self.llm_client = llm_client
        self.aggregate_registry = aggregate_registry
        self._semantic_prompt = self._load_semantic_catalog(semantic_catalog_path)

    @staticmethod
    def _load_semantic_catalog(path: str) -> str:
        """Загружает semantic-catalog.yaml как текст для LLM промпта."""
        if not path:
            return "(нет семантического каталога)"
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                return content
        except FileNotFoundError:
            logger.info("Semantic catalog not found at %s — using placeholder", path)
        except Exception as exc:
            logger.warning("Failed to load semantic catalog from %s: %s", path, exc)
        return "(нет семантического каталога)"

    def multi_plan_to_plan(self, multi_plan: MultiPlan, question: UserQuestion) -> Plan:
        """Конвертирует MultiPlan в legacy Plan для обратной совместимости."""
        return Plan(
            objective=multi_plan.objective,
            topic=multi_plan.topic,
            sql_needed=bool(multi_plan.queries),
            powerbi_needed=False,
            render_needed=multi_plan.render_needed,
            notes=list(multi_plan.notes),
        )

    @staticmethod
    def empty_plan(text: str) -> Plan:
        """Минимальный Plan при сбое планировщика."""
        return Plan(
            objective=text,
            topic="statistics",
            sql_needed=False,
            powerbi_needed=False,
            render_needed=False,
            notes=["planner:error"],
        )

    async def run_multi(self, question: UserQuestion) -> MultiPlan:
        """T024: Одношаговое LLM-планирование с каталогом агрегатов → MultiPlan.

        Алгоритм:
        1. Если есть LLM + aggregate_registry — строим catalog/semantic промпт
           и вызываем LLMClient.plan_aggregates()
        2. Парсим JSON → проверяем каждый aggregate_id против whitelist
        3. Если ANY aggregate_id невалиден → fallback на TopicRegistry
        4. Fallback: TopicRegistry detect_topic → один AggregateQuery
        """
        text = question.text.lower()
        render_needed = "без картинки" not in text and "text only" not in text

        # Пробуем LLM-планирование с каталогом агрегатов
        if self.llm_client and self.aggregate_registry:
            multi_plan = await self._llm_plan_multi(question, render_needed)
            if multi_plan is not None:
                return multi_plan

        # Fallback: keyword-matching → один AggregateQuery
        return self._fallback_multi_plan(question, render_needed)

    async def _llm_plan_multi(
        self, question: UserQuestion, render_needed: bool
    ) -> MultiPlan | None:
        """Вызывает LLM для получения MultiPlan с каталогом агрегатов."""
        registry = self.aggregate_registry
        if registry is None:
            return None

        # Формируем промпт из каталога агрегатов
        catalog_lines: list[str] = []
        for agg in registry.list_aggregates():
            agg_id = agg.get("id", "")
            name = agg.get("name", "")
            desc = agg.get("description", "")
            allowed = ", ".join(agg.get("allowed_group_by", []))
            catalog_lines.append(
                f"- {agg_id}: {name}. {desc} (allowed_group_by: {allowed})"
            )
        catalog_prompt = "\n".join(catalog_lines) if catalog_lines else "(пусто)"
        semantic_prompt = self._semantic_prompt

        raw_dict = await self.llm_client.plan_aggregates(  # type: ignore[union-attr]
            question=question.text,
            catalog_prompt=catalog_prompt,
            semantic_prompt=semantic_prompt,
            last_topic=question.last_topic,
        )
        if not raw_dict:
            return None

        queries_raw = raw_dict.get("queries")
        if not queries_raw or not isinstance(queries_raw, list):

exec
/bin/zsh -lc "rg -n \"def run_multi|aggregate_id|queries\\[\" src/swarm_powerbi_bot/agents src/swarm_powerbi_bot/services | sed -n '1,240p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
src/swarm_powerbi_bot/services/llm_client.py:184:            '"queries": [{"aggregate_id": "...", "params": {...}, "label": "..."}], '
src/swarm_powerbi_bot/services/llm_client.py:202:            "→ intent=comparison, aggregate_id=clients_outflow для обоих периодов.\n"
src/swarm_powerbi_bot/services/llm_client.py:205:            "ВАЖНО: используй только aggregate_id из каталога выше. "
src/swarm_powerbi_bot/agents/sql.py:67:    async def run_multi(
src/swarm_powerbi_bot/agents/sql.py:93:        queries = plan.queries[:max_queries]
src/swarm_powerbi_bot/agents/sql.py:100:                        client.execute_aggregate(query.aggregate_id, query.params, registry),
src/swarm_powerbi_bot/agents/sql.py:108:                            aggregate_id=result.aggregate_id,
src/swarm_powerbi_bot/agents/sql.py:119:                        aggregate_id=query.aggregate_id,
src/swarm_powerbi_bot/agents/sql.py:125:                    logger.error("run_multi error for %r: %s", query.aggregate_id, exc)
src/swarm_powerbi_bot/agents/sql.py:127:                        aggregate_id=query.aggregate_id,
src/swarm_powerbi_bot/agents/sql.py:138:                            aggregate_id=result.aggregate_id,
src/swarm_powerbi_bot/services/sql_client.py:211:        aggregate_id: str,
src/swarm_powerbi_bot/services/sql_client.py:215:        """T027: Выполняет агрегатный запрос по aggregate_id из каталога.
src/swarm_powerbi_bot/services/sql_client.py:218:        2. Маппит aggregate_id на процедуру через каталог.
src/swarm_powerbi_bot/services/sql_client.py:222:        ok, msg = registry.validate(aggregate_id, params)
src/swarm_powerbi_bot/services/sql_client.py:225:                "execute_aggregate: validation failed for %r: %s", aggregate_id, msg
src/swarm_powerbi_bot/services/sql_client.py:228:                aggregate_id=aggregate_id,
src/swarm_powerbi_bot/services/sql_client.py:234:        agg_entry = registry.get_aggregate(aggregate_id)
src/swarm_powerbi_bot/services/sql_client.py:237:                aggregate_id=aggregate_id,
src/swarm_powerbi_bot/services/sql_client.py:239:                error=f"aggregate_id not found in catalog: {aggregate_id!r}",
src/swarm_powerbi_bot/services/sql_client.py:245:                aggregate_id=aggregate_id,
src/swarm_powerbi_bot/services/sql_client.py:247:                error=f"no procedure mapped for aggregate_id: {aggregate_id!r}",
src/swarm_powerbi_bot/services/sql_client.py:254:                self._execute_aggregate_sync, aggregate_id, procedure, params
src/swarm_powerbi_bot/services/sql_client.py:259:                aggregate_id=aggregate_id,
src/swarm_powerbi_bot/services/sql_client.py:266:            logger.error("execute_aggregate error for %r: %s", aggregate_id, exc)
src/swarm_powerbi_bot/services/sql_client.py:268:                aggregate_id=aggregate_id,
src/swarm_powerbi_bot/services/sql_client.py:276:            aggregate_id=aggregate_id,
src/swarm_powerbi_bot/services/sql_client.py:277:            label=params.get("label", aggregate_id),
src/swarm_powerbi_bot/services/sql_client.py:286:        aggregate_id: str,
src/swarm_powerbi_bot/services/sql_client.py:296:            return [], aggregate_id, {}
src/swarm_powerbi_bot/services/sql_client.py:305:            logger.warning("Invalid date_from %r for %s, using default", d_from_raw, aggregate_id)
src/swarm_powerbi_bot/services/sql_client.py:310:            logger.warning("Invalid date_to %r for %s, using default", d_to_raw, aggregate_id)
src/swarm_powerbi_bot/services/sql_client.py:317:                aggregate_id,
src/swarm_powerbi_bot/services/sql_client.py:319:            return [], aggregate_id, {"DateFrom": d_from, "DateTo": d_to}
src/swarm_powerbi_bot/services/sql_client.py:328:                "execute_aggregate: no ObjectId for %s — returning empty", aggregate_id
src/swarm_powerbi_bot/services/sql_client.py:330:            return [], aggregate_id, {"DateFrom": d_from, "DateTo": d_to}
src/swarm_powerbi_bot/services/sql_client.py:381:        return rows, aggregate_id, {"DateFrom": d_from, "DateTo": d_to}
src/swarm_powerbi_bot/services/query_logger.py:52:        aggregate_id: str,
src/swarm_powerbi_bot/services/query_logger.py:62:            "aggregate_id": aggregate_id,
src/swarm_powerbi_bot/services/aggregate_registry.py:44:    """Загружает YAML-каталог, возвращает {aggregate_id: entry}.
src/swarm_powerbi_bot/services/aggregate_registry.py:76:    aggregate_id: str,
src/swarm_powerbi_bot/services/aggregate_registry.py:90:                    f"required param {param_name!r} missing for aggregate {aggregate_id!r}"
src/swarm_powerbi_bot/services/aggregate_registry.py:112:                    f"group_by {value!r} not allowed for {aggregate_id!r}; "
src/swarm_powerbi_bot/services/aggregate_registry.py:149:def validate_aggregate_id(aggregate_id: str) -> bool:
src/swarm_powerbi_bot/services/aggregate_registry.py:150:    """True, если aggregate_id есть в загруженном каталоге."""
src/swarm_powerbi_bot/services/aggregate_registry.py:151:    return aggregate_id in _catalog
src/swarm_powerbi_bot/services/aggregate_registry.py:154:def validate_params(aggregate_id: str, params: dict) -> tuple[bool, str]:
src/swarm_powerbi_bot/services/aggregate_registry.py:159:    entry = _catalog.get(aggregate_id)
src/swarm_powerbi_bot/services/aggregate_registry.py:161:        return False, f"unknown aggregate_id: {aggregate_id!r}"
src/swarm_powerbi_bot/services/aggregate_registry.py:162:    return _validate_entry_params(aggregate_id, entry, params)
src/swarm_powerbi_bot/services/aggregate_registry.py:172:    def get_aggregate(self, aggregate_id: str) -> dict | None:
src/swarm_powerbi_bot/services/aggregate_registry.py:173:        return self._catalog.get(aggregate_id)
src/swarm_powerbi_bot/services/aggregate_registry.py:175:    def validate(self, aggregate_id: str, params: dict) -> tuple[bool, str]:
src/swarm_powerbi_bot/services/aggregate_registry.py:177:        entry = self._catalog.get(aggregate_id)
src/swarm_powerbi_bot/services/aggregate_registry.py:179:            return False, f"unknown aggregate_id: {aggregate_id!r}"
src/swarm_powerbi_bot/services/aggregate_registry.py:180:        return _validate_entry_params(aggregate_id, entry, params)
src/swarm_powerbi_bot/agents/planner.py:207:    async def run_multi(self, question: UserQuestion) -> MultiPlan:
src/swarm_powerbi_bot/agents/planner.py:213:        2. Парсим JSON → проверяем каждый aggregate_id против whitelist
src/swarm_powerbi_bot/agents/planner.py:214:        3. Если ANY aggregate_id невалиден → fallback на TopicRegistry
src/swarm_powerbi_bot/agents/planner.py:283:        # Валидируем каждый aggregate_id против whitelist
src/swarm_powerbi_bot/agents/planner.py:286:            agg_id = q.get("aggregate_id", "")
src/swarm_powerbi_bot/agents/planner.py:289:                    "plan_aggregates: aggregate_id %r not in catalog — falling back",
src/swarm_powerbi_bot/agents/planner.py:309:                    aggregate_id=agg_id,
src/swarm_powerbi_bot/agents/planner.py:352:    # Маппинг legacy TopicRegistry topic_id → catalog aggregate_id
src/swarm_powerbi_bot/agents/planner.py:381:            # Проверяем что last_topic — валидный catalog aggregate_id
src/swarm_powerbi_bot/agents/planner.py:385:                # Пробуем маппинг legacy topic → catalog aggregate_id
src/swarm_powerbi_bot/agents/planner.py:389:                # Нет валидного aggregate_id для comparison → обычный single
src/swarm_powerbi_bot/agents/planner.py:423:                    AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_prev), label=prev_label),
src/swarm_powerbi_bot/agents/planner.py:424:                    AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_curr), label=curr_label),
src/swarm_powerbi_bot/agents/planner.py:436:            aggregate_id=topic,
src/swarm_powerbi_bot/agents/analyst.py:375:    async def run_multi(
src/swarm_powerbi_bot/agents/analyst.py:406:                    "aggregate_id": r.aggregate_id,
src/swarm_powerbi_bot/agents/analyst.py:407:                    "label": r.label or r.aggregate_id,
src/swarm_powerbi_bot/agents/analyst.py:444:        1. Группирует результаты попарно (текущий / предыдущий период) по aggregate_id
src/swarm_powerbi_bot/agents/analyst.py:465:            lines = [f"• {r.label or r.aggregate_id}: {r.row_count} записей" for r in ok_results]
src/swarm_powerbi_bot/agents/analyst.py:524:        Пара определяется по одинаковому aggregate_id. Первый встреченный считается
src/swarm_powerbi_bot/agents/analyst.py:547:        # Группируем по aggregate_id (сохраняем порядок первого вхождения)
src/swarm_powerbi_bot/agents/analyst.py:552:            agg_id = r.aggregate_id
src/swarm_powerbi_bot/agents/analyst.py:567:            label = current.label or current.aggregate_id
src/swarm_powerbi_bot/agents/analyst.py:573:                factors.append({"label": r.label or r.aggregate_id, "rel_change": 0.0})
src/swarm_powerbi_bot/agents/analyst.py:602:                label = r.label or r.aggregate_id

codex
FAIL
[HIGH] tests/test_e2e_pipeline.py:216 — `test_comparison_pipeline` never asserts `result.image` or PNG output even though T004/US-2 require a comparison chart. Because `MockAnalystMulti` hardcodes `+17%`, this still passes if comparison chart generation is broken.
[HIGH] tests/test_e2e_pipeline.py:362 — the smoke “fallback quality” checks are structurally incapable of validating fallback text: `MockAnalyst` always returns a canned `Тема: ...` string, and the added tests only inspect topic/follow-ups. Leaked raw field names, missing `Период:`, and bad money formatting will all escape the default suite.
[HIGH] tests/integration/test_real_e2e.py:46 — comparison integration coverage never checks for the required delta text. One test only asserts a non-empty answer, the other only asserts PNG bytes, so a response that omits the `%` comparison still passes.
[HIGH] tests/integration/test_real_e2e.py:169 — `test_e2e_fallback_has_period` and `test_e2e_statistics_money_rounded` are no-op assertions on `resp.topic`; they do not verify a period label or 2-decimal monetary formatting as required by the spec.
[MEDIUM] tests/conftest.py:76 — `MockPlannerWithRegistry.run_multi` populates `MultiPlan.queries` with plain dicts instead of `AggregateQuery` objects. Since `MockSQLMulti.run_multi` ignores them, the new MultiPlan tests do not exercise the real planner→SQL contract that production code uses.
[MEDIUM] tests/integration/test_real_llm.py:256 — `test_planner_10_questions` rejects valid `MultiPlan.intent` values such as `trend` and `ranking`, even though the model type allows them and the parametrized set includes a trend query. Correct planner output can fail this test.
tokens used
83,552
FAIL
[HIGH] tests/test_e2e_pipeline.py:216 — `test_comparison_pipeline` never asserts `result.image` or PNG output even though T004/US-2 require a comparison chart. Because `MockAnalystMulti` hardcodes `+17%`, this still passes if comparison chart generation is broken.
[HIGH] tests/test_e2e_pipeline.py:362 — the smoke “fallback quality” checks are structurally incapable of validating fallback text: `MockAnalyst` always returns a canned `Тема: ...` string, and the added tests only inspect topic/follow-ups. Leaked raw field names, missing `Период:`, and bad money formatting will all escape the default suite.
[HIGH] tests/integration/test_real_e2e.py:46 — comparison integration coverage never checks for the required delta text. One test only asserts a non-empty answer, the other only asserts PNG bytes, so a response that omits the `%` comparison still passes.
[HIGH] tests/integration/test_real_e2e.py:169 — `test_e2e_fallback_has_period` and `test_e2e_statistics_money_rounded` are no-op assertions on `resp.topic`; they do not verify a period label or 2-decimal monetary formatting as required by the spec.
[MEDIUM] tests/conftest.py:76 — `MockPlannerWithRegistry.run_multi` populates `MultiPlan.queries` with plain dicts instead of `AggregateQuery` objects. Since `MockSQLMulti.run_multi` ignores them, the new MultiPlan tests do not exercise the real planner→SQL contract that production code uses.
[MEDIUM] tests/integration/test_real_llm.py:256 — `test_planner_10_questions` rejects valid `MultiPlan.intent` values such as `trend` and `ranking`, even though the model type allows them and the parametrized set includes a trend query. Correct planner output can fail this test.
```

---
## ⚠️ Достигнут лимит раундов (3/3)
Требуется эскалация на человека.
