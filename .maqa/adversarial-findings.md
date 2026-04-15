# Adversarial Review — FAIL

**Раунд**: 1 / 3
**Дата**: 2026-04-15T16:01:38Z
**Ветка**: feature/002-fix-comparison-followup

## DeepSeek V3.2 — ERROR

```
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
session id: 019d91da-e883-70c0-839f-7c37c3cadb5b
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
Reviewing `git diff main...HEAD` against the spec in `.specify/specs/*/spec.md` first, then I’ll inspect the changed code paths for logic, security, and edge-case failures.
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
/bin/zsh -lc 'git status --short' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc 'git diff --stat main...HEAD' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 1719ms:
2026-04-15 18:55:46.403 xcodebuild[89730:107958376]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 18:55:46.627 xcodebuild[89730:107958373] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-0BC6DIfG' (errno=Operation not permitted)
2026-04-15 18:55:47.045 xcodebuild[89768:107958504]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 18:55:47.165 xcodebuild[89768:107958502] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
 .../specs/002-fix-comparison-followup/plan.md      |  47 +++++++++
 .../specs/002-fix-comparison-followup/spec.md      | 107 +++++++++++++++++++++
 .../specs/002-fix-comparison-followup/tasks.md     |  14 +++
 .../src/swarm_powerbi_bot/agents/planner.py        |  58 ++++++++++-
 .../src/swarm_powerbi_bot/services/llm_client.py   |  23 ++++-
 swarm_powerbi_bot/tests/test_planner_v2.py         |  72 ++++++++++++++
 6 files changed, 318 insertions(+), 3 deletions(-)

 succeeded in 1722ms:
2026-04-15 18:55:46.403 xcodebuild[89729:107958375]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 18:55:46.627 xcodebuild[89729:107958374] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VRPAbGBd' (errno=Operation not permitted)
2026-04-15 18:55:47.045 xcodebuild[89769:107958503]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 18:55:47.165 xcodebuild[89769:107958501] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
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
?? sql/create_kdo_procedures.sql
?? whisper/
?? ../uv.lock

codex
I have the spec location. The next step is extracting the exact diff and reading the relevant spec sections so I can map behavior changes to explicit requirements.
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
The branch includes a new spec under `.specify/specs/002-fix-comparison-followup/`, so I’m checking that alongside the planner and LLM client diffs. I need the exact contract around comparison follow-ups before judging the implementation.
exec
/bin/zsh -lc "sed -n '1,240p' .specify/specs/002-fix-comparison-followup/spec.md" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 exited 1 in 0ms:
sed: .specify/specs/002-fix-comparison-followup/spec.md: No such file or directory

exec
/bin/zsh -lc 'git diff --unified=80 main...HEAD -- src/swarm_powerbi_bot/agents/planner.py src/swarm_powerbi_bot/services/llm_client.py swarm_powerbi_bot/tests/test_planner_v2.py' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc 'git diff --name-only main...HEAD' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 1362ms:
2026-04-15 18:56:03.987 xcodebuild[90115:107959675] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VrUyspR2' (errno=Operation not permitted)
2026-04-15 18:56:04.335 xcodebuild[90118:107959716]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 18:56:04.453 xcodebuild[90118:107959715] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
swarm_powerbi_bot/specs/002-fix-comparison-followup/plan.md
swarm_powerbi_bot/specs/002-fix-comparison-followup/spec.md
swarm_powerbi_bot/specs/002-fix-comparison-followup/tasks.md
swarm_powerbi_bot/src/swarm_powerbi_bot/agents/planner.py
swarm_powerbi_bot/src/swarm_powerbi_bot/services/llm_client.py
swarm_powerbi_bot/tests/test_planner_v2.py

 succeeded in 1370ms:
2026-04-15 18:56:03.866 xcodebuild[90114:107959676]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 18:56:03.987 xcodebuild[90114:107959672] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-h10axNfx' (errno=Operation not permitted)
2026-04-15 18:56:04.335 xcodebuild[90119:107959717]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-04-15 18:56:04.453 xcodebuild[90119:107959714] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
diff --git a/swarm_powerbi_bot/src/swarm_powerbi_bot/agents/planner.py b/swarm_powerbi_bot/src/swarm_powerbi_bot/agents/planner.py
index 232b7a6..5a90c04 100644
--- a/swarm_powerbi_bot/src/swarm_powerbi_bot/agents/planner.py
+++ b/swarm_powerbi_bot/src/swarm_powerbi_bot/agents/planner.py
@@ -174,259 +174,313 @@ class PlannerAgent(Agent):
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
+            last_topic=question.last_topic,
         )
         if not raw_dict:
             return None
 
         queries_raw = raw_dict.get("queries")
         if not queries_raw or not isinstance(queries_raw, list):
             logger.warning("plan_aggregates: 'queries' is missing or empty")
             return None
 
         _ALLOWED_INTENTS = {"single", "comparison", "decomposition", "trend", "ranking"}
         raw_intent = raw_dict.get("intent", "single")
         intent = raw_intent if raw_intent in _ALLOWED_INTENTS else "single"
         if raw_intent != intent:
             logger.warning(
                 "plan_aggregates: unknown intent %r from LLM, falling back to 'single'",
                 raw_intent,
             )
 
         # T037/T038: для декомпозиции допускаем до 5 запросов; глобальный max — 10
         _MAX_QUERIES_DECOMPOSITION = 5
         _MAX_QUERIES_DEFAULT = 10
         max_queries = (
             _MAX_QUERIES_DECOMPOSITION
             if intent == "decomposition"
             else _MAX_QUERIES_DEFAULT
         )
         queries_raw = queries_raw[:max_queries]
 
         # Валидируем каждый aggregate_id против whitelist
         queries: list[AggregateQuery] = []
         for q in queries_raw:
             agg_id = q.get("aggregate_id", "")
             if not registry.get_aggregate(agg_id):
                 logger.warning(
                     "plan_aggregates: aggregate_id %r not in catalog — falling back",
                     agg_id,
                 )
                 return None  # ANY invalid → полный fallback
             raw_params = dict(q.get("params", {}))
             # Инжектим object_id из подписки пользователя, только если каталог
             # требует его (required: true). Для salon-wide агрегатов (required: false)
             # object_id намеренно не подставляем.
             if "object_id" not in raw_params and question.object_id is not None:
                 entry = registry.get_aggregate(agg_id)
                 if entry:
                     params_meta = entry.get("parameters", [])
                     obj_required = any(
                         p.get("name") == "object_id" and p.get("required", False)
                         for p in params_meta
                     )
                     if obj_required:
                         raw_params["object_id"] = question.object_id
             queries.append(
                 AggregateQuery(
                     aggregate_id=agg_id,
                     params=AggregateParams(raw_params),
                     label=q.get("label", ""),
                 )
             )
 
         if not queries:
             return None
 
         topic = raw_dict.get("topic", "statistics")
         # intent was already extracted above for query limit calculation
 
         # Разрешаем period_hint → конкретные даты для ВСЕХ интентов
         for q_obj in queries:
             period_hint = q_obj.params.get("period_hint", "")
             if period_hint and "date_from" not in q_obj.params:
                 resolved_from, resolved_to = _resolve_period(period_hint)
                 q_obj.params["date_from"] = resolved_from
                 q_obj.params["date_to"] = resolved_to
 
         # T034: для intent="comparison" убеждаемся что есть ровно 2 запроса
         if intent == "comparison":
             if len(queries) < 2:
                 logger.warning(
                     "plan_aggregates: comparison intent but only %d queries — falling back",
                     len(queries),
                 )
                 return None
 
         return MultiPlan(
             objective=question.text,
             intent=intent,
             queries=queries,
             topic=topic,
             render_needed=render_needed,
             notes=["planner_v2:llm"],
         )
 
+    _COMPARISON_KEYWORDS = {"сравни", "сравнен", "сравнить", "сравнение", "compare", "сопостав", "vs"}
+    _CLIENT_AGGREGATES = {
+        "clients_outflow", "clients_leaving", "clients_forecast",
+        "clients_noshow", "clients_quality", "clients_birthday", "clients_all",
+    }
+
     def _fallback_multi_plan(
         self, question: UserQuestion, render_needed: bool
     ) -> MultiPlan:
-        """Fallback: keyword-based TopicRegistry → один AggregateQuery."""
+        """Fallback: keyword-based TopicRegistry → AggregateQuery(s).
+
+        Определяет intent=comparison по ключевым словам и генерирует
+        2 запроса с разными периодами при наличии контекста (last_topic).
+        """
         topic = detect_topic(question.text, last_topic=question.last_topic)
+        text_lower = question.text.lower()
+
+        is_comparison = any(kw in text_lower for kw in self._COMPARISON_KEYWORDS)
+
+        if is_comparison and question.last_topic:
+            agg_id = question.last_topic
+            # Для клиентских агрегатов — group_by=status (агрегированные цифры)
+            group_by = "status" if agg_id in self._CLIENT_AGGREGATES else ""
+            today = date.today()
+            first_of_current = today.replace(day=1)
+            last_of_prev = first_of_current - timedelta(days=1)
+            first_of_prev = last_of_prev.replace(day=1)
+
+            params_prev: dict = {
+                "date_from": first_of_prev.isoformat(),
+                "date_to": last_of_prev.isoformat(),
+            }
+            params_curr: dict = {
+                "date_from": first_of_current.isoformat(),
+                "date_to": today.isoformat(),
+            }
+            if group_by:
+                params_prev["group_by"] = group_by
+                params_curr["group_by"] = group_by
+
+            _RU_MONTHS = [
+                "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
+                "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
+            ]
+            prev_label = f"{_RU_MONTHS[first_of_prev.month]} {first_of_prev.year}"
+            curr_label = f"{_RU_MONTHS[first_of_current.month]} {first_of_current.year}"
+
+            queries = [
+                AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_prev), label=prev_label),
+                AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_curr), label=curr_label),
+            ]
+            return MultiPlan(
+                objective=question.text,
+                intent="comparison",
+                queries=queries,
+                topic=agg_id,
+                render_needed=render_needed,
+                notes=["planner_v2:keyword", "comparison:fallback"],
+            )
 
-        # Формируем AggregateQuery используя topic как aggregate_id
         agg_query = AggregateQuery(
             aggregate_id=topic,
             params={},
             label=topic,
         )
 
         return MultiPlan(
             objective=question.text,
             intent="single",
             queries=[agg_query],
             topic=topic,
             render_needed=render_needed,
             notes=["planner_v2:keyword"],
         )
 
     async def run(self, question: UserQuestion) -> Plan:
         text = question.text.lower()
 
         sql_needed = "только powerbi" not in text and "only powerbi" not in text
         powerbi_needed = "только sql" not in text and "only sql" not in text
         render_needed = "без картинки" not in text and "text only" not in text
 
         # Пробуем LLM-планирование
         llm_result = await self._llm_plan(question)
         used_llm = llm_result is not None
 
         if used_llm:
             query_params = llm_result
             topic = self._derive_topic(query_params, question)
         else:
             # Fallback: keyword-matching → старые процедуры
             topic = detect_topic(question.text, last_topic=question.last_topic)
             query_params = self._fallback_params(question, topic)
 
         notes: list[str] = [f"topic:{topic}"]
         notes.append("planner:llm" if used_llm else "planner:keyword")
 
         # Флаги анализа
         if any(kw in text for kw in ("сравни", "compare", "сравнен")):
             notes.append("comparison_requested")
         if any(kw in text for kw in ("тренд", "trend", "динамик", "изменен")):
             notes.append("trend_requested")
         if any(kw in text for kw in ("прогноз", "forecast", "предсказ")):
             notes.append("forecast_requested")
         if any(kw in text for kw in ("топ", "лучш", "худш", "рейтинг", "ranking")):
             notes.append("ranking_requested")
 
         # Детекция группировки
         if any(kw in text for kw in ("по салон", "по объект", "по филиал")):
             notes.append("breakdown_by_object")
         if "по мастер" in text:
             notes.append("breakdown_by_master")
 
         # Детекция периода
         if "недел" in text:
             notes.append("period:week")
         elif "месяц" in text:
             notes.append("period:month")
         elif "квартал" in text:
             notes.append("period:quarter")
         elif "год" in text and "новый год" not in text:
             notes.append("period:year")
 
         # Если LLM не доступен: клиентские темы + сравнение → trend (fallback logic)
         if not used_llm:
             _CLIENT_TOPICS = {"outflow", "leaving", "all_clients", "noshow", "forecast"}
             if topic in _CLIENT_TOPICS and (
                 "comparison_requested" in notes or "trend_requested" in notes
             ):
                 notes.append(f"original_topic:{topic}")
                 topic = "trend"
                 query_params.procedure = get_procedure("trend")
 
         # Если v2 процедуры не задеплоены — маппим обратно на старые
         if (
             not _USE_V2
             and query_params
             and query_params.procedure
             in (
                 "spKDO_Aggregate",
diff --git a/swarm_powerbi_bot/src/swarm_powerbi_bot/services/llm_client.py b/swarm_powerbi_bot/src/swarm_powerbi_bot/services/llm_client.py
index 0a38c37..479b903 100644
--- a/swarm_powerbi_bot/src/swarm_powerbi_bot/services/llm_client.py
+++ b/swarm_powerbi_bot/src/swarm_powerbi_bot/services/llm_client.py
@@ -1,281 +1,302 @@
 from __future__ import annotations
 
 import asyncio
 import json
 import logging
 import time
 from typing import Any
 
 import httpx
 
 from ..config import Settings
 
 logger = logging.getLogger(__name__)
 
+_TOPIC_RE = __import__("re").compile(r"^[a-z][a-z0-9_]{0,63}$")
+
+
+def _sanitize_topic(topic: str) -> str:
+    """Валидирует last_topic: только a-z, 0-9, _ (до 64 символов)."""
+    if _TOPIC_RE.match(topic):
+        return topic
+    return ""
+
+
 # ── Промпт для LLM-планировщика запросов ──────────────────────
 
 _PLANNER_SYSTEM_PROMPT = """\
 Ты — планировщик SQL-запросов для дашборда салона красоты (КДО).
 Пользователь задаёт вопрос на русском. Ты собираешь запрос из компонентов.
 
 3 ПРОЦЕДУРЫ (выбери одну):
 
 1. spKDO_Aggregate — агрегация визитов/выручки из tbRecords
    group_by: total | week | month | master | service | salon | channel
    Примеры:
    - «статистика за неделю» → group_by=total
    - «тренд по неделям» → group_by=week
    - «выручка по месяцам» → group_by=month
    - «мастера за месяц» → group_by=master
    - «топ услуг» → group_by=service
    - «сравни салоны» → group_by=salon
    - «каналы привлечения» → group_by=channel
 
 2. spKDO_ClientList — список/агрегация клиентов по статусу из fnKDO_ClientStatus
    filter: all | outflow | leaving | forecast | noshow | quality | birthday
    group_by: list | status | master
    Примеры:
    - «отток за месяц» → filter=outflow, group_by=list
    - «уходящие клиенты» → filter=leaving, group_by=list
    - «прогноз визитов» → filter=forecast, group_by=list
    - «недошедшие» → filter=noshow, group_by=list
    - «контроль качества» → filter=quality, group_by=list
    - «все клиенты» → filter=all, group_by=list
    - «именинники» → filter=birthday, group_by=list
    - «отток по мастерам» → filter=outflow, group_by=master
    - «сколько в каждом статусе» → filter=all, group_by=status
    - «сравни отток по неделям» → НЕТ, используй spKDO_Aggregate group_by=week
 
 3. spKDO_CommAgg — коммуникации (звонки, обзвоны)
    reason: all | outflow | leaving | forecast | noshow | quality | birthday | waitlist | opz
    group_by: reason | result | manager | list
    Примеры:
    - «коммуникации за неделю» → reason=all, group_by=reason
    - «результаты обзвона оттока» → reason=outflow, group_by=result
    - «менеджеры по звонкам» → reason=all, group_by=manager
    - «лист ожидания» → reason=waitlist, group_by=list
    - «ОПЗ» → reason=opz, group_by=list
 
 ПАРАМЕТРЫ:
 - date_from, date_to — ISO YYYY-MM-DD
 - top — лимит строк (20)
 - master_name — имя мастера если упомянуто
 
 ПЕРИОДЫ:
 - «за неделю» → 7 дней, «за месяц» → 30 дней, «за квартал» → 90 дней
 - «за январь 2026» → 2026-01-01..2026-01-31
 - Без периода → 30 дней. Сегодня: {today}
 
 ВАЖНО:
 - «отток по мастерам» = ClientList filter=outflow group_by=master
 - «выручка по мастерам» = Aggregate group_by=master
 - «тренд/динамика выручки по неделям» = Aggregate group_by=week
 - «по неделям» → group_by=week, «по месяцам» → group_by=month (НЕ путай!)
 - Абонементы/обучение — используй старые: dbo.spKDO_Attachments, dbo.spKDO_Training
 
 КОНТЕКСТ ДИАЛОГА:
 {context}
 Если пользователь просит «сравни/покажи динамику» без уточнения темы — используй
 предыдущую тему как ориентир. Например: предыдущая тема outflow + «сравни по месяцам»
 → spKDO_Aggregate group_by=month (сравнение KPI за период, привязанное к оттоку).
 
 Ответь ТОЛЬКО JSON:
 {{"procedure": "spKDO_Aggregate", "group_by": "total", "filter": "", "reason": "", "date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD", "top": 20, "master_name": ""}}
 """
 
 def _extract_json(raw: str) -> str | None:
     """Извлекает внешний JSON-объект из ответа LLM (поддерживает вложенные {})."""
     start = raw.find("{")
     if start == -1:
         return None
     depth = 0
     for i, ch in enumerate(raw[start:], start):
         if ch == "{":
             depth += 1
         elif ch == "}":
             depth -= 1
             if depth == 0:
                 return raw[start : i + 1]
     return None
 
 
 class LLMClient:
     """Клиент для Ollama-совместимого LLM API (модель задаётся в settings.ollama_model)."""
 
     def __init__(self, settings: Settings):
         self.settings = settings
         # Circuit breaker state для plan_aggregates
         self._cb_failures: int = 0
         self._cb_open_until: float = 0.0
         self._cb_lock: asyncio.Lock = asyncio.Lock()
 
     async def plan_query(
         self, question: str, today: str, last_topic: str = ""
     ) -> dict[str, Any] | None:
         """LLM-планировщик: определяет процедуру, group_by, filter из вопроса.
 
         Возвращает dict с ключами: procedure, group_by, filter, reason,
         date_from, date_to, top, master_name.
         Или None если LLM недоступен.
         """
         if not self.settings.ollama_api_key:
             return None
 
         if last_topic:
             context = (
                 f"Предыдущая тема диалога: {last_topic}. "
                 f"Пользователь может ссылаться на неё (сравни, покажи динамику, подробнее)."
             )
         else:
             context = "Нет предыдущего контекста — первый вопрос в диалоге."
         system = _PLANNER_SYSTEM_PROMPT.format(today=today, context=context)
 
         raw = await self._raw_chat(system, question)
         if not raw:
             logger.warning("plan_query: LLM returned empty response")
             return None
 
         return self._parse_plan_json(raw)
 
     async def plan_aggregates(
         self,
         question: str,
         catalog_prompt: str,
         semantic_prompt: str,
+        last_topic: str = "",
     ) -> dict | None:
         """T025: Одношаговое LLM-планирование с каталогом агрегатов.
 
         Возвращает распарсенный JSON-dict или None при ошибке/circuit breaker.
         Timeout: settings.llm_plan_timeout (5s).
         Circuit breaker: после threshold подряд неудач → None на cooldown секунд.
         """
         if not self.settings.ollama_api_key:
             return None
 
         # Проверяем circuit breaker (под локом — потокобезопасно)
         async with self._cb_lock:
             now = time.monotonic()
             if self._cb_open_until > now:
                 logger.warning(
                     "LLM circuit breaker open: %.0fs remaining",
                     self._cb_open_until - now,
                 )
                 return None
 
         system_prompt = (
             "Ты — планировщик аналитических запросов. "
             "Ниже — каталог доступных агрегатов и семантический каталог.\n\n"
             f"КАТАЛОГ АГРЕГАТОВ:\n{catalog_prompt}\n\n"
             f"СЕМАНТИЧЕСКИЙ КАТАЛОГ:\n{semantic_prompt}\n\n"
             "Пользователь задаёт вопрос на русском. "
             "Выбери подходящие агрегаты из каталога и верни JSON:\n"
             '{"intent": "single|comparison|decomposition|trend|ranking", '
             '"queries": [{"aggregate_id": "...", "params": {...}, "label": "..."}], '
             '"topic": "statistics", "render_needed": true}\n\n'
             "ПРАВИЛА DECOMPOSITION:\n"
             "Если вопрос содержит «почему», «из-за чего», «что повлияло», «причина» "
             "или аналогичные запросы на факторный анализ — используй intent=decomposition.\n"
             "При decomposition запроси ВСЕ связанные метрики за ДВА периода:\n"
             "Пример: «почему упала выручка?» → 5 запросов:\n"
             "  1. revenue_summary за текущий период\n"
             "  2. revenue_summary за предыдущий период\n"
             "  3. client_count за текущий период\n"
             "  4. client_count за предыдущий период\n"
             "  5. avg_check (один период достаточно)\n"
             "Максимум 5 запросов при decomposition. "
             "Ставь понятный label: «Выручка (апрель)», «Клиенты (март)» и т.д.\n\n"
+            "ПРАВИЛА FOLLOW-UP:\n"
+            "Если указан last_topic — пользователь продолжает предыдущий разговор. "
+            "Используй last_topic как основу для выбора агрегата.\n"
+            "Пример: last_topic=clients_outflow, вопрос=«сравни по месяцам» "
+            "→ intent=comparison, aggregate_id=clients_outflow для обоих периодов.\n"
+            "Для comparison клиентских агрегатов (clients_*) используй group_by=status "
+            "(агрегированные цифры), НЕ group_by=list (сырой список).\n\n"
             "ВАЖНО: используй только aggregate_id из каталога выше. "
             "Ответь ТОЛЬКО JSON, без пояснений."
         )
 
         base = self.settings.ollama_base_url.rstrip("/")
         url = f"{base}/chat"
         headers = {
             "Authorization": f"Bearer {self.settings.ollama_api_key}",
             "Content-Type": "application/json",
         }
         payload: dict[str, Any] = {
             "model": self.settings.ollama_model,
             "messages": [
                 {"role": "system", "content": system_prompt},
-                {"role": "user", "content": question},
+                {"role": "user", "content": (
+                    f"{question}\nКонтекст: last_topic={_sanitize_topic(last_topic)}"
+                    if last_topic else question
+                )},
             ],
             "stream": False,
             "options": {"temperature": 0.1},
         }
 
         try:
             timeout = float(self.settings.llm_plan_timeout)
             async with httpx.AsyncClient(timeout=timeout) as client:
                 resp = await client.post(url, headers=headers, json=payload)
                 resp.raise_for_status()
                 data = resp.json()
         except Exception as exc:
             logger.error("plan_aggregates request failed: %s", exc)
             await self._record_cb_failure("request error")
             return None
 
         raw = self._extract_content(data)
         if not raw:
             logger.warning("plan_aggregates: LLM returned empty content")
             await self._record_cb_failure("empty content")
             return None
 
         result = self._parse_multiplan_json(raw)
         if result is None:
             await self._record_cb_failure("parse error")
             return None
 
         # Успех — сбрасываем счётчик ошибок (под локом)
         async with self._cb_lock:
             self._cb_failures = 0
         return result
 
     async def _record_cb_failure(self, reason: str) -> None:
         """Инкрементирует счётчик ошибок CB под локом, открывает CB при превышении порога."""
         async with self._cb_lock:
             self._cb_failures += 1
             if self._cb_failures >= self.settings.llm_circuit_breaker_threshold:
                 cooldown = self.settings.llm_circuit_breaker_cooldown
                 self._cb_open_until = time.monotonic() + cooldown
                 logger.warning(
                     "LLM circuit breaker opened for %ds after %d consecutive failures (%s)",
                     cooldown,
                     self._cb_failures,
                     reason,
                 )
 
     def _parse_multiplan_json(self, raw: str) -> dict[str, Any] | None:
         """Извлекает JSON MultiPlan из ответа LLM (поддерживает вложенные объекты)."""
         json_str = _extract_json(raw)
         if not json_str:
             logger.warning("plan_aggregates returned no JSON: %s", raw[:200])
             return None
         try:
             data = json.loads(json_str)
         except json.JSONDecodeError:
             logger.warning("plan_aggregates returned invalid JSON: %s", raw[:200])
             return None
 
         if "queries" not in data:
             logger.warning("plan_aggregates JSON missing 'queries': %s", data)
             return None
 
         return data
 
     def _parse_plan_json(self, raw: str) -> dict[str, Any] | None:
         """Извлекает JSON из ответа LLM (может быть обёрнут в markdown)."""
         json_str = _extract_json(raw)
         if not json_str:
             logger.warning("LLM planner returned no JSON: %s", raw[:200])
             return None
         try:
             data = json.loads(json_str)
         except json.JSONDecodeError:
             logger.warning("LLM planner returned invalid JSON: %s", raw[:200])
             return None
 
         if "procedure" not in data:
             logger.warning("LLM planner JSON missing 'procedure': %s", data)
             return None
 

codex
The new spec path from the diff doesn’t exist under `.specify/`, which is already a potential contract problem. I’m verifying whether the implementation is tied to an untracked/misplaced spec or whether the branch just added new behavior without updating the required spec tree.
exec
/bin/zsh -lc "rg --files | rg 'fix-comparison-followup/.*/spec\\.md|fix-comparison-followup/spec\\.md|spec\\.md"'$'"'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
specs/002-002-fix-comparison-followup/spec.md
specs/002-fix-comparison-followup/spec.md
specs/001-semantic-aggregate-layer/spec.md

codex
The diff is against files under the nested `swarm_powerbi_bot/` project, not the repo root, and the branch’s new spec lives there too. I’m reading that spec next and then tracing the changed planner fallback logic against the actual model types and tests.
exec
/bin/zsh -lc pwd in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot

exec
/bin/zsh -lc 'ls -la' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
total 496
drwxr-xr-x@ 32 zerocold  staff    1024 Apr 15 18:48 .
drwxr-xr-x  31 zerocold  staff     992 Apr 15 18:47 ..
-rw-r--r--@  1 zerocold  staff    6148 Apr 14 17:13 .DS_Store
drwxr-xr-x@  6 zerocold  staff     192 Apr 15 18:48 .claude
-rw-r--r--@  1 zerocold  staff     195 Apr 15 18:48 .dockerignore
-rw-r--r--@  1 zerocold  staff    1174 Apr 15 18:48 .env.example
drwxr-xr-x@  3 zerocold  staff      96 Apr 15 18:48 .github
-rw-r--r--@  1 zerocold  staff      46 Apr 15 18:48 .gitignore
drwxr-xr-x@  6 zerocold  staff     192 Apr 15 18:55 .maqa
drwxr-xr-x@  6 zerocold  staff     192 Apr 13 22:31 .pytest_cache
drwxr-xr-x@  5 zerocold  staff     160 Apr 15 09:09 .ruff_cache
drwxr-xr-x@ 14 zerocold  staff     448 Apr 15 18:48 .specify
drwxr-xr-x@  9 zerocold  staff     288 Apr 14 15:02 .venv
-rw-r--r--@  1 zerocold  staff    1984 Apr 15 18:48 CLAUDE.md
-rw-r--r--@  1 zerocold  staff     533 Apr 15 18:48 Dockerfile
-rw-r--r--@  1 zerocold  staff    3831 Mar 23 10:22 README.md
drwxr-xr-x@  6 zerocold  staff     192 Apr 15 18:48 catalogs
-rw-r--r--@  1 zerocold  staff    1655 Apr 15 18:48 docker-compose.test.yml
-rw-r--r--@  1 zerocold  staff    1369 Apr 15 18:48 docker-compose.yml
drwxr-xr-x@  4 zerocold  staff     128 Apr 15 18:48 docs
drwxr-xr-x@  3 zerocold  staff      96 Apr 15 17:34 logs
-rw-r--r--@  1 zerocold  staff    1706 Apr 15 18:48 maqa-config.yml
drwxr-xr-x@  3 zerocold  staff      96 Apr 13 21:24 powebi
-rw-r--r--@  1 zerocold  staff     758 Apr 15 18:48 pyproject.toml
-rw-r--r--@  1 zerocold  staff     106 Mar 23 10:22 requirements.txt
drwxr-xr-x@  5 zerocold  staff     160 Apr 15 18:48 scripts
drwxr-xr-x@  5 zerocold  staff     160 Apr 15 18:48 specs
drwxr-xr-x@  5 zerocold  staff     160 Apr 15 18:48 sql
drwxr-xr-x@  4 zerocold  staff     128 Apr 13 22:31 src
drwxr-xr-x@ 27 zerocold  staff     864 Apr 15 18:53 tests
-rw-r--r--@  1 zerocold  staff  199054 Apr 15 18:48 uv.lock
drwxr-xr-x@  6 zerocold  staff     192 Apr 13 22:47 whisper

exec
/bin/zsh -lc "sed -n '1,260p' specs/002-fix-comparison-followup/spec.md" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "sed -n '1,260p' tests/test_planner_v2.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
"""T022: Тесты PlannerAgent v2 — одношаговое LLM-планирование с каталогом агрегатов.

Покрывает:
- Mock LLM returns valid JSON → parses into MultiPlan correctly
- Mock LLM returns invalid JSON → graceful fallback (no crash)
- aggregate_id not in catalog whitelist → falls back to TopicRegistry
- Cross-domain query → multiple aggregates in plan
"""
from __future__ import annotations

import textwrap
from unittest.mock import AsyncMock

import pytest

from swarm_powerbi_bot.agents.planner import PlannerAgent
from swarm_powerbi_bot.models import MultiPlan, UserQuestion
from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry
from swarm_powerbi_bot.services.llm_client import LLMClient


# ── Fixtures ──────────────────────────────────────────────────────────────────

CATALOG_YAML = textwrap.dedent("""\
    aggregates:
      - id: revenue_total
        name: Общая выручка
        description: Суммарная выручка за период
        procedure: spKDO_Aggregate
        allowed_group_by:
          - total
          - week
          - month
      - id: outflow_clients
        name: Отток клиентов
        description: Клиенты со статусом outflow
        procedure: spKDO_ClientList
        allowed_group_by:
          - list
          - master
      - id: clients_outflow
        name: Отток клиентов (v2)
        description: Клиенты со статусом outflow
        procedure: spKDO_ClientList
        allowed_group_by:
          - list
          - status
          - master
      - id: communications_all
        name: Коммуникации
        description: Все коммуникации по типу звонка
        procedure: spKDO_CommAgg
        allowed_group_by:
          - reason
          - result
          - manager
""")


@pytest.fixture()
def catalog_path(tmp_path):
    p = tmp_path / "aggregate-catalog.yaml"
    p.write_text(CATALOG_YAML, encoding="utf-8")
    return str(p)


@pytest.fixture()
def registry(catalog_path):
    return AggregateRegistry(catalog_path)


def _parsed_or_none(json_text: str | None) -> dict | None:
    """Парсит JSON-строку или возвращает None (имитирует plan_aggregates)."""
    import json
    import re
    if not json_text:
        return None
    m = re.search(r"\{.*\}", json_text, re.DOTALL)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if "queries" not in data:
        return None
    return data


def _make_planner(llm_json: str | None, registry: AggregateRegistry) -> PlannerAgent:
    from swarm_powerbi_bot.config import Settings
    llm = LLMClient(Settings())
    # Mock plan_aggregates directly — bypasses ollama_api_key check
    llm.plan_aggregates = AsyncMock(return_value=_parsed_or_none(llm_json))
    return PlannerAgent(llm_client=llm, aggregate_registry=registry)


# ── T022-1: Valid JSON → MultiPlan ───────────────────────────────────────────

class TestValidJsonToMultiPlan:
    """Mock LLM returns valid JSON → parses into MultiPlan correctly."""

    def test_single_aggregate_returns_multiplan(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [
                {"aggregate_id": "revenue_total", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15", "group_by": "total"}, "label": "Выручка за период"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="Покажи выручку за апрель")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))

        assert isinstance(plan, MultiPlan)
        assert plan.intent == "single"
        assert len(plan.queries) == 1
        assert plan.queries[0].aggregate_id == "revenue_total"
        assert plan.queries[0].label == "Выручка за период"

    def test_multiplan_objective_set_from_question(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "revenue_total", "params": {}, "label": "Revenue"}],
            "topic": "statistics",
            "render_needed": false
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="общая выручка")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert plan.objective == "общая выручка"

    def test_multiplan_render_needed_false(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "outflow_clients", "params": {}, "label": "Outflow"}],
            "topic": "outflow",
            "render_needed": false
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="отток без картинки")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert plan.render_needed is False

    def test_multiplan_topic_preserved(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "outflow_clients", "params": {}, "label": "Отток"}],
            "topic": "outflow",
            "render_needed": true
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="отток")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert plan.topic == "outflow"

    def test_llm_note_added_on_success(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "revenue_total", "params": {}, "label": "X"}],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="статистика")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert "planner_v2:llm" in plan.notes


# ── T022-2: Invalid JSON → graceful fallback ──────────────────────────────────

class TestInvalidJsonFallback:
    """Mock LLM returns invalid JSON → graceful fallback (no crash)."""

    def test_invalid_json_returns_fallback_multiplan(self, registry):
        planner = _make_planner("это не JSON, а просто текст", registry)
        q = UserQuestion(user_id="1", text="отток за месяц")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)
        assert "planner_v2:keyword" in plan.notes

    def test_empty_llm_response_falls_back(self, registry):
        planner = _make_planner(None, registry)
        q = UserQuestion(user_id="1", text="покажи статистику")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)
        assert "planner_v2:keyword" in plan.notes

    def test_json_with_no_queries_array_falls_back(self, registry):
        planner = _make_planner('{"intent": "single", "topic": "statistics"}', registry)
        q = UserQuestion(user_id="1", text="что-то")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)

    def test_broken_json_no_exception(self, registry):
        planner = _make_planner("{broken json[[[", registry)
        q = UserQuestion(user_id="1", text="выручка")
        import asyncio
        # Must not raise
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)

    def test_null_llm_response_no_exception(self, registry):
        planner = _make_planner("", registry)
        q = UserQuestion(user_id="1", text="мастера")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)


# ── T022-3: aggregate_id not in whitelist → TopicRegistry fallback ────────────

class TestAggregateIdNotInWhitelist:
    """Если LLM вернул aggregate_id не из каталога → fallback на TopicRegistry."""

    def test_unknown_aggregate_id_triggers_fallback(self, registry):
        bad_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "not_in_catalog", "params": {}, "label": "X"}],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(bad_json, registry)
        q = UserQuestion(user_id="1", text="отток")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert "planner_v2:keyword" in plan.notes

    def test_any_invalid_aggregate_id_triggers_fallback(self, registry):
        """Если ЛЮБОЙ aggregate_id неверный — весь план → fallback."""
        mixed_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total", "params": {}, "label": "OK"},
                {"aggregate_id": "sql_injection_here", "params": {}, "label": "Bad"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(mixed_json, registry)
        q = UserQuestion(user_id="1", text="сравни выручку")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert "planner_v2:keyword" in plan.notes

    def test_empty_queries_array_fallback(self, registry):
        planner = _make_planner('{"intent": "single", "queries": [], "topic": "statistics", "render_needed": true}', registry)
        q = UserQuestion(user_id="1", text="что-то")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert "planner_v2:keyword" in plan.notes

 succeeded in 0ms:
# Feature Specification: Fix comparison follow-up intent

**Feature Branch**: `feature/002-fix-comparison-followup`
**Created**: 2026-04-15
**Status**: Draft
**Input**: Bugfix для GitHub issue #2
**Links**: https://github.com/k-p-i-bi/tg_bot/issues/2

## Описание проблемы

При follow-up вопросе «сравни по месяцам за два месяца» после вопроса об оттоке клиентов бот возвращает **сырой список клиентов** (ClientName, Phone, DaysSinceLastVisit) вместо **помесячного сравнения** агрегированных цифр оттока.

### Root cause анализ

Три точки отказа:

1. **`LLMClient.plan_aggregates()`** (`llm_client.py:140`) получает только `question.text` ("сравни по месяцам за два месяца") без `last_topic`. LLM не знает что предыдущий вопрос был об оттоке и не может выбрать правильный агрегат.

2. **`PlannerAgent._llm_plan_multi()`** (`planner.py:229`) вызывает `plan_aggregates(question=question.text, ...)` — передаёт только текст, игнорирует `question.last_topic`.

3. **`PlannerAgent._fallback_multi_plan()`** (`planner.py:346`) хардкодит `intent="single"` — даже keyword fallback не может вернуть comparison, даже если текст содержит «сравни».

## User Scenarios & Testing

### User Story 1 — Follow-up comparison по клиентским агрегатам (Priority: P1)

Пользователь спрашивает про отток, получает ответ, затем просит сравнить по месяцам. Бот должен понять контекст и вернуть помесячное сравнение оттока.

**Why this priority**: Это основной баг из issue #2 — comparison follow-up полностью сломан для клиентских тем.

**Independent Test**: Отправить два вопроса: "покажи отток" → "сравни по месяцам за два месяца". Второй ответ должен содержать агрегированные цифры за два периода.

**Acceptance Scenarios**:

1. **Given** пользователь спросил "покажи отток" и получил ответ с `topic=clients_outflow`, **When** отправляет follow-up "сравни по месяцам за два месяца" с `last_topic=clients_outflow`, **Then** бот возвращает `intent=comparison`, 2 запроса к `clients_outflow` с разными периодами (месяц 1 и месяц 2), агрегированный текст с процентом изменения.

2. **Given** пользователь спросил "покажи отток", **When** отправляет "сравни по месяцам", **Then** ответ НЕ содержит сырых данных клиентов (имена, телефоны), а содержит агрегированные числа (количество клиентов в оттоке за период A vs период B).

---

### User Story 2 — Follow-up comparison по выручке (Priority: P1)

Пользователь спрашивает про выручку, затем просит сравнить. Должен работать так же.

**Why this priority**: Выручка — самый частый запрос, comparison для неё уже частично работает, но передача last_topic улучшит точность.

**Independent Test**: "покажи выручку за март" → "а за февраль? сравни". Второй ответ — comparison chart.

**Acceptance Scenarios**:

1. **Given** `last_topic=revenue_total`, **When** "сравни с прошлым месяцем", **Then** `intent=comparison`, 2 запроса к `revenue_total`, comparison chart (image != None).

---

### User Story 3 — Keyword fallback с comparison intent (Priority: P2)

Если LLM недоступен (circuit breaker, timeout), keyword fallback должен распознавать intent=comparison по ключевым словам «сравни», «сравнение», «compare».

**Why this priority**: Без этого при LLM-отказе comparison полностью теряется.

**Independent Test**: Выключить Ollama, отправить "сравни выручку за март и февраль". Fallback должен вернуть intent=comparison.

**Acceptance Scenarios**:

1. **Given** LLM недоступен, **When** вопрос содержит "сравни" + last_topic, **Then** `_fallback_multi_plan` возвращает `intent=comparison`, 2 AggregateQuery с разными периодами.

2. **Given** LLM недоступен, **When** вопрос "сравни" без last_topic и без конкретной темы, **Then** fallback возвращает `intent=single` с `revenue_total` (безопасный default).

---

### Edge Cases

- Follow-up "сравни" без предыдущего контекста (last_topic пустой) → LLM должен попытаться определить тему из текста, fallback → revenue_total
- "Сравни по салонам" (не по времени, а по объектам) → intent=comparison с group_by=salon, НЕ два периода
- "Сравни за три месяца" → допустимо вернуть trend (intent=trend) вместо comparison
- Клиентские агрегаты с group_by=list vs group_by=status: comparison должен использовать group_by=status для агрегированных цифр, не list

## Requirements

### Functional Requirements

- **FR-001**: `LLMClient.plan_aggregates()` MUST принимать и передавать `last_topic` в LLM prompt, чтобы LLM знал контекст предыдущего вопроса
- **FR-002**: `PlannerAgent._llm_plan_multi()` MUST передавать `question.last_topic` в вызов `plan_aggregates()`
- **FR-003**: `PlannerAgent._fallback_multi_plan()` MUST определять `intent=comparison` по ключевым словам (сравни, сравнение, compare) и генерировать 2 AggregateQuery с разными периодами
- **FR-004**: При comparison для клиентских агрегатов (clients_outflow, clients_leaving и т.д.) system MUST использовать `group_by=status` (агрегированные цифры), а не `group_by=list` (сырой список)
- **FR-005**: LLM system prompt MUST содержать инструкцию: "Если last_topic указан, используй его как контекст для follow-up вопроса"

### Key Entities

- **UserQuestion**: уже содержит `last_topic: str` — используется в `_fallback_multi_plan`, но НЕ передаётся в LLM prompt
- **MultiPlan**: intent field уже поддерживает "comparison" — нет изменений в модели

## Success Criteria

### Measurable Outcomes

- **SC-001**: Follow-up "сравни по месяцам" после вопроса об оттоке возвращает intent=comparison и 2 запроса с разными периодами (тест-кейс из issue #2)
- **SC-002**: Ответ на comparison follow-up НЕ содержит сырых данных клиентов (телефонов, имён) — только агрегированные цифры
- **SC-003**: Все существующие 351 тестов проходят без регрессий
- **SC-004**: Keyword fallback при "сравни" + last_topic возвращает intent=comparison

## Assumptions

- Модель данных (UserQuestion, MultiPlan, AggregateQuery) не меняется
- LLM prompt расширяется одной строкой с last_topic — нет риска превышения контекста
- `group_by=status` поддерживается для всех `clients_*` агрегатов (проверено в каталоге: `allowed_group_by: [list, status, master]`)
- Comparison chart (matplotlib) уже поддерживает 2 набора данных — изменения только в planning слое

exec
/bin/zsh -lc "sed -n '1,420p' src/swarm_powerbi_bot/models.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "sed -n '1,420p' src/swarm_powerbi_bot/agents/planner.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
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
            logger.warning("plan_aggregates: 'queries' is missing or empty")
            return None

        _ALLOWED_INTENTS = {"single", "comparison", "decomposition", "trend", "ranking"}
        raw_intent = raw_dict.get("intent", "single")
        intent = raw_intent if raw_intent in _ALLOWED_INTENTS else "single"
        if raw_intent != intent:
            logger.warning(
                "plan_aggregates: unknown intent %r from LLM, falling back to 'single'",
                raw_intent,
            )

        # T037/T038: для декомпозиции допускаем до 5 запросов; глобальный max — 10
        _MAX_QUERIES_DECOMPOSITION = 5
        _MAX_QUERIES_DEFAULT = 10
        max_queries = (
            _MAX_QUERIES_DECOMPOSITION
            if intent == "decomposition"
            else _MAX_QUERIES_DEFAULT
        )
        queries_raw = queries_raw[:max_queries]

        # Валидируем каждый aggregate_id против whitelist
        queries: list[AggregateQuery] = []
        for q in queries_raw:
            agg_id = q.get("aggregate_id", "")
            if not registry.get_aggregate(agg_id):
                logger.warning(
                    "plan_aggregates: aggregate_id %r not in catalog — falling back",
                    agg_id,
                )
                return None  # ANY invalid → полный fallback
            raw_params = dict(q.get("params", {}))
            # Инжектим object_id из подписки пользователя, только если каталог
            # требует его (required: true). Для salon-wide агрегатов (required: false)
            # object_id намеренно не подставляем.
            if "object_id" not in raw_params and question.object_id is not None:
                entry = registry.get_aggregate(agg_id)
                if entry:
                    params_meta = entry.get("parameters", [])
                    obj_required = any(
                        p.get("name") == "object_id" and p.get("required", False)
                        for p in params_meta
                    )
                    if obj_required:
                        raw_params["object_id"] = question.object_id
            queries.append(
                AggregateQuery(
                    aggregate_id=agg_id,
                    params=AggregateParams(raw_params),
                    label=q.get("label", ""),
                )
            )

        if not queries:
            return None

        topic = raw_dict.get("topic", "statistics")
        # intent was already extracted above for query limit calculation

        # Разрешаем period_hint → конкретные даты для ВСЕХ интентов
        for q_obj in queries:
            period_hint = q_obj.params.get("period_hint", "")
            if period_hint and "date_from" not in q_obj.params:
                resolved_from, resolved_to = _resolve_period(period_hint)
                q_obj.params["date_from"] = resolved_from
                q_obj.params["date_to"] = resolved_to

        # T034: для intent="comparison" убеждаемся что есть ровно 2 запроса
        if intent == "comparison":
            if len(queries) < 2:
                logger.warning(
                    "plan_aggregates: comparison intent but only %d queries — falling back",
                    len(queries),
                )
                return None

        return MultiPlan(
            objective=question.text,
            intent=intent,
            queries=queries,
            topic=topic,
            render_needed=render_needed,
            notes=["planner_v2:llm"],
        )

    _COMPARISON_KEYWORDS = {"сравни", "сравнен", "сравнить", "сравнение", "compare", "сопостав", "vs"}
    _CLIENT_AGGREGATES = {
        "clients_outflow", "clients_leaving", "clients_forecast",
        "clients_noshow", "clients_quality", "clients_birthday", "clients_all",
    }

    def _fallback_multi_plan(
        self, question: UserQuestion, render_needed: bool
    ) -> MultiPlan:
        """Fallback: keyword-based TopicRegistry → AggregateQuery(s).

        Определяет intent=comparison по ключевым словам и генерирует
        2 запроса с разными периодами при наличии контекста (last_topic).
        """
        topic = detect_topic(question.text, last_topic=question.last_topic)
        text_lower = question.text.lower()

        is_comparison = any(kw in text_lower for kw in self._COMPARISON_KEYWORDS)

        if is_comparison and question.last_topic:
            agg_id = question.last_topic
            # Для клиентских агрегатов — group_by=status (агрегированные цифры)
            group_by = "status" if agg_id in self._CLIENT_AGGREGATES else ""
            today = date.today()
            first_of_current = today.replace(day=1)
            last_of_prev = first_of_current - timedelta(days=1)
            first_of_prev = last_of_prev.replace(day=1)

            params_prev: dict = {
                "date_from": first_of_prev.isoformat(),
                "date_to": last_of_prev.isoformat(),
            }
            params_curr: dict = {
                "date_from": first_of_current.isoformat(),
                "date_to": today.isoformat(),
            }
            if group_by:
                params_prev["group_by"] = group_by
                params_curr["group_by"] = group_by

            _RU_MONTHS = [
                "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
            ]
            prev_label = f"{_RU_MONTHS[first_of_prev.month]} {first_of_prev.year}"
            curr_label = f"{_RU_MONTHS[first_of_current.month]} {first_of_current.year}"

            queries = [
                AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_prev), label=prev_label),
                AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_curr), label=curr_label),
            ]
            return MultiPlan(
                objective=question.text,
                intent="comparison",
                queries=queries,
                topic=agg_id,
                render_needed=render_needed,
                notes=["planner_v2:keyword", "comparison:fallback"],
            )

        agg_query = AggregateQuery(
            aggregate_id=topic,
            params={},
            label=topic,
        )

        return MultiPlan(
            objective=question.text,
            intent="single",
            queries=[agg_query],
            topic=topic,
            render_needed=render_needed,
            notes=["planner_v2:keyword"],
        )

exec
/bin/zsh -lc "sed -n '1,260p' src/swarm_powerbi_bot/services/aggregate_registry.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "sed -n '1,320p' src/swarm_powerbi_bot/services/topic_registry.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
from __future__ import annotations

import datetime
import logging
import re
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyYAML is required for aggregate_registry. Install it: uv add pyyaml"
    ) from exc

logger = logging.getLogger(__name__)

# ── constants ──────────────────────────────────────────────────────────────────

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_FILTER_VALUES = frozenset(
    {"all", "outflow", "leaving", "forecast", "noshow", "quality", "birthday"}
)

_REASON_VALUES = frozenset(
    {"all", "outflow", "leaving", "forecast", "noshow", "quality", "birthday", "waitlist", "opz"}
)


# ── helpers ────────────────────────────────────────────────────────────────────


def _is_date(value: object) -> bool:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _load_catalog(path: str) -> dict[str, dict]:
    """Загружает YAML-каталог, возвращает {aggregate_id: entry}.

    Raises:
        FileNotFoundError: файл не найден
        yaml.YAMLError: невалидный YAML
        ValueError: запись без обязательного поля 'id'
    """
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.error("Catalog file not found: %s", path)
        raise
    except yaml.YAMLError as exc:
        logger.error("Invalid YAML in catalog %s: %s", path, exc)
        raise

    if not isinstance(raw, dict):
        logger.warning("Catalog %s has unexpected format, returning empty", path)
        return {}

    entries = raw.get("aggregates", [])
    result: dict[str, dict] = {}
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict) or "id" not in entry:
            raise ValueError(
                f"Catalog {path}: entry #{idx} missing required 'id' field: {entry!r}"
            )
        result[entry["id"]] = entry
    return result


def _validate_entry_params(
    aggregate_id: str,
    entry: dict,
    params: dict,
) -> tuple[bool, str]:
    """Общая валидация параметров для записи каталога."""
    allowed_group_by: list[str] = entry.get("allowed_group_by", [])

    # Проверяем наличие обязательных параметров из каталога
    catalog_params: list[dict] = entry.get("parameters", [])
    for catalog_param in catalog_params:
        if catalog_param.get("required", False):
            param_name = catalog_param.get("name", "")
            if param_name and param_name not in params:
                return False, (
                    f"required param {param_name!r} missing for aggregate {aggregate_id!r}"
                )

    for key, value in params.items():
        if key in ("date_from", "date_to"):
            if not _is_date(value):
                return False, f"{key} must be YYYY-MM-DD, got {value!r}"

        elif key == "object_id":
            if not isinstance(value, int):
                return False, f"object_id must be int, got {type(value).__name__}"

        elif key == "master_id":
            if value is not None and not isinstance(value, int):
                return (
                    False,
                    f"master_id must be int or None, got {type(value).__name__}",
                )

        elif key == "group_by":
            if value not in allowed_group_by:
                return False, (
                    f"group_by {value!r} not allowed for {aggregate_id!r}; "
                    f"allowed: {allowed_group_by}"
                )

        elif key == "filter":
            if value not in _FILTER_VALUES:
                return False, (
                    f"filter {value!r} not in allowed set {sorted(_FILTER_VALUES)}"
                )

        elif key == "reason":
            if value not in _REASON_VALUES:
                return False, (
                    f"reason {value!r} not in allowed set {sorted(_REASON_VALUES)}"
                )

        elif key in ("top_n", "top"):
            if not isinstance(value, int) or not (1 <= value <= 50):
                return False, f"{key} must be int in [1, 50], got {value!r}"

    return True, ""


# ── module-level state (populated by load_catalog()) ──────────────────────────

_catalog: dict[str, dict] = {}


def load_catalog(path: str) -> None:
    """Загружает каталог агрегатов из YAML-файла. Вызывается при старте."""
    global _catalog
    _catalog = _load_catalog(path)


# ── public functions ───────────────────────────────────────────────────────────


def validate_aggregate_id(aggregate_id: str) -> bool:
    """True, если aggregate_id есть в загруженном каталоге."""
    return aggregate_id in _catalog


def validate_params(aggregate_id: str, params: dict) -> tuple[bool, str]:
    """Валидирует params для указанного агрегата.

    Возвращает (True, "") при успехе или (False, <причина>) при ошибке.
    """
    entry = _catalog.get(aggregate_id)
    if entry is None:
        return False, f"unknown aggregate_id: {aggregate_id!r}"
    return _validate_entry_params(aggregate_id, entry, params)


# ── Registry class ─────────────────────────────────────────────────────────────


class AggregateRegistry:
    def __init__(self, catalog_path: str) -> None:
        self._catalog: dict[str, dict] = _load_catalog(catalog_path)

    def get_aggregate(self, aggregate_id: str) -> dict | None:
        return self._catalog.get(aggregate_id)

    def validate(self, aggregate_id: str, params: dict) -> tuple[bool, str]:
        """Комбинирует проверку whitelist и параметров."""
        entry = self._catalog.get(aggregate_id)
        if entry is None:
            return False, f"unknown aggregate_id: {aggregate_id!r}"
        return _validate_entry_params(aggregate_id, entry, params)

    def list_aggregates(self) -> list[dict]:
        """Возвращает все агрегаты — используется при формировании LLM-промпта."""
        return list(self._catalog.values())

 succeeded in 0ms:
"""Реестр аналитических тем КДО — маппинг вопросов на хранимые процедуры."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TopicEntry:
    topic_id: str
    procedure: str
    keywords: list[str] = field(default_factory=list)
    description: str = ""


# ──────────────────────────────────────────────
# Реестр 15 тем из модели КДО 3.2.1
# ──────────────────────────────────────────────

TOPICS: list[TopicEntry] = [
    TopicEntry(
        topic_id="all_clients",
        procedure="dbo.spKDO_AllClients",
        keywords=["база клиент", "клиентов в базе", "количество клиент", "новые клиент", "все клиент", "клиентская база"],
        description="Все клиенты — база, сегментация, количество",
    ),
    TopicEntry(
        topic_id="outflow",
        procedure="dbo.spKDO_Outflow",
        keywords=["отток", "потер", "ушедш", "не вернул", "потеряли"],
        description="Отток клиентов — кто уходит и почему",
    ),
    TopicEntry(
        topic_id="leaving",
        procedure="dbo.spKDO_Leaving",
        keywords=["уходящ", "покида", "расставан", "уход клиент", "на грани ухода"],
        description="Уходящие — клиенты на грани ухода",
    ),
    TopicEntry(
        topic_id="statistics",
        procedure="dbo.spKDO_Statistics",
        keywords=["статистик", "сводк", "итог", "показател", "общ", "kpi"],
        description="Статистика — сводные KPI-показатели",
    ),
    TopicEntry(
        topic_id="trend",
        procedure="dbo.spKDO_Trend",
        keywords=["тренд", "динамик", "рост", "падени", "изменен",
                  "сравнен", "сравни", "неделя к недел", "по неделям",
                  "по месяцам", "помесячно", "понедельно"],
        description="Тренды — динамика метрик во времени",
    ),
    TopicEntry(
        topic_id="forecast",
        procedure="dbo.spKDO_Forecast",
        keywords=["прогноз", "предсказ", "ожидаем", "план визит", "загрузк"],
        description="Прогноз визитов — загрузка мастеров",
    ),
    TopicEntry(
        topic_id="communications",
        procedure="dbo.spKDO_Communications",
        keywords=["коммуникац", "звонок", "обзвон", "сообщен", "связь с клиент"],
        description="Коммуникации — работа с клиентами",
    ),
    TopicEntry(
        topic_id="referrals",
        procedure="dbo.spKDO_Referrals",
        keywords=["реферж", "реферал", "приглаш", "рекоменда", "привёл"],
        description="Рефережи — реферальная программа",
    ),
    TopicEntry(
        topic_id="quality",
        procedure="dbo.spKDO_Quality",
        keywords=["качество", "контроль качеств", "оценк", "отзыв", "жалоб"],
        description="Контроль качества — оценки и NPS",
    ),
    TopicEntry(
        topic_id="attachments",
        procedure="dbo.spKDO_Attachments",
        keywords=["вложен", "абонемент", "подписк", "членств"],
        description="Вложения/Абонементы — подписки клиентов",
    ),
    TopicEntry(
        topic_id="birthday",
        procedure="dbo.spKDO_Birthday",
        keywords=["рожден", "именинник", "поздравлен", "день рожд"],
        description="Дни рождения — именинники и поздравления",
    ),
    TopicEntry(
        topic_id="waitlist",
        procedure="dbo.spKDO_WaitList",
        keywords=["ожидан", "лист ожидан", "очередь", "запись"],
        description="Лист ожидания — очередь клиентов",
    ),
    TopicEntry(
        topic_id="training",
        procedure="dbo.spKDO_Training",
        keywords=["обучен", "тренинг", "курс", "материал"],
        description="Обучение — обучающие материалы для мастеров",
    ),
    TopicEntry(
        topic_id="masters",
        procedure="dbo.spKDO_Masters",
        keywords=["мастер", "специалист", "сотрудник", "загрузка мастер", "персонал"],
        description="Мастера — загрузка, эффективность специалистов",
    ),
    TopicEntry(
        topic_id="services",
        procedure="dbo.spKDO_Services",
        keywords=["услуг", "выручк", "чек", "оборот", "продаж", "средний чек", "доход"],
        description="Услуги/Финансы — выручка, средний чек, популярные услуги",
    ),
    TopicEntry(
        topic_id="noshow",
        procedure="dbo.spKDO_NoShow",
        keywords=["недошедш", "не дошёл", "не дошел", "не пришёл", "не пришел", "отменил запись", "отмена записи"],
        description="Недошедшие — клиенты с отменёнными записями",
    ),
    TopicEntry(
        topic_id="opz",
        procedure="dbo.spKDO_OPZ",
        keywords=["опз", "оперативн", "оперативная запись"],
        description="ОПЗ — оперативные записи на другой день",
    ),
]

# Индекс для быстрого поиска
_TOPICS_BY_ID: dict[str, TopicEntry] = {t.topic_id: t for t in TOPICS}

DEFAULT_TOPIC = "statistics"


# Слова-модификаторы: меняют отображение, но не тему
# Если вопрос состоит ТОЛЬКО из модификаторов — это follow-up к предыдущей теме
_MODIFIER_KEYWORDS = {
    "сравнен", "сравни", "неделя к недел", "по неделям", "по месяцам",
    "помесячно", "понедельно", "динамик", "тренд", "изменен",
    "подробн", "детальн", "разбивк", "группиров",
}


def detect_topic(question: str, last_topic: str = "") -> str:
    """Определяет тему вопроса по ключевым словам (скоринг).

    Если вопрос содержит только модификаторы (сравни, по неделям)
    без явной темы — используем last_topic как контекст разговора.
    """
    text = question.lower()
    best_id = DEFAULT_TOPIC
    best_score = 0

    for entry in TOPICS:
        score = sum(1 for kw in entry.keywords if kw in text)
        if score > best_score:
            best_score = score
            best_id = entry.topic_id

    # Follow-up: вопрос без явной темы + есть предыдущий контекст
    if last_topic and last_topic in _TOPICS_BY_ID:
        # Если тема не найдена (score=0) — берём контекст
        if best_score == 0:
            return last_topic
        # Если совпал только trend по модификаторам — это follow-up
        if best_id == "trend" and best_score <= 2:
            has_real_topic = any(
                kw in text for entry in TOPICS
                if entry.topic_id != "trend"
                for kw in entry.keywords
            )
            if not has_real_topic:
                return last_topic

    # Тема не определена и нет контекста разговора — не выполняем SQL
    if best_score == 0:
        return "unknown"

    return best_id


def get_topic(topic_id: str) -> TopicEntry | None:
    return _TOPICS_BY_ID.get(topic_id)


def get_procedure(topic_id: str) -> str:
    entry = _TOPICS_BY_ID.get(topic_id)
    if entry:
        return entry.procedure
    return _TOPICS_BY_ID[DEFAULT_TOPIC].procedure


def get_description(topic_id: str) -> str:
    entry = _TOPICS_BY_ID.get(topic_id)
    return entry.description if entry else ""

exec
/bin/zsh -lc "sed -n '261,520p' tests/test_planner_v2.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:


# ── T022-4: Cross-domain query → multiple aggregates ─────────────────────────

class TestCrossDomainMultipleAggregates:
    """Cross-domain вопрос → несколько агрегатов в плане."""

    def test_two_valid_aggregates(self, registry):
        multi_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15"}, "label": "Выручка"},
                {"aggregate_id": "outflow_clients", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15"}, "label": "Отток"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(multi_json, registry)
        q = UserQuestion(user_id="1", text="покажи выручку и отток")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)
        assert plan.intent == "comparison"
        assert len(plan.queries) == 2
        ids = {aq.aggregate_id for aq in plan.queries}
        assert ids == {"revenue_total", "outflow_clients"}
        assert "planner_v2:llm" in plan.notes

    def test_three_aggregates_cross_domain(self, registry):
        multi_json = """{
            "intent": "decomposition",
            "queries": [
                {"aggregate_id": "revenue_total", "params": {}, "label": "Выручка"},
                {"aggregate_id": "outflow_clients", "params": {}, "label": "Отток"},
                {"aggregate_id": "communications_all", "params": {}, "label": "Коммуникации"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(multi_json, registry)
        q = UserQuestion(user_id="1", text="полный дашборд: выручка, отток и коммуникации")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert len(plan.queries) == 3
        assert plan.intent == "decomposition"


# ── Issue #2: Follow-up comparison intent ────────────────────────────────────

class TestFollowUpComparison:
    """Fix #2: follow-up «сравни по месяцам» должен возвращать comparison."""

    def test_followup_comparison_llm(self, registry):
        """LLM получает last_topic и возвращает comparison plan."""
        comparison_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "clients_outflow", "params": {"date_from": "2026-03-01", "date_to": "2026-03-31", "group_by": "status"}, "label": "Март"},
                {"aggregate_id": "clients_outflow", "params": {"date_from": "2026-02-01", "date_to": "2026-02-28", "group_by": "status"}, "label": "Февраль"}
            ],
            "topic": "clients_outflow",
            "render_needed": true
        }"""
        planner = _make_planner(comparison_json, registry)
        q = UserQuestion(
            user_id="1",
            text="сравни по месяцам за два месяца",
            last_topic="clients_outflow",
        )
        import asyncio
        plan = asyncio.run(planner.run_multi(q))

        assert plan.intent == "comparison"
        assert len(plan.queries) == 2
        assert all(aq.aggregate_id == "clients_outflow" for aq in plan.queries)
        # Проверяем что last_topic был передан в plan_aggregates
        call_kwargs = planner.llm_client.plan_aggregates.call_args
        assert call_kwargs is not None
        assert call_kwargs.kwargs.get("last_topic") == "clients_outflow"

    def test_followup_comparison_fallback(self, registry):
        """Без LLM: «сравни» + last_topic → comparison с 2 запросами."""
        planner = _make_planner(None, registry)  # LLM unavailable
        q = UserQuestion(
            user_id="1",
            text="сравни по месяцам за два месяца",
            last_topic="clients_outflow",
        )
        import asyncio
        plan = asyncio.run(planner.run_multi(q))

        assert plan.intent == "comparison"
        assert len(plan.queries) == 2
        assert all(aq.aggregate_id == "clients_outflow" for aq in plan.queries)
        # Клиентский агрегат → group_by=status (не list)
        for aq in plan.queries:
            assert aq.params.get("group_by") == "status"
        assert "comparison:fallback" in plan.notes

    def test_followup_comparison_no_context(self, registry):
        """«сравни» без last_topic → fallback single (нет контекста для comparison)."""
        planner = _make_planner(None, registry)
        q = UserQuestion(user_id="1", text="сравни что-то")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))

        assert isinstance(plan, MultiPlan)
        # Без контекста topic_registry вернёт unknown → single
        assert plan.intent == "single"

exec
/bin/zsh -lc "rg -n \"comparison:fallback|last_topic|plan_aggregates\\(\" tests src/swarm_powerbi_bot | sed -n '1,220p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
src/swarm_powerbi_bot/services/topic_registry.py:141:def detect_topic(question: str, last_topic: str = "") -> str:
src/swarm_powerbi_bot/services/topic_registry.py:145:    без явной темы — используем last_topic как контекст разговора.
src/swarm_powerbi_bot/services/topic_registry.py:158:    if last_topic and last_topic in _TOPICS_BY_ID:
src/swarm_powerbi_bot/services/topic_registry.py:161:            return last_topic
src/swarm_powerbi_bot/services/topic_registry.py:170:                return last_topic
src/swarm_powerbi_bot/services/llm_client.py:19:    """Валидирует last_topic: только a-z, 0-9, _ (до 64 символов)."""
src/swarm_powerbi_bot/services/llm_client.py:123:        self, question: str, today: str, last_topic: str = ""
src/swarm_powerbi_bot/services/llm_client.py:134:        if last_topic:
src/swarm_powerbi_bot/services/llm_client.py:136:                f"Предыдущая тема диалога: {last_topic}. "
src/swarm_powerbi_bot/services/llm_client.py:150:    async def plan_aggregates(
src/swarm_powerbi_bot/services/llm_client.py:155:        last_topic: str = "",
src/swarm_powerbi_bot/services/llm_client.py:199:            "Если указан last_topic — пользователь продолжает предыдущий разговор. "
src/swarm_powerbi_bot/services/llm_client.py:200:            "Используй last_topic как основу для выбора агрегата.\n"
src/swarm_powerbi_bot/services/llm_client.py:201:            "Пример: last_topic=clients_outflow, вопрос=«сравни по месяцам» "
src/swarm_powerbi_bot/services/llm_client.py:220:                    f"{question}\nКонтекст: last_topic={_sanitize_topic(last_topic)}"
src/swarm_powerbi_bot/services/llm_client.py:221:                    if last_topic else question
src/swarm_powerbi_bot/models.py:13:    last_topic: str = ""  # Тема предыдущего вопроса (для контекста разговора)
tests/test_llm_planner.py:106:            UserQuestion(user_id="1", text="сравни по неделям", last_topic="outflow"),
tests/test_llm_planner.py:222:            UserQuestion(user_id="1", text="подробнее", last_topic="outflow"),
tests/test_circuit_breaker.py:47:                result = await client.plan_aggregates("вопрос", "каталог", "семантика")
tests/test_circuit_breaker.py:59:            result = await client.plan_aggregates("вопрос", "каталог", "семантика")
tests/test_circuit_breaker.py:69:            result = await client.plan_aggregates("вопрос", "каталог", "семантика")
tests/test_circuit_breaker.py:81:            result = await client.plan_aggregates("вопрос", "каталог", "семантика")
tests/test_circuit_breaker.py:90:            result = await client.plan_aggregates("вопрос", "каталог", "семантика")
tests/test_planner_v2.py:314:        """LLM получает last_topic и возвращает comparison plan."""
tests/test_planner_v2.py:328:            last_topic="clients_outflow",
tests/test_planner_v2.py:336:        # Проверяем что last_topic был передан в plan_aggregates
tests/test_planner_v2.py:339:        assert call_kwargs.kwargs.get("last_topic") == "clients_outflow"
tests/test_planner_v2.py:342:        """Без LLM: «сравни» + last_topic → comparison с 2 запросами."""
tests/test_planner_v2.py:347:            last_topic="clients_outflow",
tests/test_planner_v2.py:358:        assert "comparison:fallback" in plan.notes
tests/test_planner_v2.py:361:        """«сравни» без last_topic → fallback single (нет контекста для comparison)."""
tests/test_context_switching.py:5:- Использует last_topic для follow-up вопросов
tests/test_context_switching.py:19:        topic = detect_topic("сравни месяц к месяцу", last_topic="outflow")
tests/test_context_switching.py:23:        topic = detect_topic("покажи по неделям", last_topic="outflow")
tests/test_context_switching.py:27:        topic = detect_topic("подробнее", last_topic="masters")
tests/test_context_switching.py:31:        topic = detect_topic("по месяцам за квартал", last_topic="services")
tests/test_context_switching.py:35:        topic = detect_topic("покажи динамику", last_topic="leaving")
tests/test_context_switching.py:40:        topic = detect_topic("разбивка по категориям", last_topic="quality")
tests/test_context_switching.py:50:        topic = detect_topic("покажи мастеров за неделю", last_topic="outflow")
tests/test_context_switching.py:54:        topic = detect_topic("какая выручка за месяц?", last_topic="outflow")
tests/test_context_switching.py:58:        topic = detect_topic("покажи отток", last_topic="masters")
tests/test_context_switching.py:62:        topic = detect_topic("контроль качества за неделю", last_topic="statistics")
tests/test_context_switching.py:66:        topic = detect_topic("кто не дошёл?", last_topic="outflow")
tests/test_context_switching.py:73:    """Без last_topic модификаторы идут в trend, остальное в statistics."""
tests/test_context_switching.py:95:        topic = detect_topic("", last_topic="outflow")
tests/test_context_switching.py:100:        topic = detect_topic("за последнюю неделю", last_topic="outflow")
tests/test_context_switching.py:103:    def test_invalid_last_topic_ignored(self):
tests/test_context_switching.py:104:        # invalid last_topic не попадает в _TOPICS_BY_ID, поэтому контекст не используется.
tests/test_context_switching.py:106:        topic = detect_topic("привет", last_topic="nonexistent_topic")
tests/test_context_switching.py:111:        topic = detect_topic("тренд выручки", last_topic="outflow")
tests/integration/test_real_e2e.py:90:        _question("а за февраль?", last_topic=topic),
tests/test_e2e_pipeline.py:114:            UserQuestion(user_id="1", text="подробнее по неделям", last_topic="outflow"),
src/swarm_powerbi_bot/telegram_bot.py:227:        # last_topic для контекста разговора (follow-up вопросы)
src/swarm_powerbi_bot/telegram_bot.py:228:        last_topic = ""
src/swarm_powerbi_bot/telegram_bot.py:230:            last_topic = user_data.get("last_topic", "")
src/swarm_powerbi_bot/telegram_bot.py:234:                         last_topic=last_topic),
src/swarm_powerbi_bot/telegram_bot.py:239:            user_data["last_topic"] = response.topic
src/swarm_powerbi_bot/agents/planner.py:212:           и вызываем LLMClient.plan_aggregates()
src/swarm_powerbi_bot/agents/planner.py:250:        raw_dict = await self.llm_client.plan_aggregates(  # type: ignore[union-attr]
src/swarm_powerbi_bot/agents/planner.py:254:            last_topic=question.last_topic,
src/swarm_powerbi_bot/agents/planner.py:359:        2 запроса с разными периодами при наличии контекста (last_topic).
src/swarm_powerbi_bot/agents/planner.py:361:        topic = detect_topic(question.text, last_topic=question.last_topic)
src/swarm_powerbi_bot/agents/planner.py:366:        if is_comparison and question.last_topic:
src/swarm_powerbi_bot/agents/planner.py:367:            agg_id = question.last_topic
src/swarm_powerbi_bot/agents/planner.py:404:                notes=["planner_v2:keyword", "comparison:fallback"],
src/swarm_powerbi_bot/agents/planner.py:438:            topic = detect_topic(question.text, last_topic=question.last_topic)
src/swarm_powerbi_bot/agents/planner.py:527:            last_topic=question.last_topic,
src/swarm_powerbi_bot/agents/planner.py:584:            raw, detect_topic(question.text, last_topic=question.last_topic)

codex
The risky part now is whether the new fallback uses the same topic namespace as the rest of the app. I’m tracing `last_topic` from Telegram response storage through planner, SQL execution, and rendering to see whether `clients_outflow` is even a valid runtime topic outside the LLM path.
exec
/bin/zsh -lc "sed -n '1,320p' src/swarm_powerbi_bot/services/chart_renderer.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "sed -n '1,320p' src/swarm_powerbi_bot/orchestrator.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "sed -n '1,360p' src/swarm_powerbi_bot/agents/sql.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
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
        multi_results: list[AggregateResult] = []
        if (
            multi_plan
            and multi_plan.queries
            and self.aggregate_registry is not None
            and "planner_v2:keyword" not in (multi_plan.notes or [])
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
        if has_multi_ok:
            sql_insight = SQLInsight(rows=[], summary="skipped: multi_results available")
            pbi_insight = await self._run_pbi(question, plan, diagnostics)
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
                    # Подставляем label из запроса (приоритет над label из результата)
                    effective_label = query.label or result.label
                    if effective_label != result.label:
                        result = AggregateResult(
                            aggregate_id=result.aggregate_id,
                            label=effective_label,
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
"""Рендеринг графиков из SQL-данных для отправки в Telegram.

Поддерживает: bar, horizontal bar, line, pie, table.
Автоматически выбирает тип графика по теме и данным.
"""
from __future__ import annotations

import io
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    HAS_MPL = True
except ImportError:  # pragma: no cover
    HAS_MPL = False

# Русские шрифты: пробуем DejaVu Sans (есть в Docker)
if HAS_MPL:
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

# ── Маппинг тем → предпочтительный тип графика ──────────────

_TOPIC_CHART: dict[str, str] = {
    "statistics": "bar",
    "trend": "line",
    "forecast": "hbar",
    "outflow": "hbar",
    "leaving": "hbar",
    "communications": "bar",
    "referrals": "pie",
    "quality": "bar",
    "masters": "hbar",
    "services": "hbar",
    "noshow": "hbar",
    "opz": "bar",
    "attachments": "bar",
    "training": "hbar",
    "all_clients": "bar",
    "birthday": "table_only",
    "waitlist": "table_only",
}


def choose_chart_type(topic: str, rows: list[dict[str, Any]]) -> str:
    """Выбирает тип графика по теме и данным."""
    return _TOPIC_CHART.get(topic, "bar")


def render_chart(
    topic: str,
    rows: list[dict[str, Any]],
    params: dict[str, Any],
    *,
    title: str = "",
) -> bytes | None:
    """Рендерит PNG-график из SQL-результата. Возвращает bytes или None."""
    if not HAS_MPL or not rows:
        return None

    chart_type = choose_chart_type(topic, rows)

    try:
        if chart_type == "table_only":
            return _render_table(rows, params, title)
        elif chart_type == "line":
            return _render_line(rows, params, title)
        elif chart_type == "pie":
            return _render_pie(rows, params, title)
        elif chart_type == "hbar":
            return _render_hbar(rows, params, title)
        else:
            return _render_bar(rows, params, title)
    except Exception:
        logger.exception("Chart render failed for topic=%s", topic)
        return None


def _period_label(params: dict[str, Any]) -> str:
    """Формирует подпись периода."""
    d_from = params.get("DateFrom")
    d_to = params.get("DateTo")
    if d_from and d_to:
        return f"{d_from} — {d_to}"
    return ""


def _auto_title(topic: str, params: dict[str, Any], override: str) -> str:
    if override:
        return override
    from .topic_registry import get_description
    desc = get_description(topic)
    period = _period_label(params)
    if period:
        return f"{desc}\n{period}"
    return desc


# Предпочтительная value-колонка по теме (что осмысленнее показывать)
_PREFERRED_VALUE: dict[str, str] = {
    "outflow": "TotalSpent",
    "leaving": "TotalSpent",
    "forecast": "TotalSpent",
    "noshow": "TotalVisits",
    "masters": "Revenue",
    "services": "Revenue",
    "all_clients": "TotalVisits",
    "quality": "TotalVisits",
}


def _pick_label_value(
    rows: list[dict[str, Any]], topic: str = "",
) -> tuple[str, str]:
    """Автоматически выбирает колонку для подписей и значений."""
    if not rows:
        return "", ""
    keys = list(rows[0].keys())

    # Для подписей: первая текстовая колонка
    label_col = ""
    for k in keys:
        val = rows[0].get(k)
        if isinstance(val, str) and k not in ("SalonName", "Phone"):
            label_col = k
            break

    # Для значений: предпочтительная колонка по теме, иначе первая числовая
    value_col = ""
    preferred = _PREFERRED_VALUE.get(topic, "")
    if preferred and preferred in keys:
        val = rows[0].get(preferred)
        if isinstance(val, (int, float)):
            value_col = preferred

    if not value_col:
        skip = {"ObjectId", "MasterId", "ClientId", "Id", "CRMId", "Top",
                "DaysSinceLastVisit", "DaysOverdue", "ServicePeriodDays"}
        for k in keys:
            val = rows[0].get(k)
            if isinstance(val, (int, float)) and k not in skip:
                value_col = k
                break

    return label_col, value_col


def _pick_multi_values(rows: list[dict[str, Any]]) -> list[str]:
    """Для bar-графиков со статистикой: все числовые колонки."""
    if not rows:
        return []
    skip = {"ObjectId", "MasterId", "ClientId", "Id", "CRMId", "Top"}
    return [
        k for k in rows[0].keys()
        if isinstance(rows[0].get(k), (int, float)) and k not in skip
    ]


def _format_number(n: float) -> str:
    """Форматирует числа для подписей: 1234567 → 1.2M, 12345 → 12.3K."""
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if abs(n) >= 10_000:
        return f"{n / 1_000:.1f}K"
    if isinstance(n, float) and n != int(n):
        return f"{n:.1f}"
    return str(int(n))


# ── Рендереры ────────────────────────────────────────────────

def _render_bar(rows: list[dict[str, Any]], params: dict[str, Any], title: str) -> bytes:
    """Вертикальная столбчатая диаграмма."""
    # Для Statistics: несколько метрик в одной строке
    if len(rows) == 1:
        return _render_single_row_bar(rows[0], params, title)

    label_col, value_col = _pick_label_value(rows, params.get("topic", ""))
    if not label_col or not value_col:
        return _render_single_row_bar(rows[0], params, title)

    labels = [str(r.get(label_col, ""))[:20] for r in rows[:15]]
    values = [float(r.get(value_col, 0) or 0) for r in rows[:15]]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(labels)), values, color="#4472C4")

    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                _format_number(v), ha="center", va="bottom", fontsize=8)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel(value_col)
    ax.set_title(_auto_title(params.get("topic", ""), params, title), fontsize=11)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: _format_number(x)))

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_single_row_bar(row: dict[str, Any], params: dict[str, Any], title: str) -> bytes:
    """Одна строка с несколькими метриками → группа столбцов."""
    skip = {"SalonName", "ObjectId", "MasterId", "ClientId", "Top"}
    metrics = {k: float(v) for k, v in row.items()
               if isinstance(v, (int, float)) and k not in skip and v}
    if not metrics:
        metrics = {"Нет данных": 0}

    labels = list(metrics.keys())[:10]
    values = list(metrics.values())[:10]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(labels)), values, color="#4472C4")

    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                _format_number(v), ha="center", va="bottom", fontsize=9)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_title(_auto_title(params.get("topic", ""), params, title), fontsize=11)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: _format_number(x)))

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_hbar(rows: list[dict[str, Any]], params: dict[str, Any], title: str) -> bytes:
    """Горизонтальная столбчатая диаграмма (для рейтингов/списков)."""
    label_col, value_col = _pick_label_value(rows, params.get("topic", ""))
    if not label_col or not value_col:
        if rows:
            return _render_single_row_bar(rows[0], params, title)
        return _empty_chart(params, title)

    labels = [str(r.get(label_col, ""))[:25] for r in rows[:15]]
    values = [float(r.get(value_col, 0) or 0) for r in rows[:15]]

    # Обратный порядок: самый большой сверху
    labels.reverse()
    values.reverse()

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.4)))
    bars = ax.barh(range(len(labels)), values, color="#4472C4")

    for bar, v in zip(bars, values):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                f" {_format_number(v)}", ha="left", va="center", fontsize=9)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel(value_col)
    ax.set_title(_auto_title(params.get("topic", ""), params, title), fontsize=11)

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_line(rows: list[dict[str, Any]], params: dict[str, Any], title: str) -> bytes:
    """Линейный график (тренды)."""
    # Ищем временную колонку
    time_col = ""
    for k in ("WeekEnd", "MonthEnd", "DateFrom", "Date"):
        if k in rows[0]:
            time_col = k
            break

    value_cols = _pick_multi_values(rows)
    if not time_col or not value_cols:
        return _render_bar(rows, params, title)

    x_labels = [str(r.get(time_col, ""))[:10] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5"]

    for i, vc in enumerate(value_cols[:3]):
        values = [float(r.get(vc, 0) or 0) for r in rows]
        ax.plot(range(len(x_labels)), values, marker="o", markersize=4,
                label=vc, color=colors[i % len(colors)])

    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=8)
    ax.legend(fontsize=9)
    ax.set_title(_auto_title("trend", params, title), fontsize=11)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: _format_number(x)))
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_pie(rows: list[dict[str, Any]], params: dict[str, Any], title: str) -> bytes:
    """Круговая диаграмма (рефережи, каналы)."""
    label_col, value_col = _pick_label_value(rows, params.get("topic", ""))
    if not label_col or not value_col:
        return _render_bar(rows, params, title)

    data = [(str(r.get(label_col, ""))[:20], float(r.get(value_col, 0) or 0))
            for r in rows[:8]]
    data = [(lbl, val) for lbl, val in data if val > 0]

    if not data:
        return _empty_chart(params, title)

    labels, values = zip(*data)

    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Set3.colors[:len(labels)]
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=140, textprops={"fontsize": 9},

exec
/bin/zsh -lc "rg -n \"response\\.topic|last_topic|aggregate_id|MultiPlan|comparison\" src/swarm_powerbi_bot tests | sed -n '1,260p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
tests/test_security.py:1:"""T023: Security тесты — SQL-инъекции, whitelist aggregate_id, валидация параметров.
tests/test_security.py:5:- aggregate_id not in whitelist → rejected
tests/test_security.py:76:    def test_sql_injection_in_aggregate_id_rejected(self, registry):
tests/test_security.py:77:        """aggregate_id с SQL-инъекцией отклоняется whitelist-ом."""
tests/test_security.py:81:            assert "unknown aggregate_id" in msg
tests/test_security.py:108:# ── aggregate_id whitelist ────────────────────────────────────────────────────
tests/test_security.py:111:    """aggregate_id не из whitelist → rejected."""
tests/test_security.py:120:        assert "unknown aggregate_id" in msg
tests/test_security.py:135:        """dbo.spKDO_Aggregate не в whitelist — только aggregate_id из каталога."""
tests/test_security.py:140:        """Все aggregate_id из каталога должны проходить whitelist."""
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
src/swarm_powerbi_bot/services/llm_client.py:19:    """Валидирует last_topic: только a-z, 0-9, _ (до 64 символов)."""
src/swarm_powerbi_bot/services/llm_client.py:123:        self, question: str, today: str, last_topic: str = ""
src/swarm_powerbi_bot/services/llm_client.py:134:        if last_topic:
src/swarm_powerbi_bot/services/llm_client.py:136:                f"Предыдущая тема диалога: {last_topic}. "
src/swarm_powerbi_bot/services/llm_client.py:155:        last_topic: str = "",
src/swarm_powerbi_bot/services/llm_client.py:183:            '{"intent": "single|comparison|decomposition|trend|ranking", '
src/swarm_powerbi_bot/services/llm_client.py:184:            '"queries": [{"aggregate_id": "...", "params": {...}, "label": "..."}], '
src/swarm_powerbi_bot/services/llm_client.py:199:            "Если указан last_topic — пользователь продолжает предыдущий разговор. "
src/swarm_powerbi_bot/services/llm_client.py:200:            "Используй last_topic как основу для выбора агрегата.\n"
src/swarm_powerbi_bot/services/llm_client.py:201:            "Пример: last_topic=clients_outflow, вопрос=«сравни по месяцам» "
src/swarm_powerbi_bot/services/llm_client.py:202:            "→ intent=comparison, aggregate_id=clients_outflow для обоих периодов.\n"
src/swarm_powerbi_bot/services/llm_client.py:203:            "Для comparison клиентских агрегатов (clients_*) используй group_by=status "
src/swarm_powerbi_bot/services/llm_client.py:205:            "ВАЖНО: используй только aggregate_id из каталога выше. "
src/swarm_powerbi_bot/services/llm_client.py:220:                    f"{question}\nКонтекст: last_topic={_sanitize_topic(last_topic)}"
src/swarm_powerbi_bot/services/llm_client.py:221:                    if last_topic else question
src/swarm_powerbi_bot/services/llm_client.py:270:        """Извлекает JSON MultiPlan из ответа LLM (поддерживает вложенные объекты)."""
tests/test_composition.py:19:from swarm_powerbi_bot.models import AggregateQuery, AggregateResult, MultiPlan, UserQuestion
tests/test_composition.py:89:def _make_decomposition_plan(queries: list[AggregateQuery]) -> MultiPlan:
tests/test_composition.py:90:    return MultiPlan(
tests/test_composition.py:110:                {"aggregate_id": "revenue_summary", "params": {"period_hint": "текущий месяц"}, "label": "Выручка (апрель)"},
tests/test_composition.py:111:                {"aggregate_id": "revenue_summary", "params": {"period_hint": "прошлый месяц"}, "label": "Выручка (март)"},
tests/test_composition.py:112:                {"aggregate_id": "client_count", "params": {"period_hint": "текущий месяц"}, "label": "Клиенты (апрель)"},
tests/test_composition.py:113:                {"aggregate_id": "client_count", "params": {"period_hint": "прошлый месяц"}, "label": "Клиенты (март)"},
tests/test_composition.py:122:        assert isinstance(plan, MultiPlan)
tests/test_composition.py:132:                {"aggregate_id": "revenue_summary", "params": {}, "label": "Выручка (апрель)"},
tests/test_composition.py:133:                {"aggregate_id": "revenue_summary", "params": {}, "label": "Выручка (март)"},
tests/test_composition.py:134:                {"aggregate_id": "client_count", "params": {}, "label": "Клиенты (апрель)"},
tests/test_composition.py:135:                {"aggregate_id": "client_count", "params": {}, "label": "Клиенты (март)"},
tests/test_composition.py:136:                {"aggregate_id": "avg_check", "params": {}, "label": "Средний чек"},
tests/test_composition.py:147:        agg_ids = [aq.aggregate_id for aq in plan.queries]
tests/test_composition.py:157:                {"aggregate_id": "revenue_summary", "params": {}, "label": "Выручка (апрель)"},
tests/test_composition.py:158:                {"aggregate_id": "revenue_summary", "params": {}, "label": "Выручка (март)"},
tests/test_composition.py:182:                {"aggregate_id": "revenue_summary", "params": {}, "label": f"q{i}"}
tests/test_composition.py:195:        """Для intent=comparison/ranking LLM может вернуть до 10 запросов."""
tests/test_composition.py:197:            "intent": "comparison",
tests/test_composition.py:199:                {"aggregate_id": "revenue_summary", "params": {}, "label": f"q{i}"}
tests/test_composition.py:216:                {"aggregate_id": "revenue_summary", "params": {}, "label": f"q{i}"}
tests/test_composition.py:236:        aggregate_id: str,
tests/test_composition.py:241:            aggregate_id=aggregate_id,
tests/test_composition.py:261:            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
tests/test_composition.py:283:            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
tests/test_composition.py:306:            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
tests/test_composition.py:323:            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
tests/test_composition.py:371:                aggregate_id="revenue_summary",
tests/test_composition.py:379:                aggregate_id="client_count",
tests/test_composition.py:388:            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
tests/test_composition.py:402:                aggregate_id="revenue_summary",
tests/test_composition.py:409:                aggregate_id="client_count",
tests/test_composition.py:418:            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
tests/test_composition.py:432:                aggregate_id="revenue_summary",
tests/test_composition.py:439:                aggregate_id="revenue_summary",
tests/test_composition.py:447:            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
src/swarm_powerbi_bot/services/query_logger.py:52:        aggregate_id: str,
src/swarm_powerbi_bot/services/query_logger.py:62:            "aggregate_id": aggregate_id,
src/swarm_powerbi_bot/services/chart_renderer.py:407:def render_comparison(
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
src/swarm_powerbi_bot/services/sql_client.py:439:            # salon допускает без ObjectId (cross-salon comparison)
tests/test_e2e_pipeline.py:114:            UserQuestion(user_id="1", text="подробнее по неделям", last_topic="outflow"),
tests/test_e2e_pipeline.py:155:    def test_comparison_note(self):
tests/test_e2e_pipeline.py:160:        assert "comparison_requested" in plan.notes
tests/test_llm_planner.py:106:            UserQuestion(user_id="1", text="сравни по неделям", last_topic="outflow"),
tests/test_llm_planner.py:222:            UserQuestion(user_id="1", text="подробнее", last_topic="outflow"),
tests/test_llm_planner.py:226:    def test_no_llm_comparison_switches_to_trend(self):
tests/test_llm_planner.py:232:        assert "comparison_requested" in plan.notes
src/swarm_powerbi_bot/services/topic_registry.py:141:def detect_topic(question: str, last_topic: str = "") -> str:
src/swarm_powerbi_bot/services/topic_registry.py:145:    без явной темы — используем last_topic как контекст разговора.
src/swarm_powerbi_bot/services/topic_registry.py:158:    if last_topic and last_topic in _TOPICS_BY_ID:
src/swarm_powerbi_bot/services/topic_registry.py:161:            return last_topic
src/swarm_powerbi_bot/services/topic_registry.py:170:                return last_topic
tests/test_planner.py:17:    assert "comparison_requested" in plan.notes
tests/test_data_accuracy.py:173:        result = AggregateResult(aggregate_id="test", status="ok", error="stale")
tests/test_data_accuracy.py:180:        result = AggregateResult(aggregate_id="test", status="error", error="timeout")
tests/test_data_accuracy.py:188:        result = AggregateResult(aggregate_id="test", rows=rows)
tests/test_query_logger.py:40:            aggregate_id="revenue_by_master",
tests/test_query_logger.py:60:        required = {"timestamp", "user_id", "aggregate_id", "params", "duration_ms", "row_count", "status"}
tests/test_query_logger.py:76:    def test_aggregate_id_recorded(self, logger, log_file):
tests/test_query_logger.py:79:        assert entry["aggregate_id"] == "revenue_by_master"
tests/test_query_logger.py:115:            aggregate_id="revenue_by_master",
tests/test_comparison.py:25:    MultiPlan,
tests/test_comparison.py:29:from swarm_powerbi_bot.services.chart_renderer import HAS_MPL, render_comparison
tests/test_comparison.py:104:    def test_comparison_intent_produces_two_queries(self, registry):
tests/test_comparison.py:106:            "intent": "comparison",
tests/test_comparison.py:108:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:111:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:122:        assert isinstance(plan, MultiPlan)
tests/test_comparison.py:123:        assert plan.intent == "comparison"
tests/test_comparison.py:126:        assert plan.queries[0].aggregate_id == "revenue_total"
tests/test_comparison.py:127:        assert plan.queries[1].aggregate_id == "revenue_total"
tests/test_comparison.py:129:    def test_comparison_queries_have_different_date_ranges(self, registry):
tests/test_comparison.py:131:            "intent": "comparison",
tests/test_comparison.py:133:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:136:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:152:    def test_comparison_with_single_query_falls_back(self, registry):
tests/test_comparison.py:153:        """Если comparison intent но только 1 запрос → fallback на keyword."""
tests/test_comparison.py:155:            "intent": "comparison",
tests/test_comparison.py:157:                {"aggregate_id": "revenue_total", "params": {}, "label": "Один"}
tests/test_comparison.py:237:    def test_period_hint_resolved_in_comparison_plan(self, registry):
tests/test_comparison.py:238:        """period_hint в params → разрешается в date_from/date_to при comparison."""
tests/test_comparison.py:240:            "intent": "comparison",
tests/test_comparison.py:242:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:245:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:256:        assert plan.intent == "comparison"
tests/test_comparison.py:269:    def test_master_comparison_two_queries(self, registry):
tests/test_comparison.py:271:            "intent": "comparison",
tests/test_comparison.py:273:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:276:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:287:        assert plan.intent == "comparison"
tests/test_comparison.py:292:    def test_master_comparison_labels_preserved(self, registry):
tests/test_comparison.py:294:            "intent": "comparison",
tests/test_comparison.py:296:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:299:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:318:    """render_comparison: grouped bar chart с mock-данными, без исключений."""
tests/test_comparison.py:321:    def test_render_comparison_returns_png_bytes(self):
tests/test_comparison.py:325:        png = render_comparison(
tests/test_comparison.py:337:    def test_render_comparison_with_empty_b_no_exception(self):
tests/test_comparison.py:342:        png = render_comparison(
tests/test_comparison.py:353:    def test_render_comparison_with_both_empty_no_exception(self):
tests/test_comparison.py:355:        png = render_comparison(
tests/test_comparison.py:366:    def test_render_comparison_multiple_rows(self):
tests/test_comparison.py:377:        png = render_comparison(
tests/test_comparison.py:388:    def test_render_comparison_masters_no_exception(self):
tests/test_comparison.py:393:        png = render_comparison(
tests/test_comparison.py:430:    def test_format_comparison_marks_incomplete_period_a(self):
tests/test_comparison.py:434:            aggregate_id="revenue_total",
tests/test_comparison.py:440:            aggregate_id="revenue_total",
tests/test_comparison.py:445:        comparison = ComparisonResult(
tests/test_comparison.py:451:        text = analyst.format_comparison(comparison, incomplete_period_a=True)
tests/test_comparison.py:454:    def test_format_comparison_no_incomplete_marker_when_full(self):
tests/test_comparison.py:458:            aggregate_id="revenue_total",
tests/test_comparison.py:464:            aggregate_id="revenue_total",
tests/test_comparison.py:469:        comparison = ComparisonResult(
tests/test_comparison.py:475:        text = analyst.format_comparison(comparison)
tests/test_comparison.py:478:    def test_format_comparison_includes_delta(self):
tests/test_comparison.py:482:            aggregate_id="revenue_total",
tests/test_comparison.py:488:            aggregate_id="revenue_total",
tests/test_comparison.py:493:        comparison = ComparisonResult(
tests/test_comparison.py:499:        text = analyst.format_comparison(comparison)
tests/test_comparison.py:503:    def test_format_comparison_negative_delta(self):
tests/test_comparison.py:507:            aggregate_id="revenue_total",
tests/test_comparison.py:513:            aggregate_id="revenue_total",
tests/test_comparison.py:518:        comparison = ComparisonResult(
tests/test_comparison.py:524:        text = analyst.format_comparison(comparison)
tests/test_comparison.py:530:    def test_format_comparison_empty_data(self):
tests/test_comparison.py:533:        result_a = AggregateResult(aggregate_id="revenue_total", rows=[], row_count=0)
tests/test_comparison.py:534:        result_b = AggregateResult(aggregate_id="revenue_total", rows=[], row_count=0)
tests/test_comparison.py:535:        comparison = ComparisonResult(
tests/test_comparison.py:541:        text = analyst.format_comparison(comparison)
src/swarm_powerbi_bot/orchestrator.py:11:    MultiPlan,
src/swarm_powerbi_bot/orchestrator.py:16:from .services.chart_renderer import render_chart, render_comparison
src/swarm_powerbi_bot/orchestrator.py:47:        # T026: Пробуем LLM-планирование с каталогом агрегатов (MultiPlan)
src/swarm_powerbi_bot/orchestrator.py:48:        multi_plan: MultiPlan | None = None
src/swarm_powerbi_bot/orchestrator.py:80:        # T031: Если есть MultiPlan и aggregate_registry — выполняем все запросы через SQLAgent.run_multi()
src/swarm_powerbi_bot/orchestrator.py:81:        # Пропускаем run_multi() для keyword-fallback планов: их aggregate_id — topic-идентификаторы,
src/swarm_powerbi_bot/orchestrator.py:82:        # не валидные catalog aggregate_ids, и они провалят registry.validate().
src/swarm_powerbi_bot/orchestrator.py:113:            diagnostics["multi_plan_aggregate"] = first_query.aggregate_id
src/swarm_powerbi_bot/orchestrator.py:155:            and multi_plan.intent == "comparison"
src/swarm_powerbi_bot/orchestrator.py:162:                        render_comparison,
src/swarm_powerbi_bot/orchestrator.py:166:                        ok_results[0].label or ok_results[0].aggregate_id,
src/swarm_powerbi_bot/orchestrator.py:167:                        ok_results[1].label or ok_results[1].aggregate_id,
src/swarm_powerbi_bot/orchestrator.py:173:                        diagnostics["chart_type"] = "matplotlib_comparison"
tests/test_planner_v2.py:4:- Mock LLM returns valid JSON → parses into MultiPlan correctly
tests/test_planner_v2.py:6:- aggregate_id not in catalog whitelist → falls back to TopicRegistry
tests/test_planner_v2.py:17:from swarm_powerbi_bot.models import MultiPlan, UserQuestion
tests/test_planner_v2.py:98:# ── T022-1: Valid JSON → MultiPlan ───────────────────────────────────────────
tests/test_planner_v2.py:100:class TestValidJsonToMultiPlan:
tests/test_planner_v2.py:101:    """Mock LLM returns valid JSON → parses into MultiPlan correctly."""
tests/test_planner_v2.py:107:                {"aggregate_id": "revenue_total", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15", "group_by": "total"}, "label": "Выручка за период"}
tests/test_planner_v2.py:117:        assert isinstance(plan, MultiPlan)
tests/test_planner_v2.py:120:        assert plan.queries[0].aggregate_id == "revenue_total"
tests/test_planner_v2.py:126:            "queries": [{"aggregate_id": "revenue_total", "params": {}, "label": "Revenue"}],
tests/test_planner_v2.py:139:            "queries": [{"aggregate_id": "outflow_clients", "params": {}, "label": "Outflow"}],
tests/test_planner_v2.py:152:            "queries": [{"aggregate_id": "outflow_clients", "params": {}, "label": "Отток"}],
tests/test_planner_v2.py:165:            "queries": [{"aggregate_id": "revenue_total", "params": {}, "label": "X"}],
tests/test_planner_v2.py:186:        assert isinstance(plan, MultiPlan)
tests/test_planner_v2.py:194:        assert isinstance(plan, MultiPlan)
tests/test_planner_v2.py:202:        assert isinstance(plan, MultiPlan)
tests/test_planner_v2.py:210:        assert isinstance(plan, MultiPlan)
tests/test_planner_v2.py:217:        assert isinstance(plan, MultiPlan)
tests/test_planner_v2.py:220:# ── T022-3: aggregate_id not in whitelist → TopicRegistry fallback ────────────
tests/test_planner_v2.py:223:    """Если LLM вернул aggregate_id не из каталога → fallback на TopicRegistry."""
tests/test_planner_v2.py:225:    def test_unknown_aggregate_id_triggers_fallback(self, registry):
tests/test_planner_v2.py:228:            "queries": [{"aggregate_id": "not_in_catalog", "params": {}, "label": "X"}],
tests/test_planner_v2.py:238:    def test_any_invalid_aggregate_id_triggers_fallback(self, registry):
tests/test_planner_v2.py:239:        """Если ЛЮБОЙ aggregate_id неверный — весь план → fallback."""
tests/test_planner_v2.py:241:            "intent": "comparison",
tests/test_planner_v2.py:243:                {"aggregate_id": "revenue_total", "params": {}, "label": "OK"},
tests/test_planner_v2.py:244:                {"aggregate_id": "sql_injection_here", "params": {}, "label": "Bad"}
tests/test_planner_v2.py:270:            "intent": "comparison",
tests/test_planner_v2.py:272:                {"aggregate_id": "revenue_total", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15"}, "label": "Выручка"},
tests/test_planner_v2.py:273:                {"aggregate_id": "outflow_clients", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15"}, "label": "Отток"}
tests/test_planner_v2.py:282:        assert isinstance(plan, MultiPlan)
tests/test_planner_v2.py:283:        assert plan.intent == "comparison"
tests/test_planner_v2.py:285:        ids = {aq.aggregate_id for aq in plan.queries}
tests/test_planner_v2.py:293:                {"aggregate_id": "revenue_total", "params": {}, "label": "Выручка"},
tests/test_planner_v2.py:294:                {"aggregate_id": "outflow_clients", "params": {}, "label": "Отток"},
tests/test_planner_v2.py:295:                {"aggregate_id": "communications_all", "params": {}, "label": "Коммуникации"}
tests/test_planner_v2.py:308:# ── Issue #2: Follow-up comparison intent ────────────────────────────────────
tests/test_planner_v2.py:311:    """Fix #2: follow-up «сравни по месяцам» должен возвращать comparison."""
tests/test_planner_v2.py:313:    def test_followup_comparison_llm(self, registry):
tests/test_planner_v2.py:314:        """LLM получает last_topic и возвращает comparison plan."""
tests/test_planner_v2.py:315:        comparison_json = """{
tests/test_planner_v2.py:316:            "intent": "comparison",
tests/test_planner_v2.py:318:                {"aggregate_id": "clients_outflow", "params": {"date_from": "2026-03-01", "date_to": "2026-03-31", "group_by": "status"}, "label": "Март"},
tests/test_planner_v2.py:319:                {"aggregate_id": "clients_outflow", "params": {"date_from": "2026-02-01", "date_to": "2026-02-28", "group_by": "status"}, "label": "Февраль"}
tests/test_planner_v2.py:324:        planner = _make_planner(comparison_json, registry)
tests/test_planner_v2.py:328:            last_topic="clients_outflow",
tests/test_planner_v2.py:333:        assert plan.intent == "comparison"
tests/test_planner_v2.py:335:        assert all(aq.aggregate_id == "clients_outflow" for aq in plan.queries)

exec
/bin/zsh -lc "sed -n '200,420p' src/swarm_powerbi_bot/services/sql_client.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "sed -n '1,220p' tests/test_context_switching.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
                rows = []
                for row in cursor.fetchall():
                    rows.append(dict(zip(columns, row)))
                return rows
            finally:
                conn.close()

        return await asyncio.to_thread(_sync)

    async def execute_aggregate(
        self,
        aggregate_id: str,
        params: dict[str, Any],
        registry: "AggregateRegistry",  # type: ignore[name-defined]
    ) -> AggregateResult:
        """T027: Выполняет агрегатный запрос по aggregate_id из каталога.

        1. Валидирует через registry.validate() — возвращает AggregateResult(status=error) если невалиден.
        2. Маппит aggregate_id на процедуру через каталог.
        3. Выполняет SQL и возвращает AggregateResult(status=ok|error|timeout).
        """
        # Валидация
        ok, msg = registry.validate(aggregate_id, params)
        if not ok:
            logger.warning(
                "execute_aggregate: validation failed for %r: %s", aggregate_id, msg
            )
            return AggregateResult(
                aggregate_id=aggregate_id,
                label=params.get("label", ""),
                status="error",
                error=f"validation failed: {msg}",
            )

        agg_entry = registry.get_aggregate(aggregate_id)
        if not agg_entry:
            return AggregateResult(
                aggregate_id=aggregate_id,
                status="error",
                error=f"aggregate_id not found in catalog: {aggregate_id!r}",
            )

        procedure = agg_entry.get("procedure", "")
        if not procedure:
            return AggregateResult(
                aggregate_id=aggregate_id,
                status="error",
                error=f"no procedure mapped for aggregate_id: {aggregate_id!r}",
            )

        start_ms = int(time.monotonic() * 1000)

        try:
            rows, _topic, _p = await asyncio.to_thread(
                self._execute_aggregate_sync, aggregate_id, procedure, params
            )
        except asyncio.TimeoutError:
            duration_ms = int(time.monotonic() * 1000) - start_ms
            return AggregateResult(
                aggregate_id=aggregate_id,
                status="timeout",
                error="SQL query timed out",
                duration_ms=duration_ms,
            )
        except Exception as exc:
            duration_ms = int(time.monotonic() * 1000) - start_ms
            logger.error("execute_aggregate error for %r: %s", aggregate_id, exc)
            return AggregateResult(
                aggregate_id=aggregate_id,
                status="error",
                error=str(exc),
                duration_ms=duration_ms,
            )

        duration_ms = int(time.monotonic() * 1000) - start_ms
        return AggregateResult(
            aggregate_id=aggregate_id,
            label=params.get("label", aggregate_id),
            rows=rows,
            row_count=len(rows),
            duration_ms=duration_ms,
            status="ok",
        )

    def _execute_aggregate_sync(
        self,
        aggregate_id: str,
        procedure: str,
        params: dict[str, Any],
        max_rows: int = 20,
    ) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
        """Синхронное выполнение агрегатного запроса."""
        # Защита от SQL injection: только alphanumeric + underscore + точка
        bare = procedure.replace("dbo.", "", 1) if procedure.startswith("dbo.") else procedure
        if not re.fullmatch(r"[a-zA-Z0-9_.]+", bare):
            logger.error("Invalid procedure name rejected: %r", procedure)
            return [], aggregate_id, {}
        if not procedure.startswith("dbo."):
            procedure = f"dbo.{procedure}"

        d_from_raw = params.get("date_from")
        d_to_raw = params.get("date_to")
        try:
            d_from = date.fromisoformat(d_from_raw) if d_from_raw else date.today() - timedelta(days=30)
        except (ValueError, TypeError):
            logger.warning("Invalid date_from %r for %s, using default", d_from_raw, aggregate_id)
            d_from = date.today() - timedelta(days=30)
        try:
            d_to = date.fromisoformat(d_to_raw) if d_to_raw else date.today()
        except (ValueError, TypeError):
            logger.warning("Invalid date_to %r for %s, using default", d_to_raw, aggregate_id)
            d_to = date.today()

        conn_str = self.settings.sql_connection_string()
        if not conn_str or pyodbc is None:
            logger.warning(
                "_execute_aggregate_sync: no connection string or pyodbc unavailable for %s",
                aggregate_id,
            )
            return [], aggregate_id, {"DateFrom": d_from, "DateTo": d_to}

        obj_id = params.get("object_id")
        if obj_id is None and self.settings.default_object_id:
            obj_id = self.settings.default_object_id

        group_by = params.get("group_by", "")
        if obj_id is None and group_by != "salon":
            logger.warning(
                "execute_aggregate: no ObjectId for %s — returning empty", aggregate_id
            )
            return [], aggregate_id, {"DateFrom": d_from, "DateTo": d_to}

        # Каталог использует "top", LLM может передать "top_n" — принимаем оба
        top_n = params.get("top", params.get("top_n", max_rows))

        sql_parts = [f"EXEC {procedure} @DateFrom=?, @DateTo=?"]
        sql_args: list[Any] = [d_from, d_to]

        if obj_id is not None:
            sql_parts.append("@ObjectId=?")
            sql_args.append(obj_id)

        master_id = params.get("master_id")
        if master_id is not None:
            sql_parts.append("@MasterId=?")
            sql_args.append(master_id)

        if group_by:
            sql_parts.append("@GroupBy=?")
            sql_args.append(group_by)

        filter_val = params.get("filter", "")
        if filter_val:
            sql_parts.append("@Filter=?")
            sql_args.append(filter_val)

        reason = params.get("reason", "")
        if reason:
            sql_parts.append("@Reason=?")
            sql_args.append(reason)

        sql_parts.append("@Top=?")
        sql_args.append(top_n)

        sql = ", ".join(sql_parts) + ";"
        logger.debug("execute_aggregate SQL: %s | args: %s", sql, sql_args)

        rows: list[dict[str, Any]] = []
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cur = conn.cursor()
            cur.execute(sql, sql_args)
            cols = [desc[0] for desc in (cur.description or [])]
            for idx, row in enumerate(cur.fetchall()):
                if idx >= max_rows:
                    break
                item = {}
                for cidx, col in enumerate(cols):
                    val = row[cidx]
                    item[col] = val.isoformat() if hasattr(val, "isoformat") else val
                rows.append(item)

        return rows, aggregate_id, {"DateFrom": d_from, "DateTo": d_to}

    async def fetch_rows_with_params(
        self,
        qp: QueryParams,
        *,
        max_rows: int = 20,
    ) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
        """Выполняет запрос с LLM-определёнными параметрами."""
        return await asyncio.to_thread(
            self._fetch_with_query_params,
            qp,
            max_rows,
        )

    def _fetch_with_query_params(
        self,
        qp: QueryParams,
        max_rows: int,
    ) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
        """Вызывает процедуру с параметрами из QueryParams."""
        procedure = qp.procedure or "spKDO_Aggregate"
        # Защита от SQL injection: только alphanumeric + underscore + точка
        if not re.fullmatch(r"[a-zA-Z0-9_.]+", procedure):
            logger.error("Invalid procedure name rejected: %r", procedure)
            return [], "", {}
        # Добавляем dbo. если не указано
        if not procedure.startswith("dbo."):
            procedure = f"dbo.{procedure}"
        topic_id = procedure.replace("dbo.spKDO_", "").lower()

        # Парсим даты (LLM может вернуть невалидную строку)
        try:
            d_from = date.fromisoformat(qp.date_from) if qp.date_from else date.today() - timedelta(days=30)
        except (ValueError, TypeError):
            logger.warning("Invalid date_from %r, using default", qp.date_from)
            d_from = date.today() - timedelta(days=30)
        try:
            d_to = date.fromisoformat(qp.date_to) if qp.date_to else date.today()
        except (ValueError, TypeError):

 succeeded in 0ms:
"""Тесты переключения и сохранения контекста разговора.

Проверяет что бот:
- Сохраняет тему после вопроса
- Использует last_topic для follow-up вопросов
- Переключает тему при явном указании
- Не путает модификаторы (сравни, по неделям) с темой
"""
from swarm_powerbi_bot.services.topic_registry import detect_topic


# ── Follow-up: тема сохраняется ──────────────────────────────

class TestContextRetention:
    """Если новый вопрос — модификатор (сравни, подробнее),
    тема должна остаться от предыдущего вопроса."""

    def test_comparison_keeps_outflow(self):
        topic = detect_topic("сравни месяц к месяцу", last_topic="outflow")
        assert topic == "outflow"

    def test_weekly_keeps_outflow(self):
        topic = detect_topic("покажи по неделям", last_topic="outflow")
        assert topic == "outflow"

    def test_details_keeps_masters(self):
        topic = detect_topic("подробнее", last_topic="masters")
        assert topic == "masters"

    def test_monthly_keeps_services(self):
        topic = detect_topic("по месяцам за квартал", last_topic="services")
        assert topic == "services"

    def test_dynamics_keeps_leaving(self):
        topic = detect_topic("покажи динамику", last_topic="leaving")
        assert topic == "leaving"

    def test_breakdown_keeps_quality(self):
        """'разбивка по категориям' — нет явной темы, follow-up."""
        topic = detect_topic("разбивка по категориям", last_topic="quality")
        assert topic == "quality"


# ── Явное переключение темы ──────────────────────────────────

class TestContextSwitch:
    """При явных ключевых словах другой темы — переключаемся."""

    def test_switch_from_outflow_to_masters(self):
        topic = detect_topic("покажи мастеров за неделю", last_topic="outflow")
        assert topic == "masters"

    def test_switch_from_outflow_to_services(self):
        topic = detect_topic("какая выручка за месяц?", last_topic="outflow")
        assert topic == "services"

    def test_switch_from_masters_to_outflow(self):
        topic = detect_topic("покажи отток", last_topic="masters")
        assert topic == "outflow"

    def test_switch_from_statistics_to_quality(self):
        topic = detect_topic("контроль качества за неделю", last_topic="statistics")
        assert topic == "quality"

    def test_switch_from_outflow_to_noshow(self):
        topic = detect_topic("кто не дошёл?", last_topic="outflow")
        assert topic == "noshow"


# ── Без контекста — fallback ─────────────────────────────────

class TestNoContext:
    """Без last_topic модификаторы идут в trend, остальное в statistics."""

    def test_comparison_without_context_goes_trend(self):
        topic = detect_topic("сравни по неделям")
        assert topic == "trend"

    def test_gibberish_returns_unknown(self):
        # score=0, нет контекста — возвращаем sentinel "unknown" вместо дефолта
        topic = detect_topic("привет как дела")
        assert topic == "unknown"

    def test_clear_topic_without_context(self):
        topic = detect_topic("отток за месяц")
        assert topic == "outflow"


# ── Пограничные случаи ──────────────────────────────────────

class TestEdgeCases:
    """Вопросы с неочевидным поведением."""

    def test_empty_question_with_context(self):
        topic = detect_topic("", last_topic="outflow")
        assert topic == "outflow"

    def test_period_only_keeps_context(self):
        """'за последнюю неделю' без темы — follow-up."""
        topic = detect_topic("за последнюю неделю", last_topic="outflow")
        assert topic == "outflow"

    def test_invalid_last_topic_ignored(self):
        # invalid last_topic не попадает в _TOPICS_BY_ID, поэтому контекст не используется.
        # score=0 → возвращаем "unknown"
        topic = detect_topic("привет", last_topic="nonexistent_topic")
        assert topic == "unknown"

    def test_trend_with_explicit_revenue_switches(self):
        """'тренд выручки' — явно про тренд, не follow-up."""
        topic = detect_topic("тренд выручки", last_topic="outflow")
        # "выручк" matches services, "тренд" matches trend
        assert topic in ("trend", "services")

exec
/bin/zsh -lc "sed -n '1,260p' tests/test_llm_planner.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
"""Тесты LLM-планировщика запросов (v2 — универсальные процедуры).

Проверяет:
- Парсинг JSON из ответа LLM
- plan_query() с мок-LLM
- PlannerAgent с LLM vs fallback
- Маппинг (procedure, group_by/filter) → topic
- Передачу QueryParams в SQLAgent
"""
import asyncio
from unittest.mock import AsyncMock


from swarm_powerbi_bot.agents.planner import PlannerAgent
from swarm_powerbi_bot.models import QueryParams, UserQuestion
from swarm_powerbi_bot.services.llm_client import LLMClient, _PLANNER_SYSTEM_PROMPT


# ── Парсинг JSON из LLM-ответа ─────────────────────────────────

class TestPlanJsonParsing:
    """LLM может вернуть JSON в разных обёртках."""

    def setup_method(self):
        from swarm_powerbi_bot.config import Settings
        self.client = LLMClient(Settings())

    def test_clean_json(self):
        raw = '{"procedure": "spKDO_Aggregate", "group_by": "total", "filter": "", "reason": "", "date_from": "2026-03-15", "date_to": "2026-04-14", "top": 20, "master_name": ""}'
        result = self.client._parse_plan_json(raw)
        assert result is not None
        assert result["procedure"] == "spKDO_Aggregate"
        assert result["group_by"] == "total"

    def test_json_in_markdown(self):
        raw = '```json\n{"procedure": "spKDO_Aggregate", "group_by": "week", "filter": "", "reason": "", "date_from": "2026-01-01", "date_to": "2026-04-14", "top": 20, "master_name": ""}\n```'
        result = self.client._parse_plan_json(raw)
        assert result is not None
        assert result["procedure"] == "spKDO_Aggregate"
        assert result["group_by"] == "week"

    def test_json_with_prefix_text(self):
        raw = 'Вот параметры: {"procedure": "spKDO_Aggregate", "group_by": "master", "filter": "", "reason": "", "date_from": "2026-03-15", "date_to": "2026-04-14", "top": 10, "master_name": "Анна"}'
        result = self.client._parse_plan_json(raw)
        assert result is not None
        assert result["master_name"] == "Анна"

    def test_no_json(self):
        result = self.client._parse_plan_json("Я не понимаю вопрос")
        assert result is None

    def test_invalid_json(self):
        result = self.client._parse_plan_json("{broken json here}")
        assert result is None

    def test_json_without_procedure(self):
        result = self.client._parse_plan_json('{"group_by": "week", "date_from": "2026-01-01"}')
        assert result is None


# ── PlannerAgent с LLM (v2 — универсальные процедуры) ──────────

class TestPlannerWithLLM:
    """PlannerAgent использует LLM для сборки запроса из компонентов."""

    def _make_planner(self, llm_response: dict | None):
        from swarm_powerbi_bot.config import Settings
        llm = LLMClient(Settings())
        llm.plan_query = AsyncMock(return_value=llm_response)
        return PlannerAgent(llm_client=llm)

    def test_llm_outflow_topic(self):
        """LLM определяет тему outflow, процедура зависит от USE_V2."""
        planner = self._make_planner({
            "procedure": "spKDO_ClientList",
            "group_by": "list",
            "filter": "outflow",
            "reason": "",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="покажи отток за месяц"),
        ))
        assert plan.topic == "outflow"
        assert plan.query_params is not None
        assert "planner:llm" in plan.notes
        # Процедура: v2=ClientList, v1=Outflow — главное topic верный
        assert "Outflow" in plan.query_params.procedure or "ClientList" in plan.query_params.procedure

    def test_llm_trend_topic(self):
        """LLM определяет тренд по неделям."""
        planner = self._make_planner({
            "procedure": "spKDO_Aggregate",
            "group_by": "week",
            "filter": "",
            "reason": "",
            "date_from": "2026-01-14",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="сравни по неделям", last_topic="outflow"),
        ))
        assert plan.topic == "trend"
        assert "Trend" in plan.query_params.procedure or "Aggregate" in plan.query_params.procedure

    def test_llm_masters_with_name(self):
        planner = self._make_planner({
            "procedure": "spKDO_Aggregate",
            "group_by": "master",
            "filter": "",
            "reason": "",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
            "top": 10,
            "master_name": "Анна",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="покажи загрузку мастера Анна"),
        ))
        assert plan.topic == "masters"
        assert plan.query_params.master_name == "Анна"

    def test_llm_communications_topic(self):
        planner = self._make_planner({
            "procedure": "spKDO_CommAgg",
            "group_by": "reason",
            "filter": "",
            "reason": "all",
            "date_from": "2026-04-07",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="коммуникации за неделю"),
        ))
        assert plan.topic == "communications"

    def test_llm_outflow_by_master_topic(self):
        """LLM: отток по мастерам → topic=outflow."""
        planner = self._make_planner({
            "procedure": "spKDO_ClientList",
            "group_by": "master",
            "filter": "outflow",
            "reason": "",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="отток по мастерам"),
        ))
        assert plan.topic == "outflow"

    def test_llm_fallback_on_none(self):
        """Если LLM недоступен — fallback на keyword-matching."""
        planner = self._make_planner(None)
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert plan.topic == "outflow"
        assert plan.query_params is not None
        assert "planner:keyword" in plan.notes

    def test_llm_preserves_object_id(self):
        planner = self._make_planner({
            "procedure": "spKDO_Aggregate",
            "group_by": "total",
            "filter": "",
            "reason": "",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="статистика", object_id=12345),
        ))
        assert plan.query_params.object_id == 12345

    def test_llm_invalid_procedure_fallback(self):
        """Если LLM вернул невалидную процедуру — fallback."""
        planner = self._make_planner({
            "procedure": "spKDO_Hacked; DROP TABLE",
            "group_by": "total",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="статистика за неделю"),
        ))
        assert "planner:keyword" in plan.notes  # fallback


# ── PlannerAgent без LLM (fallback) ────────────────────────────

class TestPlannerFallback:
    def test_no_llm_outflow(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert plan.topic == "outflow"
        assert "planner:keyword" in plan.notes

    def test_no_llm_statistics(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="покажи статистику за неделю"),
        ))
        assert plan.topic == "statistics"

    def test_no_llm_with_context_retention(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="подробнее", last_topic="outflow"),
        ))
        assert plan.topic == "outflow"

    def test_no_llm_comparison_switches_to_trend(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="сравни отток по неделям"),
        ))
        assert plan.topic == "trend"
        assert "comparison_requested" in plan.notes


# ── Маппинг topic ───────────────────────────────────────────────

class TestTopicMapping:
    """_derive_topic корректно маппит (procedure, params) → topic."""

    def setup_method(self):
        self.planner = PlannerAgent()
        self.q = UserQuestion(user_id="1", text="test")

    def test_aggregate_mappings(self):
        cases = {
            "total": "statistics",
            "week": "trend",
            "month": "trend",
            "master": "masters",
            "service": "services",
            "channel": "referrals",
        }
        for group_by, expected_topic in cases.items():
            qp = QueryParams(procedure="spKDO_Aggregate", group_by=group_by)
            topic = self.planner._derive_topic(qp, self.q)
            assert topic == expected_topic, f"group_by={group_by}"

    def test_clientlist_mappings(self):
        cases = {
            "outflow": "outflow",

codex
I’ve got enough code context to start falsifying the new behavior with tests and contract checks. The main suspicion is that the fallback comparison path ignores the actual question semantics and may generate invalid aggregate ids for the executor.
exec
/bin/zsh -lc "nl -ba src/swarm_powerbi_bot/agents/planner.py | sed -n '330,420p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "nl -ba src/swarm_powerbi_bot/services/llm_client.py | sed -n '145,235p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
   145	            logger.warning("plan_query: LLM returned empty response")
   146	            return None
   147	
   148	        return self._parse_plan_json(raw)
   149	
   150	    async def plan_aggregates(
   151	        self,
   152	        question: str,
   153	        catalog_prompt: str,
   154	        semantic_prompt: str,
   155	        last_topic: str = "",
   156	    ) -> dict | None:
   157	        """T025: Одношаговое LLM-планирование с каталогом агрегатов.
   158	
   159	        Возвращает распарсенный JSON-dict или None при ошибке/circuit breaker.
   160	        Timeout: settings.llm_plan_timeout (5s).
   161	        Circuit breaker: после threshold подряд неудач → None на cooldown секунд.
   162	        """
   163	        if not self.settings.ollama_api_key:
   164	            return None
   165	
   166	        # Проверяем circuit breaker (под локом — потокобезопасно)
   167	        async with self._cb_lock:
   168	            now = time.monotonic()
   169	            if self._cb_open_until > now:
   170	                logger.warning(
   171	                    "LLM circuit breaker open: %.0fs remaining",
   172	                    self._cb_open_until - now,
   173	                )
   174	                return None
   175	
   176	        system_prompt = (
   177	            "Ты — планировщик аналитических запросов. "
   178	            "Ниже — каталог доступных агрегатов и семантический каталог.\n\n"
   179	            f"КАТАЛОГ АГРЕГАТОВ:\n{catalog_prompt}\n\n"
   180	            f"СЕМАНТИЧЕСКИЙ КАТАЛОГ:\n{semantic_prompt}\n\n"
   181	            "Пользователь задаёт вопрос на русском. "
   182	            "Выбери подходящие агрегаты из каталога и верни JSON:\n"
   183	            '{"intent": "single|comparison|decomposition|trend|ranking", '
   184	            '"queries": [{"aggregate_id": "...", "params": {...}, "label": "..."}], '
   185	            '"topic": "statistics", "render_needed": true}\n\n'
   186	            "ПРАВИЛА DECOMPOSITION:\n"
   187	            "Если вопрос содержит «почему», «из-за чего», «что повлияло», «причина» "
   188	            "или аналогичные запросы на факторный анализ — используй intent=decomposition.\n"
   189	            "При decomposition запроси ВСЕ связанные метрики за ДВА периода:\n"
   190	            "Пример: «почему упала выручка?» → 5 запросов:\n"
   191	            "  1. revenue_summary за текущий период\n"
   192	            "  2. revenue_summary за предыдущий период\n"
   193	            "  3. client_count за текущий период\n"
   194	            "  4. client_count за предыдущий период\n"
   195	            "  5. avg_check (один период достаточно)\n"
   196	            "Максимум 5 запросов при decomposition. "
   197	            "Ставь понятный label: «Выручка (апрель)», «Клиенты (март)» и т.д.\n\n"
   198	            "ПРАВИЛА FOLLOW-UP:\n"
   199	            "Если указан last_topic — пользователь продолжает предыдущий разговор. "
   200	            "Используй last_topic как основу для выбора агрегата.\n"
   201	            "Пример: last_topic=clients_outflow, вопрос=«сравни по месяцам» "
   202	            "→ intent=comparison, aggregate_id=clients_outflow для обоих периодов.\n"
   203	            "Для comparison клиентских агрегатов (clients_*) используй group_by=status "
   204	            "(агрегированные цифры), НЕ group_by=list (сырой список).\n\n"
   205	            "ВАЖНО: используй только aggregate_id из каталога выше. "
   206	            "Ответь ТОЛЬКО JSON, без пояснений."
   207	        )
   208	
   209	        base = self.settings.ollama_base_url.rstrip("/")
   210	        url = f"{base}/chat"
   211	        headers = {
   212	            "Authorization": f"Bearer {self.settings.ollama_api_key}",
   213	            "Content-Type": "application/json",
   214	        }
   215	        payload: dict[str, Any] = {
   216	            "model": self.settings.ollama_model,
   217	            "messages": [
   218	                {"role": "system", "content": system_prompt},
   219	                {"role": "user", "content": (
   220	                    f"{question}\nКонтекст: last_topic={_sanitize_topic(last_topic)}"
   221	                    if last_topic else question
   222	                )},
   223	            ],
   224	            "stream": False,
   225	            "options": {"temperature": 0.1},
   226	        }
   227	
   228	        try:
   229	            timeout = float(self.settings.llm_plan_timeout)
   230	            async with httpx.AsyncClient(timeout=timeout) as client:
   231	                resp = await client.post(url, headers=headers, json=payload)
   232	                resp.raise_for_status()
   233	                data = resp.json()
   234	        except Exception as exc:
   235	            logger.error("plan_aggregates request failed: %s", exc)

 succeeded in 0ms:
   330	        if intent == "comparison":
   331	            if len(queries) < 2:
   332	                logger.warning(
   333	                    "plan_aggregates: comparison intent but only %d queries — falling back",
   334	                    len(queries),
   335	                )
   336	                return None
   337	
   338	        return MultiPlan(
   339	            objective=question.text,
   340	            intent=intent,
   341	            queries=queries,
   342	            topic=topic,
   343	            render_needed=render_needed,
   344	            notes=["planner_v2:llm"],
   345	        )
   346	
   347	    _COMPARISON_KEYWORDS = {"сравни", "сравнен", "сравнить", "сравнение", "compare", "сопостав", "vs"}
   348	    _CLIENT_AGGREGATES = {
   349	        "clients_outflow", "clients_leaving", "clients_forecast",
   350	        "clients_noshow", "clients_quality", "clients_birthday", "clients_all",
   351	    }
   352	
   353	    def _fallback_multi_plan(
   354	        self, question: UserQuestion, render_needed: bool
   355	    ) -> MultiPlan:
   356	        """Fallback: keyword-based TopicRegistry → AggregateQuery(s).
   357	
   358	        Определяет intent=comparison по ключевым словам и генерирует
   359	        2 запроса с разными периодами при наличии контекста (last_topic).
   360	        """
   361	        topic = detect_topic(question.text, last_topic=question.last_topic)
   362	        text_lower = question.text.lower()
   363	
   364	        is_comparison = any(kw in text_lower for kw in self._COMPARISON_KEYWORDS)
   365	
   366	        if is_comparison and question.last_topic:
   367	            agg_id = question.last_topic
   368	            # Для клиентских агрегатов — group_by=status (агрегированные цифры)
   369	            group_by = "status" if agg_id in self._CLIENT_AGGREGATES else ""
   370	            today = date.today()
   371	            first_of_current = today.replace(day=1)
   372	            last_of_prev = first_of_current - timedelta(days=1)
   373	            first_of_prev = last_of_prev.replace(day=1)
   374	
   375	            params_prev: dict = {
   376	                "date_from": first_of_prev.isoformat(),
   377	                "date_to": last_of_prev.isoformat(),
   378	            }
   379	            params_curr: dict = {
   380	                "date_from": first_of_current.isoformat(),
   381	                "date_to": today.isoformat(),
   382	            }
   383	            if group_by:
   384	                params_prev["group_by"] = group_by
   385	                params_curr["group_by"] = group_by
   386	
   387	            _RU_MONTHS = [
   388	                "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
   389	                "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
   390	            ]
   391	            prev_label = f"{_RU_MONTHS[first_of_prev.month]} {first_of_prev.year}"
   392	            curr_label = f"{_RU_MONTHS[first_of_current.month]} {first_of_current.year}"
   393	
   394	            queries = [
   395	                AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_prev), label=prev_label),
   396	                AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_curr), label=curr_label),
   397	            ]
   398	            return MultiPlan(
   399	                objective=question.text,
   400	                intent="comparison",
   401	                queries=queries,
   402	                topic=agg_id,
   403	                render_needed=render_needed,
   404	                notes=["planner_v2:keyword", "comparison:fallback"],
   405	            )
   406	
   407	        agg_query = AggregateQuery(
   408	            aggregate_id=topic,
   409	            params={},
   410	            label=topic,
   411	        )
   412	
   413	        return MultiPlan(
   414	            objective=question.text,
   415	            intent="single",
   416	            queries=[agg_query],
   417	            topic=topic,
   418	            render_needed=render_needed,
   419	            notes=["planner_v2:keyword"],
   420	        )

exec
/bin/zsh -lc 'PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p no:cacheprovider tests/test_planner_v2.py tests/test_context_switching.py tests/test_comparison.py' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 exited 1 in 153ms:
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

exec
/bin/zsh -lc "find catalogs -maxdepth 2 -type f | sort | sed -n '1,120p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
catalogs/aggregate-catalog.yaml
catalogs/bootstrap/gaps.md
catalogs/bootstrap/pbix-to-sql-mapping.yaml
catalogs/bootstrap/semantic-model.yaml
catalogs/category-index.yaml
catalogs/semantic-catalog.yaml

exec
/bin/zsh -lc "sed -n '1,260p' src/swarm_powerbi_bot/telegram_bot.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import Settings
from .models import UserQuestion
from .orchestrator import SwarmOrchestrator
from .services.registration import get_user_object_id, is_subscribed, parse_start_arg, subscribe
# TODO: раскомментировать когда Ollama поддержит аудио-тракт
# from .services.stt_client import STTClient
from .services.sql_client import has_period_hint

# ── Inline-кнопки выбора периода ─────────────────────────────

PERIOD_BUTTONS = [
    [
        InlineKeyboardButton("Вчера", callback_data="period:вчера"),
        InlineKeyboardButton("Неделя", callback_data="period:за неделю"),
        InlineKeyboardButton("Месяц", callback_data="period:за месяц"),
    ],
    [
        InlineKeyboardButton("Квартал", callback_data="period:за квартал"),
        InlineKeyboardButton("Полгода", callback_data="period:за полгода"),
        InlineKeyboardButton("Год", callback_data="period:за год"),
    ],
]

PERIOD_KEYBOARD = InlineKeyboardMarkup(PERIOD_BUTTONS)


class TelegramSwarmBot:
    def __init__(self, token: str, orchestrator: SwarmOrchestrator, settings: Settings):
        self.token = token
        self.orchestrator = orchestrator
        self.settings = settings
        # TODO: раскомментировать когда Ollama поддержит аудио-тракт
        # self.stt = STTClient(settings)

    # ── /start [activation_link] ──────────────────────────────

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.effective_user:
            return

        account_id = str(update.effective_user.id)
        first_arg = context.args[0] if context.args else ""

        # Активация по ссылке: /start <customer_id>-<dataset_id>
        if first_arg and first_arg.strip():
            try:
                customer_id, dataset_id = parse_start_arg(first_arg)
                code, msg = await subscribe(customer_id, dataset_id, account_id, self.settings)
                await update.message.reply_text(msg)
            except ValueError as ve:
                await update.message.reply_text(f"⚠️ {ve}")
            except Exception:
                await update.message.reply_text("Техническая ошибка. Попробуйте позже.")
            return

        # Без аргумента — проверяем подписку и приветствуем
        try:
            already = await is_subscribed(account_id, self.settings)
        except Exception:
            already = False

        # TODO: раскомментировать когда Ollama поддержит аудио-тракт
        # voice_hint = ""
        # if self.stt.available:
        #     voice_hint = "\n\nМожно отправить голосовое сообщение — я пойму!"
        voice_hint = ""

        if already:
            await update.message.reply_text(
                "Вы подписаны! Просто напишите вопрос, например:\n"
                "• Покажи отток клиентов\n"
                "• Какая выручка за неделю?\n"
                "• Топ мастеров по загрузке"
                + voice_hint
            )
        else:
            await update.message.reply_text(
                "Привет! Я аналитический бот КДО.\n\n"
                "Просто напишите вопрос, например:\n"
                "• Покажи отток клиентов\n"
                "• Какая выручка за неделю?\n"
                "• Топ мастеров по загрузке\n\n"
                "Я определю тему и спрошу за какой период, "
                "если вы не указали его в вопросе."
                + voice_hint
            )

    # ── /ask <вопрос> ─────────────────────────────────────────

    async def ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return
        text = " ".join(context.args).strip()
        if not text:
            await update.message.reply_text("Пример: /ask Покажи тренд выручки за неделю")
            return
        await self._handle_user_text(update, context, text)

    # ── Обычное текстовое сообщение ───────────────────────────

    async def text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.message.text:
            return
        await self._handle_user_text(update, context, update.message.text.strip())

    # ── Голосовое сообщение (отключено — Ollama не поддерживает аудио-тракт) ──
    #
    # async def voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #     if not update.message or not update.message.voice:
    #         return
    #     if not self.stt.available:
    #         await update.message.reply_text(
    #             "Голосовые сообщения пока не поддерживаются — напишите текстом."
    #         )
    #         return
    #     await update.message.chat.send_action(action=ChatAction.TYPING)
    #     voice = update.message.voice
    #     file = await voice.get_file()
    #     audio_bytes = await file.download_as_bytearray()
    #     text = await self.stt.transcribe(bytes(audio_bytes), filename="voice.ogg")
    #     if not text:
    #         await update.message.reply_text(
    #             "Не удалось распознать. Попробуйте ещё раз или напишите текстом."
    #         )
    #         return
    #     await update.message.reply_text(f"🎤 _{text}_", parse_mode="Markdown")
    #     await self._handle_user_text(update, context, text)

    # ── Callback от inline-кнопки периода ─────────────────────

    async def period_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query or not query.data:
            return

        await query.answer()

        # Достаём сохранённый вопрос
        pending = (context.user_data or {}).get("pending_question", "")
        if not pending:
            await query.edit_message_text("Сессия истекла, задайте вопрос заново.")
            return

        # Извлекаем период из callback_data ("period:за неделю" → "за неделю")
        period_text = query.data.split(":", 1)[1]

        # Дополняем вопрос периодом
        full_question = f"{pending} {period_text}"

        # Убираем кнопки, показываем что выбрал пользователь
        await query.edit_message_text(f"📊 {pending} — *{period_text}*", parse_mode="Markdown")

        # Выполняем запрос — используем query.message для отправки ответа,
        # но user_id берём из callback_query.from_user (пользователь, не бот)
        if query.from_user:
            context.user_data["_callback_user_id"] = str(query.from_user.id)
        await self._process_question(query.message, full_question, context=context)

        # Очищаем pending
        context.user_data.pop("pending_question", None)

    # ── Внутренняя логика ─────────────────────────────────────

    async def _handle_user_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str,
    ) -> None:
        """Проверяет наличие периода. Если нет — показывает визард."""
        if not update.message:
            return

        if has_period_hint(text):
            # Период указан — выполняем сразу
            await self._process_question(update.message, text, context=context)
        else:
            # Период не указан — спрашиваем через кнопки
            context.user_data["pending_question"] = text
            await update.message.reply_text(
                f"📋 *{text}*\n\nЗа какой период?",
                reply_markup=PERIOD_KEYBOARD,
                parse_mode="Markdown",
            )

    async def _process_question(self, message, text: str, context: ContextTypes.DEFAULT_TYPE | None = None) -> None:
        await message.chat.send_action(action=ChatAction.TYPING)

        user_id = "unknown"
        # Для callback-запросов (period_callback) user_id сохранён из callback_query.from_user,
        # т.к. query.message.from_user — это бот, а не пользователь.
        user_data_raw = context.user_data if context else {}
        callback_uid = (user_data_raw or {}).pop("_callback_user_id", None)
        if callback_uid:
            user_id = callback_uid
        elif hasattr(message, "from_user") and message.from_user:
            user_id = str(message.from_user.id)
        elif hasattr(message, "chat") and message.chat:
            user_id = str(message.chat.id)

        # Получаем ObjectId (SalonId) из подписки — кэшируем в user_data
        object_id: int | None = None
        user_data = context.user_data if context else {}
        if user_data is not None:
            object_id = user_data.get("object_id")
            if object_id is None and user_id != "unknown":
                try:
                    object_id = await get_user_object_id(user_id, self.settings)
                    if object_id:
                        user_data["object_id"] = object_id
                except Exception:
                    pass
        # Fallback на default_object_id из конфига
        if object_id is None and self.settings.default_object_id:
            object_id = self.settings.default_object_id

        # last_topic для контекста разговора (follow-up вопросы)
        last_topic = ""
        if user_data is not None:
            last_topic = user_data.get("last_topic", "")

        response = await self.orchestrator.handle_question(
            UserQuestion(user_id=user_id, text=text, object_id=object_id,
                         last_topic=last_topic),
        )

        # Сохраняем тему для следующего вопроса
        if user_data is not None and response.topic:
            user_data["last_topic"] = response.topic

        if response.image:
            # Описание — caption к картинке (до 1024 символов)
            caption = self._fit_caption(response.answer)
            try:
                await message.reply_photo(
                    response.image, caption=caption, parse_mode="Markdown",
                )
            except Exception:
                # Markdown может сломаться — шлём без разметки
                await message.reply_photo(response.image, caption=caption)

            # Если ответ длиннее caption — шлём полный текст отдельно
            if len(response.answer) > 1024:
                try:
                    await message.reply_text(response.answer, parse_mode="Markdown")
                except Exception:
                    await message.reply_text(response.answer)
        else:
            try:
                await message.reply_text(response.answer, parse_mode="Markdown")

exec
/bin/zsh -lc "rg -n \"clients_outflow|outflow_clients|clients_all|revenue_total|aggregate-catalog|aggregates:\" catalogs src tests -g '"'!**/.venv/**'"'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
src/swarm_powerbi_bot/services/llm_client.py:201:            "Пример: last_topic=clients_outflow, вопрос=«сравни по месяцам» "
src/swarm_powerbi_bot/services/llm_client.py:202:            "→ intent=comparison, aggregate_id=clients_outflow для обоих периодов.\n"
src/swarm_powerbi_bot/services/llm_client.py:241:            logger.warning("plan_aggregates: LLM returned empty content")
tests/test_aggregate_registry.py:19:    aggregates:
catalogs/aggregate-catalog.yaml:9:aggregates:
catalogs/aggregate-catalog.yaml:15:  - id: revenue_total
catalogs/aggregate-catalog.yaml:220:  - id: clients_outflow
catalogs/aggregate-catalog.yaml:445:  - id: clients_all
tests/test_multi_query.py:20:    aggregates:
tests/test_planner_v2.py:25:    aggregates:
tests/test_planner_v2.py:26:      - id: revenue_total
tests/test_planner_v2.py:34:      - id: outflow_clients
tests/test_planner_v2.py:41:      - id: clients_outflow
tests/test_planner_v2.py:62:    p = tmp_path / "aggregate-catalog.yaml"
tests/test_planner_v2.py:107:                {"aggregate_id": "revenue_total", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15", "group_by": "total"}, "label": "Выручка за период"}
tests/test_planner_v2.py:120:        assert plan.queries[0].aggregate_id == "revenue_total"
tests/test_planner_v2.py:126:            "queries": [{"aggregate_id": "revenue_total", "params": {}, "label": "Revenue"}],
tests/test_planner_v2.py:139:            "queries": [{"aggregate_id": "outflow_clients", "params": {}, "label": "Outflow"}],
tests/test_planner_v2.py:152:            "queries": [{"aggregate_id": "outflow_clients", "params": {}, "label": "Отток"}],
tests/test_planner_v2.py:165:            "queries": [{"aggregate_id": "revenue_total", "params": {}, "label": "X"}],
tests/test_planner_v2.py:243:                {"aggregate_id": "revenue_total", "params": {}, "label": "OK"},
tests/test_planner_v2.py:272:                {"aggregate_id": "revenue_total", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15"}, "label": "Выручка"},
tests/test_planner_v2.py:273:                {"aggregate_id": "outflow_clients", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15"}, "label": "Отток"}
tests/test_planner_v2.py:286:        assert ids == {"revenue_total", "outflow_clients"}
tests/test_planner_v2.py:293:                {"aggregate_id": "revenue_total", "params": {}, "label": "Выручка"},
tests/test_planner_v2.py:294:                {"aggregate_id": "outflow_clients", "params": {}, "label": "Отток"},
tests/test_planner_v2.py:318:                {"aggregate_id": "clients_outflow", "params": {"date_from": "2026-03-01", "date_to": "2026-03-31", "group_by": "status"}, "label": "Март"},
tests/test_planner_v2.py:319:                {"aggregate_id": "clients_outflow", "params": {"date_from": "2026-02-01", "date_to": "2026-02-28", "group_by": "status"}, "label": "Февраль"}
tests/test_planner_v2.py:321:            "topic": "clients_outflow",
tests/test_planner_v2.py:328:            last_topic="clients_outflow",
tests/test_planner_v2.py:335:        assert all(aq.aggregate_id == "clients_outflow" for aq in plan.queries)
tests/test_planner_v2.py:339:        assert call_kwargs.kwargs.get("last_topic") == "clients_outflow"
tests/test_planner_v2.py:347:            last_topic="clients_outflow",
tests/test_planner_v2.py:354:        assert all(aq.aggregate_id == "clients_outflow" for aq in plan.queries)
tests/test_comparison.py:36:    aggregates:
tests/test_comparison.py:37:      - id: revenue_total
tests/test_comparison.py:46:      - id: outflow_clients
tests/test_comparison.py:58:    p = tmp_path / "aggregate-catalog.yaml"
tests/test_comparison.py:108:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:111:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:126:        assert plan.queries[0].aggregate_id == "revenue_total"
tests/test_comparison.py:127:        assert plan.queries[1].aggregate_id == "revenue_total"
tests/test_comparison.py:133:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:136:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:157:                {"aggregate_id": "revenue_total", "params": {}, "label": "Один"}
tests/test_comparison.py:242:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:245:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:273:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:276:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:296:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:299:                {"aggregate_id": "revenue_total",
tests/test_comparison.py:434:            aggregate_id="revenue_total",
tests/test_comparison.py:440:            aggregate_id="revenue_total",
tests/test_comparison.py:458:            aggregate_id="revenue_total",
tests/test_comparison.py:464:            aggregate_id="revenue_total",
tests/test_comparison.py:482:            aggregate_id="revenue_total",
tests/test_comparison.py:488:            aggregate_id="revenue_total",
tests/test_comparison.py:507:            aggregate_id="revenue_total",
tests/test_comparison.py:513:            aggregate_id="revenue_total",
tests/test_comparison.py:533:        result_a = AggregateResult(aggregate_id="revenue_total", rows=[], row_count=0)
tests/test_comparison.py:534:        result_b = AggregateResult(aggregate_id="revenue_total", rows=[], row_count=0)
src/swarm_powerbi_bot/agents/planner.py:261:            logger.warning("plan_aggregates: 'queries' is missing or empty")
src/swarm_powerbi_bot/agents/planner.py:269:                "plan_aggregates: unknown intent %r from LLM, falling back to 'single'",
src/swarm_powerbi_bot/agents/planner.py:289:                    "plan_aggregates: aggregate_id %r not in catalog — falling back",
src/swarm_powerbi_bot/agents/planner.py:333:                    "plan_aggregates: comparison intent but only %d queries — falling back",
src/swarm_powerbi_bot/agents/planner.py:349:        "clients_outflow", "clients_leaving", "clients_forecast",
src/swarm_powerbi_bot/agents/planner.py:350:        "clients_noshow", "clients_quality", "clients_birthday", "clients_all",
tests/test_security.py:21:    aggregates:
tests/test_security.py:22:      - id: revenue_total
tests/test_security.py:31:      - id: outflow_clients
tests/test_security.py:50:    p = tmp_path / "aggregate-catalog.yaml"
tests/test_security.py:85:        ok, msg = registry.validate("revenue_total", {"group_by": "'; DROP TABLE; --"})
tests/test_security.py:91:        ok, msg = registry.validate("revenue_total", {"date_from": "'; DROP TABLE--"})
tests/test_security.py:97:        ok, msg = registry.validate("outflow_clients", {"filter": "'; DROP TABLE--"})
tests/test_security.py:103:        ok, msg = registry.validate("revenue_total", {"date_from": "2026-04-01", "date_to": "2026-04-15"})
tests/test_security.py:114:        ok, _ = registry.validate("revenue_total", {})
tests/test_security.py:131:        ok, msg = registry.validate("revenue_total; DROP TABLE", {})
tests/test_security.py:165:            ok, msg = registry.validate("revenue_total", {"date_from": bad_date})
tests/test_security.py:171:            ok, msg = registry.validate("revenue_total", {"date_to": bad_date})
tests/test_security.py:176:        ok, msg = registry.validate("revenue_total", {
tests/test_security.py:184:        ok, msg = registry.validate("revenue_total", {"date_from": 20260101})
tests/test_security.py:194:        # revenue_total allows: total, week, month, master
tests/test_security.py:197:            ok, msg = registry.validate("revenue_total", {"group_by": val})
tests/test_security.py:198:            assert ok is False, f"Expected rejection for group_by={val!r} on revenue_total"
tests/test_security.py:203:            ok, msg = registry.validate("revenue_total", {"group_by": val})
tests/test_security.py:204:            assert ok is True, f"Expected OK for group_by={val!r} on revenue_total, got: {msg}"
tests/test_security.py:208:        # "salon" доступен для visits_by_salon, но не для outflow_clients
tests/test_security.py:210:        ok_outflow, msg = registry.validate("outflow_clients", {"group_by": "salon"})
tests/test_security.py:217:        ok, _ = registry.validate("revenue_total", {})
tests/test_security.py:221:        ok, msg = registry.validate("revenue_total", {"group_by": "total; DROP TABLE"})
tests/test_security.py:229:        ok, msg = registry.validate("revenue_total", {"top_n": 0})
tests/test_security.py:234:        ok, msg = registry.validate("revenue_total", {"top_n": 51})
tests/test_security.py:239:        ok, msg = registry.validate("revenue_total", {"top_n": "20"})
tests/test_security.py:244:            ok, _ = registry.validate("revenue_total", {"top_n": n})
tests/test_security.py:252:        ok, msg = registry.validate("revenue_total", {"object_id": "12345"})
tests/test_security.py:257:        ok, _ = registry.validate("revenue_total", {"object_id": 12345})
tests/test_security.py:261:        ok, msg = registry.validate("revenue_total", {"master_id": "42"})
tests/test_security.py:266:        ok, _ = registry.validate("revenue_total", {"master_id": None})
src/swarm_powerbi_bot/config.py:130:    aggregate_catalog_path: str = "catalogs/aggregate-catalog.yaml"
src/swarm_powerbi_bot/config.py:176:            aggregate_catalog_path=os.getenv("AGGREGATE_CATALOG_PATH", "catalogs/aggregate-catalog.yaml").strip(),
tests/integration/test_real_llm.py:152:            aggregate_id="revenue_total",
tests/integration/test_real_sql.py:49:# ── 3. revenue_total ─────────────────────────────────────────────────────────
tests/integration/test_real_sql.py:51:async def test_aggregate_revenue_total(
tests/integration/test_real_sql.py:57:        "revenue_total",
tests/integration/test_real_sql.py:66:# ── 4. clients_outflow ───────────────────────────────────────────────────────
tests/integration/test_real_sql.py:68:async def test_aggregate_clients_outflow(
tests/integration/test_real_sql.py:73:        "clients_outflow",
tests/integration/test_real_sql.py:110:    for entry in aggregates:
tests/integration/test_real_sql.py:141:        "revenue_total",
tests/integration/test_real_sql.py:185:    agg_ids = ["revenue_total", "revenue_by_week", "revenue_by_master",
tests/integration/test_real_sql.py:186:               "clients_outflow", "comm_all_by_reason"]
tests/test_composition.py:27:    aggregates:
tests/test_composition.py:51:      - id: outflow_clients
tests/test_composition.py:63:    p = tmp_path / "aggregate-catalog.yaml"

exec
/bin/zsh -lc "nl -ba catalogs/aggregate-catalog.yaml | sed -n '210,280p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "nl -ba src/swarm_powerbi_bot/orchestrator.py | sed -n '40,120p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
    40	        self.analyst_agent = analyst_agent
    41	        self.aggregate_registry = aggregate_registry
    42	        self.query_logger = query_logger
    43	
    44	    async def handle_question(self, question: UserQuestion) -> SwarmResponse:
    45	        diagnostics: dict[str, str] = {}
    46	
    47	        # T026: Пробуем LLM-планирование с каталогом агрегатов (MultiPlan)
    48	        multi_plan: MultiPlan | None = None
    49	        if getattr(self.planner, "aggregate_registry", None) is not None:
    50	            try:
    51	                multi_plan = await self.planner.run_multi(question)
    52	                planner_v2_mode = (
    53	                    "llm" if "planner_v2:llm" in multi_plan.notes else "keyword"
    54	                )
    55	                logger.info(
    56	                    "[PLAN_V2] %s | intent=%s | topic=%s | queries=%d",
    57	                    planner_v2_mode,
    58	                    multi_plan.intent,
    59	                    multi_plan.topic,
    60	                    len(multi_plan.queries),
    61	                )
    62	                diagnostics["planner_v2"] = planner_v2_mode
    63	            except Exception as exc:
    64	                logger.error("[PLAN_V2] ERROR: %s", exc)
    65	                diagnostics["planner_v2_error"] = str(exc)
    66	                multi_plan = None
    67	
    68	        # I1: Пропускаем legacy planner.run() если multi_plan с запросами уже получен —
    69	        # иначе два LLM-вызова на каждый вопрос (двойной cost/latency)
    70	        if multi_plan and multi_plan.queries:
    71	            plan = self.planner.multi_plan_to_plan(multi_plan, question)
    72	        else:
    73	            try:
    74	                plan = await self.planner.run(question)
    75	            except Exception as exc:
    76	                logger.error("[PLAN] ERROR: %s", exc)
    77	                diagnostics["plan_error"] = str(exc)
    78	                plan = self.planner.empty_plan(question.text)
    79	
    80	        # T031: Если есть MultiPlan и aggregate_registry — выполняем все запросы через SQLAgent.run_multi()
    81	        # Пропускаем run_multi() для keyword-fallback планов: их aggregate_id — topic-идентификаторы,
    82	        # не валидные catalog aggregate_ids, и они провалят registry.validate().
    83	        multi_results: list[AggregateResult] = []
    84	        if (
    85	            multi_plan
    86	            and multi_plan.queries
    87	            and self.aggregate_registry is not None
    88	            and "planner_v2:keyword" not in (multi_plan.notes or [])
    89	        ):
    90	            diagnostics["multi_plan_intent"] = multi_plan.intent
    91	            diagnostics["multi_plan_queries"] = str(len(multi_plan.queries))
    92	            try:
    93	                multi_results = await self.sql_agent.run_multi(
    94	                    multi_plan,
    95	                    self.aggregate_registry,
    96	                    logger_=self.query_logger,
    97	                )
    98	                ok_count = sum(1 for r in multi_results if r.status == "ok")
    99	                diagnostics["multi_plan_ok"] = str(ok_count)
   100	                logger.info(
   101	                    "[MULTI_SQL] queries=%d ok=%d",
   102	                    len(multi_results),
   103	                    ok_count,
   104	                )
   105	            except Exception as exc:
   106	                logger.error("[MULTI_SQL] ERROR: %s", exc)
   107	                diagnostics["multi_sql_error"] = str(exc)
   108	        elif multi_plan and multi_plan.queries:
   109	            # Degradation: LLM спланировал запросы, но registry не инициализирован
   110	            # (нет каталога агрегатов) — запросы не могут быть валидированы и выполнены.
   111	            # Логируем для диагностики, fallback на legacy plan.
   112	            first_query = multi_plan.queries[0]
   113	            diagnostics["multi_plan_aggregate"] = first_query.aggregate_id
   114	            diagnostics["multi_plan_intent"] = multi_plan.intent
   115	
   116	        # Диагностика планировщика
   117	        planner_mode = "llm" if "planner:llm" in plan.notes else "keyword"
   118	        qp = plan.query_params
   119	        if qp:
   120	            logger.info(

 succeeded in 0ms:
   210	    returns: [Channel, ClientCount, Visits, Revenue, AvgCheck, SalonName]
   211	    examples:
   212	      - question: "откуда приходят клиенты"
   213	      - question: "каналы привлечения"
   214	      - question: "эффективность каналов маркетинга"
   215	
   216	  # ══════════════════════════════════════════════════════
   217	  # spKDO_ClientList — списки клиентов по статусу КДО
   218	  # ══════════════════════════════════════════════════════
   219	
   220	  - id: clients_outflow
   221	    name: "Отток клиентов"
   222	    category: clients
   223	    procedure: spKDO_ClientList
   224	    description: "Клиенты без визита 31-240 дней сверх ожидаемой даты (DaysToAwaiting от -240 до -31). Соответствует DAX-мере «Статус клиента для обработки = Отток»."
   225	    allowed_group_by: [list, status, master]
   226	    parameters:
   227	      - name: date_from
   228	        type: date
   229	        required: false
   230	      - name: date_to
   231	        type: date
   232	        required: false
   233	      - name: object_id
   234	        type: int
   235	        required: true
   236	      - name: master_id
   237	        type: int
   238	        required: false
   239	      - name: filter
   240	        type: string
   241	        required: false
   242	        allowed_values: [all, birthday, forecast, leaving, noshow, outflow, quality]
   243	        default: outflow
   244	      - name: group_by
   245	        type: string
   246	        required: false
   247	        default: list
   248	      - name: top
   249	        type: int
   250	        required: false
   251	        default: 20
   252	    returns: [ClientName, Phone, Category, ClientStatus, LastVisit, FirstVisit, ExpectedNextVisit, DaysSinceLastVisit, DaysOverdue, ServicePeriodDays, TotalVisits, TotalSpent, LastCommResult, SalonName]
   253	    examples:
   254	      - question: "покажи отток клиентов"
   255	      - question: "кто из клиентов уходит в отток"
   256	      - question: "список оттока"
   257	
   258	  - id: clients_leaving
   259	    name: "Уходящие клиенты"
   260	    category: clients
   261	    procedure: spKDO_ClientList
   262	    description: "Клиенты без визита 1-30 дней сверх ожидаемой даты (DaysToAwaiting от -30 до -1). Соответствует DAX-мере «Уходящие»."
   263	    allowed_group_by: [list, status, master]
   264	    parameters:
   265	      - name: date_from
   266	        type: date
   267	        required: false
   268	      - name: date_to
   269	        type: date
   270	        required: false
   271	      - name: object_id
   272	        type: int
   273	        required: true
   274	      - name: master_id
   275	        type: int
   276	        required: false
   277	      - name: filter
   278	        type: string
   279	        required: false
   280	        allowed_values: [all, birthday, forecast, leaving, noshow, outflow, quality]

exec
/bin/zsh -lc "nl -ba src/swarm_powerbi_bot/services/topic_registry.py | sed -n '141,176p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "nl -ba src/swarm_powerbi_bot/telegram_bot.py | sed -n '220,250p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
   141	def detect_topic(question: str, last_topic: str = "") -> str:
   142	    """Определяет тему вопроса по ключевым словам (скоринг).
   143	
   144	    Если вопрос содержит только модификаторы (сравни, по неделям)
   145	    без явной темы — используем last_topic как контекст разговора.
   146	    """
   147	    text = question.lower()
   148	    best_id = DEFAULT_TOPIC
   149	    best_score = 0
   150	
   151	    for entry in TOPICS:
   152	        score = sum(1 for kw in entry.keywords if kw in text)
   153	        if score > best_score:
   154	            best_score = score
   155	            best_id = entry.topic_id
   156	
   157	    # Follow-up: вопрос без явной темы + есть предыдущий контекст
   158	    if last_topic and last_topic in _TOPICS_BY_ID:
   159	        # Если тема не найдена (score=0) — берём контекст
   160	        if best_score == 0:
   161	            return last_topic
   162	        # Если совпал только trend по модификаторам — это follow-up
   163	        if best_id == "trend" and best_score <= 2:
   164	            has_real_topic = any(
   165	                kw in text for entry in TOPICS
   166	                if entry.topic_id != "trend"
   167	                for kw in entry.keywords
   168	            )
   169	            if not has_real_topic:
   170	                return last_topic
   171	
   172	    # Тема не определена и нет контекста разговора — не выполняем SQL
   173	    if best_score == 0:
   174	        return "unknown"
   175	
   176	    return best_id

 succeeded in 0ms:
   220	                        user_data["object_id"] = object_id
   221	                except Exception:
   222	                    pass
   223	        # Fallback на default_object_id из конфига
   224	        if object_id is None and self.settings.default_object_id:
   225	            object_id = self.settings.default_object_id
   226	
   227	        # last_topic для контекста разговора (follow-up вопросы)
   228	        last_topic = ""
   229	        if user_data is not None:
   230	            last_topic = user_data.get("last_topic", "")
   231	
   232	        response = await self.orchestrator.handle_question(
   233	            UserQuestion(user_id=user_id, text=text, object_id=object_id,
   234	                         last_topic=last_topic),
   235	        )
   236	
   237	        # Сохраняем тему для следующего вопроса
   238	        if user_data is not None and response.topic:
   239	            user_data["last_topic"] = response.topic
   240	
   241	        if response.image:
   242	            # Описание — caption к картинке (до 1024 символов)
   243	            caption = self._fit_caption(response.answer)
   244	            try:
   245	                await message.reply_photo(
   246	                    response.image, caption=caption, parse_mode="Markdown",
   247	                )
   248	            except Exception:
   249	                # Markdown может сломаться — шлём без разметки
   250	                await message.reply_photo(response.image, caption=caption)

exec
/bin/zsh -lc "sed -n '240,420p' .specify/specs/001-semantic-aggregate-layer/spec.md" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
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
**чтобы** выбирать правильный агрегат для каждого вопроса пользователя.

**Почему P1**: без каталога LLM не знает какие запросы доступны.

**Independent Test**: aggregate-catalog.yaml содержит все агрегаты → LLM по каталогу корректно выбирает агрегат для типовых вопросов.

**Acceptance Scenarios**:

```gherkin
Scenario: Формат каталога
  Given aggregate-catalog.yaml
  Then каждый агрегат содержит:
    | Поле | Описание |
    | id | Уникальный идентификатор (snake_case) |
    | name | Название на русском |
    | description | Описание на русском: что возвращает, для каких вопросов |
    | parameters | Список параметров с типами и ограничениями |
    | returns | Описание колонок результата |
    | related_dax | Связанная DAX-мера (ссылка на semantic-model) |
    | examples | 2-3 примера вопросов пользователя → параметры вызова |

Scenario: LLM не видит SQL
  Given aggregate-catalog.yaml
  Then каталог НЕ содержит: SQL-код, имена stored procedures, connection strings

Scenario: Параметры строго типизированы
  Given aggregate-catalog.yaml
  Then каждый параметр имеет:
    - type: date | int | enum
    - Для enum: список допустимых значений
    - Для int: min/max ограничения
    - required/optional флаг
    - default значение (если optional)
```

---

## Phase 1: Каталог базовых агрегатов в БД

### P1 — US-007: SQL view/TVF для базовых агрегатов

**Как** разработчик,
**я хочу** обернуть существующие 17 v1 + 3 v2 stored procedures и gap-агрегаты в единообразные view/TVF, с предрассчитанными (materialized) агрегатами где overhead хранения ≤3x,
**чтобы** SQLAgent мог вызывать их через стандартный интерфейс каталога с минимальной латентностью.

**Почему P1**: без SQL-слоя нечего вызывать из PlannerAgent. Materialized агрегаты обеспечивают скорость при параллельных запросах.

**Independent Test**: вызвать агрегат `revenue_by_master` с параметрами `{date_from, date_to, object_id}` → получить ожидаемый результат из MSSQL.

**Acceptance Scenarios**:

```gherkin
Scenario: Единый интерфейс агрегатов
  Given набор агрегатов покрывающий 17 тем topic_registry
  When SQLAgent получает запрос из PlannerAgent
  Then SQLAgent вызывает агрегат по id из aggregate-catalog.yaml
  And передаёт типизированные параметры
  And получает результат в предсказуемом формате

Scenario: Backward compatibility
  Given существующие 77 тестов
  When новый SQLAgent вызывает агрегаты вместо прямых SP
  Then все 77 тестов продолжают проходить
  And результаты численно совпадают с прежними
```

---

## Phase 2: LLM выбирает агрегаты

### P1 — US-008: PlannerAgent с каталогом

**Как** пользователь,
**я хочу** задавать произвольные вопросы, а бот сам определяет какие данные запросить,
**чтобы** не ограничиваться 17 жёсткими темами.

**Почему P1**: главная бизнес-ценность — переход от keyword-matching к semantic planning.

**Independent Test**: вопрос "покажи средний чек по мастерам за март" → PlannerAgent выбирает агрегат `revenue_by_master` с параметрами `{group_by: master, date_from: 2026-03-01, date_to: 2026-03-31}`.

**Acceptance Scenarios**:

```gherkin
Scenario: LLM планирует в два шага
  Given пользователь спрашивает "какой отток за месяц?"
  When PlannerAgent выполняет шаг 1 (category selection)
  Then LLM получает компактный индекс категорий (клиенты, выручка, мастера, коммуникации...)
  And LLM выбирает категорию "клиенты" → подкатегория "отток"
  When PlannerAgent выполняет шаг 2 (aggregate selection)
  Then LLM получает детальные агрегаты только категории "клиенты"
  And план содержит: aggregate_id = "client_list_outflow", параметры = {filter: outflow, date_from, date_to, object_id}
  And план НЕ содержит SQL-код

Scenario: Кросс-доменный запрос (несколько категорий)
  Given пользователь спрашивает "сравни отток и оборот за две недели"
  When PlannerAgent выполняет шаг 1
  Then LLM выбирает две категории: "клиенты" + "выручка"
  When PlannerAgent выполняет шаг 2
  Then LLM получает агрегаты обеих категорий
  And план содержит агрегаты из разных доменов

Scenario: Fallback на keyword при недоступности LLM
  Given LLM недоступен (таймаут, ошибка)
  When пользователь задаёт вопрос
  Then PlannerAgent переключается на topic_registry (keyword-scoring)
  And пользователь получает ответ (пусть менее точный)

Scenario: Невозможный вопрос
  Given пользователь спрашивает "какая погода сегодня?"
  When PlannerAgent ищет подходящий агрегат в каталоге
  Then агрегат не найден
  And бот отвечает "Извините, у меня нет данных для ответа на этот вопрос"
  And бот НЕ пытается изобрести SQL-запрос
```

**Edge Cases**:
- Вопрос содержит имя мастера с опечаткой — SQLAgent делает запрос к tbMasters (per-request, всегда актуально), fuzzy-match по LIKE/SOUNDEX
- Вопрос без периода — используется период по умолчанию (последние 30 дней) или запрашивается через inline-кнопки (существующая механика)
- Follow-up вопрос ("а по неделям?") — LLM переиспользует контекст предыдущего запроса

---

### P1 — US-009: Multi-query SQLAgent

**Как** система,
**я хочу** выполнять несколько агрегатных запросов за один вопрос пользователя,
**чтобы** отвечать на сложные вопросы, требующие комбинации данных.

**Почему P1**: без multi-query невозможны фазы 3 (сравнения) и 4 (композиция).

**Independent Test**: PlannerAgent возвращает план с 2 запросами → SQLAgent выполняет оба → результаты передаются AnalystAgent.

**Acceptance Scenarios**:

```gherkin
Scenario: Выполнение нескольких запросов
  Given план содержит 2 агрегата: revenue_summary + client_outflow
  When SQLAgent обрабатывает план
  Then оба запроса выполняются
  And каждый запрос имеет таймаут 10 секунд
  And результаты возвращаются как список SQLInsight

Scenario: Ограничение количества запросов
  Given план содержит 12 агрегатов
  When SQLAgent проверяет план
  Then выполняются только первые 10
  And в diagnostics добавляется предупреждение "превышен лимит запросов"

Scenario: Частичный отказ
  Given план содержит 3 агрегата
  And второй агрегат возвращает ошибку (таймаут)
  When SQLAgent обрабатывает план
  Then первый и третий результаты возвращаются успешно
  And для второго — пустой результат с ошибкой в diagnostics
  And AnalystAgent работает с тем что получил
```

---

## Phase 3: Сравнения

exec
/bin/zsh -lc "sed -n '420,620p' .specify/specs/001-semantic-aggregate-layer/spec.md" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc 'rg -n "comparison|fallback|TopicRegistry|last_topic|group_by=status|keyword" .specify/specs/001-semantic-aggregate-layer/spec.md' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
6:**Input**: Переход от жёстко привязанных stored procedures к семантическому слою агрегатов: LLM выбирает агрегаты из каталога вместо keyword-matching по topic_registry.
15:1. **PlannerAgent** определяет план: LLM-путь (`LLMClient.plan_query()`) или keyword-fallback (`topic_registry.detect_topic()`)
45:| TopicRegistry | `services/topic_registry.py` | Сохраняется как fallback |
337:**Почему P1**: главная бизнес-ценность — переход от keyword-matching к semantic planning.
362:Scenario: Fallback на keyword при недоступности LLM
365:  Then PlannerAgent переключается на topic_registry (keyword-scoring)
597:- **FR-018**: TopicRegistry сохраняется как fallback при недоступности LLM
620:- **SC-005**: При недоступности LLM бот продолжает работать через keyword-fallback (17 тем)
629:- Q: Multi-query execution model (parallel/sequential, лимит запросов)? → A: Параллельно (asyncio.gather), до 10 запросов. Агрегаты предрассчитаны (materialized views/indexed views в MSSQL) если overhead хранения ≤3x. Real-time fallback для редких запросов.
631:- Q: Инструмент извлечения PBIX (Phase 0)? → A: Чистый Python (zipfile + json) как основной путь — нулевые зависимости, можно писать скрипты анализа модели. pbi-tools CLI как fallback если DataModelSchema не парсится стандартно.
632:- Q: Раскатка по фазам (big-bang vs feature flag vs по салонам)? → A: Big-bang. Клиентов немного, постепенная раскатка не нужна. TopicRegistry остаётся как fallback при отказе LLM, но не как параллельный режим работы.

 succeeded in 0ms:
## Phase 3: Сравнения

### P2 — US-010: Сравнение периодов

**Как** пользователь,
**я хочу** спросить "сравни выручку за март и апрель",
**чтобы** видеть динамику и конкретные числа роста/падения.

**Почему P2**: частый запрос владельцев салонов.

**Independent Test**: вопрос "сравни март и апрель" → PlannerAgent создаёт 2 запроса с разными периодами → AnalystAgent формирует сравнительный текст → ChartRenderer строит grouped bar chart.

**Acceptance Scenarios**:

```gherkin
Scenario: Сравнение двух периодов
  Given пользователь спрашивает "сравни выручку за март и апрель"
  When PlannerAgent составляет план
  Then план содержит 2 вызова одного агрегата с разными date_from/date_to
  And AnalystAgent получает оба результата
  And AnswerAgent формирует текст: "Выручка за март: X руб., за апрель: Y руб. Изменение: +/-Z%"
  And ChartRenderer строит grouped bar chart с двумя рядами

Scenario: Автоматическое определение периодов
  Given пользователь спрашивает "этот месяц vs прошлый"
  When PlannerAgent разбирает запрос
  Then "этот месяц" = текущий календарный месяц (с 1-го числа до сегодня)
  And "прошлый" = предыдущий полный календарный месяц

Scenario: Сравнение по мастерам
  Given пользователь спрашивает "кто лучше — Анна или Мария?"
  When PlannerAgent составляет план
  Then план содержит запросы по двум мастерам (fuzzy-match по имени)
  And AnalystAgent сравнивает ключевые метрики: выручка, клиенты, средний чек
```

**Edge Cases**:
- Сравнение текущего незавершённого месяца с полным прошлым — AnalystAgent отмечает что период неполный
- Имена мастеров с опечатками — fuzzy-matching по справочнику

---

## Phase 4: Композиция агрегатов

### P3 — US-011: Анализ причин

**Как** пользователь,
**я хочу** спросить "почему упала выручка?",
**чтобы** получить анализ какой фактор (клиенты, чек, загрузка) повлиял.

**Почему P3**: продвинутая аналитика, требует стабильных фаз 1-3.

**Independent Test**: вопрос "почему упала выручка?" → PlannerAgent запрашивает 4 агрегата (выручка/клиенты/средний чек/загрузка за 2 периода) → AnalystAgent анализирует что просело → ответ с конкретными числами.

**Acceptance Scenarios**:

```gherkin
Scenario: Декомпозиция вопроса в набор запросов
  Given пользователь спрашивает "почему упала выручка?"
  When PlannerAgent декомпозирует вопрос
  Then план содержит до 5 агрегатов:
    - revenue_summary за текущий и прошлый период
    - client_count за текущий и прошлый период
    - avg_check (средний чек)
  And AnalystAgent сравнивает метрики и определяет основной фактор

Scenario: Лимит запросов
  Given PlannerAgent планирует 10 запросов
  Then все выполняются параллельно (asyncio.gather) с таймаутом 10 секунд каждый
  And общее время ответа не превышает 15 секунд (параллельно)
  And пользователь видит typing indicator пока идёт обработка
```

---

## Защита БД (cross-cutting, все фазы)

### P1 — US-012: Защита от произвольного SQL

**Как** система,
**я хочу** гарантировать что LLM никогда не генерирует и не исполняет произвольный SQL,
**чтобы** предотвратить SQL-инъекции и несанкционированный доступ к данным.

**Почему P1**: безопасность — NON-NEGOTIABLE.

**Independent Test**: подать в PlannerAgent вопрос с SQL-инъекцией → бот возвращает "не могу ответить" вместо выполнения вредоносного кода.

**Acceptance Scenarios**:

```gherkin
Scenario: LLM выбирает только из каталога
  Given PlannerAgent получает вопрос
  When LLM возвращает plan
  Then plan.aggregate_id проверяется по whitelist из aggregate-catalog.yaml
  And если id не в каталоге — план отклоняется

Scenario: Параметры строго типизированы
  Given plan содержит параметры
  When SQLAgent валидирует параметры
  Then date_from/date_to — только формат YYYY-MM-DD
  And group_by — только из enum {master, service, day, week, month, salon, channel, status, reason, result, manager, list}
  And top_n — int в диапазоне [1, 50]
  And master_id, service_id — только int из справочника
  And любой невалидный параметр отклоняется (а не приводится)

Scenario: Read-only подключение
  Given SQLClient подключается к MSSQL
  Then используется SQL-пользователь с правами SELECT-only
  And попытка INSERT/UPDATE/DELETE/EXEC (кроме разрешённых SP) завершается ошибкой на уровне БД

Scenario: Логирование вызовов
  Given SQLAgent выполняет агрегатный запрос
  Then в лог записывается: user_id, timestamp, aggregate_id, параметры, время выполнения, количество строк
  And лог НЕ содержит: данные ответа, connection strings, токены

Scenario: SQL-инъекция в вопросе
  Given пользователь отправляет "'; DROP TABLE tbClients; --"
  When PlannerAgent обрабатывает вопрос
  Then LLM не находит подходящего агрегата
  And бот отвечает "не могу ответить на этот вопрос"
  And ни один SQL-запрос не выполняется
```

---

## Обновление семантики (cross-cutting)

### P3 — US-013: CI-пайплайн обновления PBIX

**Как** разработчик,
**я хочу** чтобы при изменении PBIX-файла автоматически пересобиралась семантическая модель,
**чтобы** каталоги и агрегаты всегда были синхронизированы с отчётом.

**Почему P3**: автоматизация, не блокирует основную функциональность.

**Independent Test**: изменить PBIX → запустить CI → проверить что semantic-model.yaml обновился и агрегаты прошли валидацию.

**Acceptance Scenarios**:

```gherkin
Scenario: PBIX изменился → пересборка
  Given PBIX-файл обновлён в репозитории
  When срабатывает CI-задача
  Then semantic-model.yaml пересобирается
  And pbix-to-sql-mapping.yaml обновляется
  And semantic-catalog.yaml обновляется
  And aggregate-catalog.yaml проверяется на совместимость
  And если есть новые gaps — создаётся issue

Scenario: Обратная совместимость
  Given обновлённый semantic-model.yaml
  When проверяются существующие агрегаты
  Then если агрегат ссылается на удалённую колонку/таблицу — CI падает с ошибкой
  And сообщение указывает какой агрегат и какая зависимость нарушена
```

---

## Functional Requirements

- **FR-001**: Система извлекает семантическую модель из PBIX-файла в формат semantic-model.yaml
- **FR-002**: Система создаёт маппинг PBIX→SQL в формате pbix-to-sql-mapping.yaml
- **FR-003**: Система генерирует semantic-catalog.yaml с бизнес-сущностями, метриками и правилами на русском языке
- **FR-004**: Система выполняет gap-анализ и создаёт gaps.md
- **FR-005**: Для каждого gap система генерирует SQL view/TVF с верификацией против DAX-оригинала
- **FR-006**: Система формирует aggregate-catalog.yaml с описанием каждого агрегата
- **FR-007**: PlannerAgent работает в два шага: (1) выбор категорий по компактному индексу, (2) выбор конкретных агрегатов из детального каталога выбранных категорий. Поддерживает кросс-доменные запросы (несколько категорий за раз)
- **FR-008**: SQLAgent выполняет до 10 агрегатных запросов параллельно (asyncio.gather) за один вопрос пользователя, каждый с таймаутом 10 секунд
- **FR-009**: AnalystAgent принимает массив результатов от нескольких агрегатов и формирует единый ответ
- **FR-010**: ChartRenderer поддерживает сравнительные графики (grouped bar, multi-line)
- **FR-011**: При сравнении периодов PlannerAgent автоматически определяет даты "этот месяц", "прошлый квартал" и т.д.
- **FR-012**: При вопросе без подходящего агрегата система отвечает "не могу ответить" без выполнения SQL
- **FR-013**: LLM никогда не генерирует SQL — только выбирает aggregate_id + параметры из каталога
- **FR-014**: Все параметры агрегатов валидируются по типу и whitelist перед выполнением
- **FR-015**: SQLClient использует read-only подключение к MSSQL
- **FR-016**: Все вызовы агрегатов логируются: user_id, timestamp, aggregate_id, параметры, время выполнения
- **FR-017**: Существующие 77 тестов продолжают проходить (backward compatibility)
- **FR-018**: TopicRegistry сохраняется как fallback при недоступности LLM
- **FR-019**: Документация (docs/) обновляется при изменении API, моделей, каталогов
- **FR-020**: При изменении PBIX — CI пересобирает semantic-model.yaml и проверяет совместимость агрегатов

## Key Entities

| Entity | Описание | Связи |
|---|---|---|
| Клиент (Client) | Посетитель салона: имя, телефон, категория, канал привлечения, дата рождения | Записывается к Мастеру на Услугу, совершает Визиты, имеет Статус |
| Мастер (Master) | Специалист салона: имя, рейтинг, категория, планы обучения | Оказывает Услуги Клиентам в рамках Визитов |
| Услуга (Service) | Процедура: название, категория, первичная/вторичная, период повторного визита | Оказывается Мастером Клиенту в рамках Визита |
| Визит (Record) | Факт оказания услуги: дата, статус (1=выполнен, -1=отменён, 0=запланирован), длительность, сумма | Связывает Клиента, Мастера, Услугу, Салон |
| Салон (Dataset/Object) | Точка оказания услуг: ObjectId, название | Содержит Мастеров, принимает Клиентов |
| Коммуникация | Контакт с клиентом: дата, причина, тип, результат, менеджер | Связана с Клиентом и Салоном |
| Абонемент | Пакет услуг: номер, баланс, срок, статус | Принадлежит Клиенту в Салоне |
| Статус клиента | Рассчитанное состояние: Прогноз / Уходящие / Отток / Контроль качества / Лист ожидания / Недошедшие | Вычисляется из Визитов + ServicePeriod (default 33 дня) |

## Success Criteria

- **SC-001**: Пользователь получает корректный ответ на любой из 17 существующих типов вопросов (регрессия)
- **SC-002**: Пользователь получает ответ на вопросы, комбинирующие несколько тем ("выручка по мастерам с разбивкой по неделям")
- **SC-003**: Пользователь может сравнивать два периода или двух мастеров и получает числа изменений
- **SC-004**: На вопрос "почему упала выручка?" бот декомпозирует вопрос и находит основной фактор
- **SC-005**: При недоступности LLM бот продолжает работать через keyword-fallback (17 тем)

codex
I found a branch-level integration risk: the new `comparison:fallback` plan is still tagged as `planner_v2:keyword`, and the orchestrator explicitly refuses to execute any keyword `MultiPlan`. I’m checking the legacy SQL path now to confirm whether that means the new 2-query fallback is effectively dead code at runtime.
exec
/bin/zsh -lc "sed -n '1,210p' src/swarm_powerbi_bot/services/sql_client.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
from __future__ import annotations

import asyncio
import logging
import re
import time
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from ..config import Settings
from ..models import AggregateResult, QueryParams
from .topic_registry import detect_topic, get_procedure

if TYPE_CHECKING:
    from .aggregate_registry import AggregateRegistry

logger = logging.getLogger(__name__)

try:
    import pyodbc  # type: ignore
except Exception:  # pragma: no cover
    pyodbc = None
    logger.warning("pyodbc not available — SQL queries will be disabled")


# ── Извлечение дат из русского текста ────────────────────────

_MONTH_MAP: dict[str, int] = {
    "январ": 1,
    "феврал": 2,
    "март": 3,
    "апрел": 4,
    "мая": 5,
    "май": 5,
    "июн": 6,
    "июл": 7,
    "август": 8,
    "сентябр": 9,
    "октябр": 10,
    "ноябр": 11,
    "декабр": 12,
}

_RE_MONTH = re.compile(
    r"за\s+(январ\w*|феврал\w*|март\w*|апрел\w*|ма[йя]\w*|"
    r"июн\w*|июл\w*|август\w*|сентябр\w*|октябр\w*|ноябр\w*|декабр\w*)"
    r"(?:\s+(\d{4}))?",
    re.IGNORECASE,
)

_RE_RANGE = re.compile(
    r"с\s+(\d{1,2})\s+по\s+(\d{1,2})\s+"
    r"(январ\w*|феврал\w*|март\w*|апрел\w*|ма[йя]\w*|"
    r"июн\w*|июл\w*|август\w*|сентябр\w*|октябр\w*|ноябр\w*|декабр\w*)"
    r"(?:\s+(\d{4}))?",
    re.IGNORECASE,
)


def _match_month(text: str) -> int:
    low = text.lower()
    for stem, num in _MONTH_MAP.items():
        if low.startswith(stem):
            return num
    return 0


_PERIOD_HINTS = (
    "недел",
    "месяц",
    "месяч",
    "меся",
    "квартал",
    "год",
    "вчера",
    "сегодн",
    "полугод",
    "полгод",
)


def has_period_hint(question: str) -> bool:
    """Проверяет, указан ли в вопросе какой-либо период."""
    text = question.lower()
    if _RE_MONTH.search(text) or _RE_RANGE.search(text):
        return True
    return any(h in text for h in _PERIOD_HINTS)


def extract_date_params(question: str) -> dict[str, date]:
    """Извлекает @DateFrom / @DateTo из вопроса на русском."""
    today = date.today()
    text = question.lower()

    # «за январь 2025»
    m = _RE_MONTH.search(text)
    if m:
        month = _match_month(m.group(1))
        year = int(m.group(2)) if m.group(2) else today.year
        if month:
            first = date(year, month, 1)
            if month == 12:
                last = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last = date(year, month + 1, 1) - timedelta(days=1)
            return {"DateFrom": first, "DateTo": last}

    # «с 1 по 15 марта»
    m = _RE_RANGE.search(text)
    if m:
        day_from, day_to = int(m.group(1)), int(m.group(2))
        month = _match_month(m.group(3))
        year = int(m.group(4)) if m.group(4) else today.year
        if month:
            return {
                "DateFrom": date(year, month, day_from),
                "DateTo": date(year, month, day_to),
            }

    # «вчера»
    if "вчера" in text:
        yesterday = today - timedelta(days=1)
        return {"DateFrom": yesterday, "DateTo": yesterday}

    # «сегодня»
    if "сегодн" in text:
        return {"DateFrom": today, "DateTo": today}

    # «за последнюю неделю» / «за неделю»
    if "недел" in text:
        return {"DateFrom": today - timedelta(days=7), "DateTo": today}

    # «за последний месяц» / «за месяц» / «за меся»
    if "месяц" in text or "меся" in text:
        return {"DateFrom": today - timedelta(days=30), "DateTo": today}

    # «за квартал»
    if "квартал" in text:
        return {"DateFrom": today - timedelta(days=90), "DateTo": today}

    # «за полугодие»
    if "полугод" in text or "полгод" in text:
        return {"DateFrom": today - timedelta(days=180), "DateTo": today}

    # «за год»
    if "год" in text and "новый год" not in text:
        return {"DateFrom": today - timedelta(days=365), "DateTo": today}

    # По умолчанию — последние 30 дней
    return {"DateFrom": today - timedelta(days=30), "DateTo": today}


_RE_OBJECT_ID = re.compile(r"салон[а-яё]*\s*(?:id\s*)?(\d{4,})", re.IGNORECASE)
_RE_MASTER_ID = re.compile(r"мастер[а-яё]*\s*(?:id\s*)?(\d{4,})", re.IGNORECASE)


def _extract_object_id(question: str) -> int | None:
    """Извлекает ObjectId (SalonId/YClientsId) из вопроса."""
    m = _RE_OBJECT_ID.search(question)
    return int(m.group(1)) if m else None


def _extract_master_id(question: str) -> int | None:
    """Извлекает MasterId из вопроса."""
    m = _RE_MASTER_ID.search(question)
    return int(m.group(1)) if m else None


class SQLClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def execute_query(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Выполняет произвольный параметризованный SELECT-запрос.

        Используется MasterResolver для поиска мастеров.
        """
        conn_str = self.settings.sql_connection_string()
        if not conn_str or pyodbc is None:
            logger.warning("execute_query: no connection string or pyodbc unavailable")
            return []

        def _sync() -> list[dict[str, Any]]:
            conn = pyodbc.connect(conn_str, timeout=10)
            try:
                cursor = conn.cursor()
                # Извлекаем имена параметров из SQL в порядке появления
                param_names = re.findall(r"@(\w+)", sql)
                p = params or {}
                sql_args = [p[name] for name in param_names if name in p]
                query = re.sub(r"@\w+", "?", sql)
                cursor.execute(query, sql_args)
                columns = (
                    [col[0] for col in cursor.description] if cursor.description else []
                )
                rows = []
                for row in cursor.fetchall():
                    rows.append(dict(zip(columns, row)))
                return rows
            finally:
                conn.close()

        return await asyncio.to_thread(_sync)

    async def execute_aggregate(
        self,

exec
/bin/zsh -lc "nl -ba src/swarm_powerbi_bot/orchestrator.py | sed -n '80,110p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
    80	        # T031: Если есть MultiPlan и aggregate_registry — выполняем все запросы через SQLAgent.run_multi()
    81	        # Пропускаем run_multi() для keyword-fallback планов: их aggregate_id — topic-идентификаторы,
    82	        # не валидные catalog aggregate_ids, и они провалят registry.validate().
    83	        multi_results: list[AggregateResult] = []
    84	        if (
    85	            multi_plan
    86	            and multi_plan.queries
    87	            and self.aggregate_registry is not None
    88	            and "planner_v2:keyword" not in (multi_plan.notes or [])
    89	        ):
    90	            diagnostics["multi_plan_intent"] = multi_plan.intent
    91	            diagnostics["multi_plan_queries"] = str(len(multi_plan.queries))
    92	            try:
    93	                multi_results = await self.sql_agent.run_multi(
    94	                    multi_plan,
    95	                    self.aggregate_registry,
    96	                    logger_=self.query_logger,
    97	                )
    98	                ok_count = sum(1 for r in multi_results if r.status == "ok")
    99	                diagnostics["multi_plan_ok"] = str(ok_count)
   100	                logger.info(
   101	                    "[MULTI_SQL] queries=%d ok=%d",
   102	                    len(multi_results),
   103	                    ok_count,
   104	                )
   105	            except Exception as exc:
   106	                logger.error("[MULTI_SQL] ERROR: %s", exc)
   107	                diagnostics["multi_sql_error"] = str(exc)
   108	        elif multi_plan and multi_plan.queries:
   109	            # Degradation: LLM спланировал запросы, но registry не инициализирован
   110	            # (нет каталога агрегатов) — запросы не могут быть валидированы и выполнены.

exec
/bin/zsh -lc "rg -n \"def fetch_rows\\(|planner_v2:keyword|run_multi\\(\" src/swarm_powerbi_bot/services/sql_client.py src/swarm_powerbi_bot/orchestrator.py src/swarm_powerbi_bot/agents/planner.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
src/swarm_powerbi_bot/services/sql_client.py:506:    async def fetch_rows(
src/swarm_powerbi_bot/orchestrator.py:51:                multi_plan = await self.planner.run_multi(question)
src/swarm_powerbi_bot/orchestrator.py:80:        # T031: Если есть MultiPlan и aggregate_registry — выполняем все запросы через SQLAgent.run_multi()
src/swarm_powerbi_bot/orchestrator.py:81:        # Пропускаем run_multi() для keyword-fallback планов: их aggregate_id — topic-идентификаторы,
src/swarm_powerbi_bot/orchestrator.py:88:            and "planner_v2:keyword" not in (multi_plan.notes or [])
src/swarm_powerbi_bot/orchestrator.py:93:                multi_results = await self.sql_agent.run_multi(
src/swarm_powerbi_bot/orchestrator.py:136:        # Пропускаем legacy SQL если run_multi() уже получил данные — иначе дублируем запрос
src/swarm_powerbi_bot/orchestrator.py:212:            analysis = await self.analyst_agent.run_multi(
src/swarm_powerbi_bot/agents/planner.py:207:    async def run_multi(self, question: UserQuestion) -> MultiPlan:
src/swarm_powerbi_bot/agents/planner.py:404:                notes=["planner_v2:keyword", "comparison:fallback"],
src/swarm_powerbi_bot/agents/planner.py:419:            notes=["planner_v2:keyword"],

exec
/bin/zsh -lc "sed -n '1,280p' src/swarm_powerbi_bot/agents/analyst.py" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
from __future__ import annotations

import json
from datetime import date
from typing import Literal

from .base import Agent
from ..models import AggregateResult, AnalysisResult, ComparisonResult, ModelInsight, MultiPlan, Plan, SQLInsight, UserQuestion
from ..services.llm_client import LLMClient
from ..services.topic_registry import get_description

# ── Подсказки для описания графиков ──────────────────────────

_CHART_HINTS: dict[str, str] = {
    "statistics": "На графике показаны ключевые KPI: визиты, клиенты, выручка, средний чек.",
    "trend": "На графике показана динамика по неделям: визиты, клиенты и выручка.",
    "outflow": "На графике показаны клиенты в оттоке — отсортированы по просроченности.",
    "leaving": "На графике показаны уходящие клиенты — просрочка 1-30 дней.",
    "forecast": "На графике показаны клиенты, которых ожидаем в ближайшие 14 дней.",
    "communications": "На графике показана сводка коммуникаций по типам и результатам.",
    "referrals": "На диаграмме показано распределение клиентов по каналам привлечения.",
    "masters": "На графике показаны мастера по выручке/загрузке.",
    "services": "На графике показаны услуги по выручке.",
    "quality": "На графике показаны клиенты на контроле качества.",
    "noshow": "На графике показаны недошедшие клиенты.",
    "opz": "На графике показаны оперативные записи.",
    "training": "На графике показано выполнение плана по обучению мастеров.",
    "attachments": "На графике показаны абонементы по статусам.",
    "all_clients": "На графике показана клиентская база.",
}

# Тематические follow-up подсказки
_TOPIC_FOLLOW_UPS: dict[str, list[str]] = {
    "all_clients": [
        "Хотите посмотреть клиентов по конкретному салону?",
        "Показать динамику клиентской базы по месяцам?",
    ],
    "outflow": [
        "Хотите сравнить отток по салонам?",
        "Показать причины оттока за другой период?",
    ],
    "leaving": [
        "Показать уходящих по конкретному мастеру?",
        "Хотите увидеть историю визитов этих клиентов?",
    ],
    "statistics": [
        "Хотите детализацию по конкретному показателю?",
        "Сравнить KPI за разные периоды?",
    ],
    "trend": [
        "Показать тренд по другому показателю?",
        "Хотите прогноз на основе текущего тренда?",
    ],
    "forecast": [
        "Хотите прогноз по конкретному мастеру?",
        "Показать загрузку по салонам?",
    ],
    "communications": [
        "Хотите посмотреть результативность обзвонов?",
        "Показать коммуникации по конкретному менеджеру?",
    ],
    "referrals": [
        "Показать рефережи по салонам?",
        "Хотите увидеть конверсию рефералов в постоянных клиентов?",
    ],
    "quality": [
        "Показать оценки по конкретному мастеру?",
        "Хотите увидеть динамику качества за период?",
    ],
    "attachments": [
        "Показать абонементы с истекающим сроком?",
        "Хотите увидеть статистику продлений?",
    ],
    "birthday": [
        "Показать именинников на следующую неделю?",
        "Хотите увидеть кого ещё не поздравили?",
    ],
    "waitlist": [
        "Показать лист ожидания по услугам?",
        "Хотите увидеть среднее время ожидания?",
    ],
    "training": [
        "Показать кто ещё не прошёл обучение?",
        "Хотите статистику по завершённости курсов?",
    ],
    "masters": [
        "Сравнить мастеров по загрузке?",
        "Показать выручку по мастерам за период?",
    ],
    "services": [
        "Показать топ-5 популярных услуг?",
        "Хотите динамику среднего чека по месяцам?",
    ],
    "noshow": [
        "Показать недошедших за другой период?",
        "Хотите увидеть результаты обзвона недошедших?",
    ],
    "opz": [
        "Показать ОПЗ по конкретному менеджеру?",
        "Хотите статистику конверсии ОПЗ?",
    ],
}

_DEFAULT_FOLLOW_UPS = [
    "Уточните период анализа (неделя/месяц/квартал)",
    "Уточните разрез: салон, мастер, категория",
]


class AnalystAgent(Agent):
    name = "analyst"

    SYSTEM_PROMPT = (
        "Ты — дашборд салона красоты (КДО). Озвучиваешь данные из SQL текстом.\n\n"
        "СЛОВАРЬ ПОЛЕЙ (используй эти названия при описании):\n"
        "• ClientName — имя клиента\n"
        "• TotalSpent — сумма трат этого клиента за всю историю (₽)\n"
        "• TotalVisits — количество визитов этого клиента\n"
        "• DaysSinceLastVisit — дней с последнего визита\n"
        "• DaysOverdue — дней просрочки (на сколько опоздал от ожидаемого визита)\n"
        "• ServicePeriodDays — средний период между визитами клиента (дни)\n"
        "• LastVisit — дата последнего визита\n"
        "• ExpectedNextVisit — ожидаемая дата следующего визита\n"
        "• Category — категория клиента в CRM\n"
        "• ClientStatus — статус клиента (отток/уходящий/прогноз и т.д.)\n"
        "• SalonName — название салона\n"
        "• Revenue / AvgCheck — выручка / средний чек\n\n"
        "ПРАВИЛА (нарушение = брак):\n"
        "1. Описывай ТОЛЬКО данные из sql_rows. Ни слова от себя.\n"
        "2. ЗАПРЕЩЕНО: рекомендации, оценки, прогнозы, "
        "слова «срочно/критично/тревожно/VIP/топ/рекомендую/необходимо».\n"
        "3. ЗАПРЕЩЕНО: таблицы (| --- |). Только текст и • списки.\n"
        "4. ЗАПРЕЩЕНО: выдумывать ранги, категории, причины.\n"
        "5. Формат: МАКСИМУМ 4 предложения. Тема, период, кол-во записей, "
        "главные цифры. Если график — одно предложение что на осях. "
        "Это чат в Telegram — стена текста = плохо.\n"
        "6. Числа относятся к КОНКРЕТНОМУ клиенту, не ко всем сразу. "
        "TotalSpent=8000 значит «этот клиент потратил 8000₽», "
        "а НЕ «общая сумма 8000₽».\n\n"
        "Пример:\n"
        "«Отток за 30 дней: 20 клиентов. Просрочка от 31 до 240 дней. "
        "Клиент с наибольшей историей трат — 57 000 ₽ за 59 визитов. "
        "На графике — клиенты по убыванию просрочки.»"
    )

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def run(
        self,
        question: UserQuestion,
        plan: Plan,
        sql_insight: SQLInsight,
        model_insight: ModelInsight,
        diagnostics: dict[str, str],
        *,
        has_chart: bool = False,
    ) -> AnalysisResult:
        fallback = self._fallback_summary(
            question, plan, sql_insight, model_insight, diagnostics, has_chart=has_chart,
        )

        user_prompt = self._compose_prompt(
            question, plan, sql_insight, model_insight, diagnostics, has_chart=has_chart,
        )
        answer = await self.llm_client.synthesize(self.SYSTEM_PROMPT, user_prompt, fallback)

        confidence = "low"
        if sql_insight.rows and model_insight.metrics:
            confidence = "high"
        elif sql_insight.rows or model_insight.metrics:
            confidence = "medium"

        follow_ups = _TOPIC_FOLLOW_UPS.get(plan.topic, _DEFAULT_FOLLOW_UPS)

        return AnalysisResult(
            answer=answer,
            confidence=confidence,
            follow_ups=follow_ups,
            diagnostics=diagnostics,
        )

    def _compose_prompt(
        self,
        question: UserQuestion,
        plan: Plan,
        sql_insight: SQLInsight,
        model_insight: ModelInsight,
        diagnostics: dict[str, str],
        *,
        has_chart: bool = False,
    ) -> str:
        topic_desc = get_description(plan.topic)
        data: dict = {
            "question": question.text,
            "topic": plan.topic,
            "topic_description": topic_desc,
            "sql_summary": sql_insight.summary,
            "row_count": len(sql_insight.rows),
            "sql_rows": sql_insight.rows[:10],
            "sql_params": {k: str(v) for k, v in sql_insight.params.items()},
            "model_summary": model_insight.summary,
            "model_metrics": model_insight.metrics,
        }
        if has_chart:
            chart_hint = _CHART_HINTS.get(plan.topic, "К ответу прикреплён график.")
            data["chart_attached"] = True
            data["chart_description_hint"] = chart_hint
        return json.dumps(data, ensure_ascii=False)

    def _fallback_summary(
        self,
        question: UserQuestion,
        plan: Plan,
        sql_insight: SQLInsight,
        model_insight: ModelInsight,
        diagnostics: dict[str, str],
        *,
        has_chart: bool = False,
    ) -> str:
        topic_desc = get_description(plan.topic)
        lines = []

        if topic_desc:
            lines.append(f"*{topic_desc}*")
            lines.append("")

        if sql_insight.rows:
            lines.append(f"Найдено записей: {len(sql_insight.rows)}")
            # Показываем ключевые поля первой строки человеко-читаемо
            row = sql_insight.rows[0]
            preview_fields = []
            for key, val in row.items():
                if key in ("SalonName",) or val is None:
                    continue
                preview_fields.append(f"• {key}: {val}")
                if len(preview_fields) >= 5:
                    break
            if preview_fields:
                lines.append("")
                lines.append("*Пример:*")
                lines.extend(preview_fields)
        else:
            lines.append("Данных за указанный период не найдено.")

        if has_chart:
            chart_hint = _CHART_HINTS.get(plan.topic, "")
            if chart_hint:
                lines.append("")
                lines.append(chart_hint)

        follow_ups = _TOPIC_FOLLOW_UPS.get(plan.topic, _DEFAULT_FOLLOW_UPS)
        if follow_ups:
            lines.append("")
            lines.append("_Попробуйте уточнить период или фильтры._")

        return "\n".join(lines)

    async def run_multi(
        self,
        question: str,
        results: list[AggregateResult],
        plan: MultiPlan,
    ) -> AnalysisResult:
        """T030/T039: Синтезирует результаты нескольких агрегатных запросов в один ответ.

        - Пропускает результаты со статусом != "ok"
        - Использует label из AggregateResult для контекста
        - При intent="decomposition": сравнивает метрики по периодам и выявляет главный фактор
        - Возвращает AnalysisResult с ответом на вопрос
        """
        ok_results = [r for r in results if r.status == "ok"]
        skipped = len(results) - len(ok_results)

        # T039: специальная ветка для факторного анализа
        if plan.intent == "decomposition":
            return self._synthesize_decomposition(question, ok_results, plan, skipped)

        fallback = self._fallback_multi(question, ok_results, plan, skipped)


exec
/bin/zsh -lc 'rg -n "incomplete_period|format_comparison|ComparisonResult|period_a|period_b" src/swarm_powerbi_bot/agents/analyst.py tests/test_comparison.py' in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
src/swarm_powerbi_bot/agents/analyst.py:8:from ..models import AggregateResult, AnalysisResult, ComparisonResult, ModelInsight, MultiPlan, Plan, SQLInsight, UserQuestion
src/swarm_powerbi_bot/agents/analyst.py:493:    def _is_incomplete_period(date_to_str: str) -> bool:
src/swarm_powerbi_bot/agents/analyst.py:536:    def format_comparison(
src/swarm_powerbi_bot/agents/analyst.py:538:        comparison: ComparisonResult,
src/swarm_powerbi_bot/agents/analyst.py:540:        incomplete_period_a: bool = False,
src/swarm_powerbi_bot/agents/analyst.py:541:        incomplete_period_b: bool = False,
src/swarm_powerbi_bot/agents/analyst.py:550:        label_a = comparison.period_a or "Период 1"
src/swarm_powerbi_bot/agents/analyst.py:551:        label_b = comparison.period_b or "Период 2"
src/swarm_powerbi_bot/agents/analyst.py:553:        if incomplete_period_a:
src/swarm_powerbi_bot/agents/analyst.py:555:        if incomplete_period_b:
tests/test_comparison.py:24:    ComparisonResult,
tests/test_comparison.py:409:    def test_is_incomplete_period_today(self):
tests/test_comparison.py:412:        assert AnalystAgent._is_incomplete_period(today) is True
tests/test_comparison.py:414:    def test_is_incomplete_period_future(self):
tests/test_comparison.py:417:        assert AnalystAgent._is_incomplete_period(future) is True
tests/test_comparison.py:419:    def test_is_incomplete_period_past(self):
tests/test_comparison.py:422:        assert AnalystAgent._is_incomplete_period(past) is False
tests/test_comparison.py:424:    def test_is_incomplete_period_empty_string(self):
tests/test_comparison.py:425:        assert AnalystAgent._is_incomplete_period("") is False
tests/test_comparison.py:427:    def test_is_incomplete_period_invalid_string(self):
tests/test_comparison.py:428:        assert AnalystAgent._is_incomplete_period("not-a-date") is False
tests/test_comparison.py:430:    def test_format_comparison_marks_incomplete_period_a(self):
tests/test_comparison.py:431:        """Если period_a неполный → в тексте есть "(неполный период)"."""
tests/test_comparison.py:445:        comparison = ComparisonResult(
tests/test_comparison.py:446:            period_a="Этот месяц",
tests/test_comparison.py:447:            period_b="Прошлый месяц",
tests/test_comparison.py:451:        text = analyst.format_comparison(comparison, incomplete_period_a=True)
tests/test_comparison.py:454:    def test_format_comparison_no_incomplete_marker_when_full(self):
tests/test_comparison.py:469:        comparison = ComparisonResult(
tests/test_comparison.py:470:            period_a="Прошлый месяц",
tests/test_comparison.py:471:            period_b="Позапрошлый месяц",
tests/test_comparison.py:475:        text = analyst.format_comparison(comparison)
tests/test_comparison.py:478:    def test_format_comparison_includes_delta(self):
tests/test_comparison.py:493:        comparison = ComparisonResult(
tests/test_comparison.py:494:            period_a="Апрель",
tests/test_comparison.py:495:            period_b="Март",
tests/test_comparison.py:499:        text = analyst.format_comparison(comparison)
tests/test_comparison.py:503:    def test_format_comparison_negative_delta(self):
tests/test_comparison.py:518:        comparison = ComparisonResult(
tests/test_comparison.py:519:            period_a="Апрель",
tests/test_comparison.py:520:            period_b="Март",
tests/test_comparison.py:524:        text = analyst.format_comparison(comparison)
tests/test_comparison.py:530:    def test_format_comparison_empty_data(self):
tests/test_comparison.py:535:        comparison = ComparisonResult(
tests/test_comparison.py:536:            period_a="Период 1",
tests/test_comparison.py:537:            period_b="Период 2",
tests/test_comparison.py:541:        text = analyst.format_comparison(comparison)

codex
I have enough static evidence for several failures. I’m validating the most important ones with direct function calls so the findings are grounded in actual runtime behavior, not just code reading.
2026-04-15T16:00:01.790014Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/zsh -lc "PYTHONPATH=src python - <<'PY'
from swarm_powerbi_bot.services.topic_registry import detect_topic
cases = [
    ('сравни выручку за март и февраль','outflow'),
    ('сравни выручку за март и февраль',''),
    ('сравни по салонам','clients_outflow'),
]
for text,last in cases:
    print(text, '| last=', last, '=>', detect_topic(text, last_topic=last))
PY"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"zsh:1: can't create temp file for here document: operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"zsh:1: can't create temp file for here document: operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
2026-04-15T16:00:01.790007Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/zsh -lc "PYTHONPATH=src python - <<'PY'
from swarm_powerbi_bot.agents.planner import PlannerAgent
from swarm_powerbi_bot.models import UserQuestion
import asyncio

planner = PlannerAgent()
for q in [
    UserQuestion(user_id='1', text='сравни выручку за март и февраль', last_topic='outflow'),
    UserQuestion(user_id='1', text='сравни выручку за март и февраль'),
    UserQuestion(user_id='1', text='сравни по салонам', last_topic='clients_outflow', object_id=123),
    UserQuestion(user_id='1', text='сравни по месяцам за два месяца', last_topic='clients_outflow', object_id=123),
]:
    mp = asyncio.run(planner.run_multi(q))
    print('Q:', q.text, 'last_topic=', q.last_topic)
    print('intent=', mp.intent, 'topic=', mp.topic)
    for aq in mp.queries:
        print('  ', aq.aggregate_id, dict(aq.params), aq.label)
    print('notes=', mp.notes)
    print('---')
PY"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"zsh:1: can't create temp file for here document: operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"zsh:1: can't create temp file for here document: operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
exec
/bin/zsh -lc "PYTHONPATH=src python -c \"from swarm_powerbi_bot.agents.planner import PlannerAgent; from swarm_powerbi_bot.models import UserQuestion; import asyncio; planner=PlannerAgent(); cases=[UserQuestion(user_id='1', text='сравни выручку за март и февраль', last_topic='outflow'), UserQuestion(user_id='1', text='сравни выручку за март и февраль'), UserQuestion(user_id='1', text='сравни по салонам', last_topic='clients_outflow', object_id=123), UserQuestion(user_id='1', text='сравни по месяцам за два месяца', last_topic='clients_outflow', object_id=123)];
for q in cases:
 mp=asyncio.run(planner.run_multi(q)); print('Q:', q.text, '| last=', q.last_topic, '| intent=', mp.intent, '| topic=', mp.topic, '| queries=', [(aq.aggregate_id, dict(aq.params), aq.label) for aq in mp.queries], '| notes=', mp.notes)\"" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
exec
/bin/zsh -lc "PYTHONPATH=src python -c \"from swarm_powerbi_bot.services.topic_registry import detect_topic; cases=[('сравни выручку за март и февраль','outflow'),('сравни выручку за март и февраль',''),('сравни по салонам','clients_outflow')]; [print(text, '| last=', last, '=>', detect_topic(text, last_topic=last)) for text,last in cases]\"" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 exited 1 in 259ms:
/Users/zerocold/.matplotlib is not a writable directory
Traceback (most recent call last):
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 545, in _get_config_or_cache_dir
    tmpdir = tempfile.mkdtemp(prefix="matplotlib-")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 373, in mkdtemp
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

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot/src/swarm_powerbi_bot/services/__init__.py", line 1, in <module>
    from .chart_renderer import render_chart
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot/src/swarm_powerbi_bot/services/chart_renderer.py", line 15, in <module>
    import matplotlib
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 1010, in <module>
    rcParams._update_raw(_rc_params_in_file(matplotlib_fname()))
                                            ^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 636, in matplotlib_fname
    for fname in gen_candidates():
                 ^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 633, in gen_candidates
    yield os.path.join(get_configdir(), 'matplotlibrc')
                       ^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 340, in wrapper
    ret = func(**kwargs)
          ^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 579, in get_configdir
    return _get_config_or_cache_dir(_get_xdg_config_dir)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 547, in _get_config_or_cache_dir
    raise OSError(
OSError: Matplotlib requires access to a writable cache directory, but there was an issue with the default path (/Users/zerocold/.matplotlib), and a temporary directory could not be created; set the MPLCONFIGDIR environment variable to a writable directory

 exited 1 in 259ms:
/Users/zerocold/.matplotlib is not a writable directory
Traceback (most recent call last):
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 545, in _get_config_or_cache_dir
    tmpdir = tempfile.mkdtemp(prefix="matplotlib-")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/lib/python3.12/tempfile.py", line 373, in mkdtemp
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

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot/src/swarm_powerbi_bot/agents/__init__.py", line 1, in <module>
    from .analyst import AnalystAgent
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot/src/swarm_powerbi_bot/agents/analyst.py", line 9, in <module>
    from ..services.llm_client import LLMClient
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot/src/swarm_powerbi_bot/services/__init__.py", line 1, in <module>
    from .chart_renderer import render_chart
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot/src/swarm_powerbi_bot/services/chart_renderer.py", line 15, in <module>
    import matplotlib
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 1010, in <module>
    rcParams._update_raw(_rc_params_in_file(matplotlib_fname()))
                                            ^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 636, in matplotlib_fname
    for fname in gen_candidates():
                 ^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 633, in gen_candidates
    yield os.path.join(get_configdir(), 'matplotlibrc')
                       ^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 340, in wrapper
    ret = func(**kwargs)
          ^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 579, in get_configdir
    return _get_config_or_cache_dir(_get_xdg_config_dir)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zerocold/Downloads/git/kpi/tg_bot/.venv/lib/python3.12/site-packages/matplotlib/__init__.py", line 547, in _get_config_or_cache_dir
    raise OSError(
OSError: Matplotlib requires access to a writable cache directory, but there was an issue with the default path (/Users/zerocold/.matplotlib), and a temporary directory could not be created; set the MPLCONFIGDIR environment variable to a writable directory

exec
/bin/zsh -lc "nl -ba src/swarm_powerbi_bot/agents/planner.py | sed -n '308,345p'" in /Users/zerocold/Downloads/git/kpi/tg_bot/swarm_powerbi_bot
 succeeded in 0ms:
   308	                AggregateQuery(
   309	                    aggregate_id=agg_id,
   310	                    params=AggregateParams(raw_params),
   311	                    label=q.get("label", ""),
   312	                )
   313	            )
   314	
   315	        if not queries:
   316	            return None
   317	
   318	        topic = raw_dict.get("topic", "statistics")
   319	        # intent was already extracted above for query limit calculation
   320	
   321	        # Разрешаем period_hint → конкретные даты для ВСЕХ интентов
   322	        for q_obj in queries:
   323	            period_hint = q_obj.params.get("period_hint", "")
   324	            if period_hint and "date_from" not in q_obj.params:
   325	                resolved_from, resolved_to = _resolve_period(period_hint)
   326	                q_obj.params["date_from"] = resolved_from
   327	                q_obj.params["date_to"] = resolved_to
   328	
   329	        # T034: для intent="comparison" убеждаемся что есть ровно 2 запроса
   330	        if intent == "comparison":
   331	            if len(queries) < 2:
   332	                logger.warning(
   333	                    "plan_aggregates: comparison intent but only %d queries — falling back",
   334	                    len(queries),
   335	                )
   336	                return None
   337	
   338	        return MultiPlan(
   339	            objective=question.text,
   340	            intent=intent,
   341	            queries=queries,
   342	            topic=topic,
   343	            render_needed=render_needed,
   344	            notes=["planner_v2:llm"],
   345	        )

codex
FAIL
[HIGH] src/swarm_powerbi_bot/agents/planner.py:404 — The new fallback comparison plan is still tagged `planner_v2:keyword`; `SwarmOrchestrator` skips `run_multi()` for any keyword `MultiPlan`, so when the LLM is unavailable these two generated queries are never executed and the request silently degrades to a single legacy SQL call instead of a comparison.
[HIGH] src/swarm_powerbi_bot/agents/planner.py:367 — Comparison fallback blindly reuses `question.last_topic` as the aggregate id and ignores the current question’s explicit topic. After an `outflow` answer, `сравни выручку за март и февраль` will still compare the previous topic, not revenue; if `last_topic` came from the legacy path (`outflow`, `services`, etc.), it is not even a catalog aggregate id.
[HIGH] src/swarm_powerbi_bot/agents/planner.py:370 — Every fallback comparison is hard-coded to “previous full month vs current month-to-date”. On 2026-04-15, `сравни за март и февраль` becomes `2026-03-01..2026-03-31` vs `2026-04-01..2026-04-15`, and edge cases from the spec such as `сравни по салонам` or `сравни за три месяца` are forced into the wrong query shape.
[HIGH] src/swarm_powerbi_bot/agents/planner.py:375 — The fallback client-comparison queries never copy `question.object_id` into `params`, even though catalog client aggregates require `object_id`; if this path is executed through the aggregate runner, registry validation rejects the follow-up instead of answering it.
[MEDIUM] src/swarm_powerbi_bot/agents/planner.py:318 — `_llm_plan_multi()` persists the LLM’s free-form `topic` verbatim, but the new follow-up mechanism assumes `last_topic` is a concrete aggregate id such as `clients_outflow`. If the model returns the schema example `statistics`, the next turn sends `last_topic=statistics`, which is too coarse to recover the correct aggregate and makes the new context handoff nondeterministic.
tokens used
93,692
FAIL
[HIGH] src/swarm_powerbi_bot/agents/planner.py:404 — The new fallback comparison plan is still tagged `planner_v2:keyword`; `SwarmOrchestrator` skips `run_multi()` for any keyword `MultiPlan`, so when the LLM is unavailable these two generated queries are never executed and the request silently degrades to a single legacy SQL call instead of a comparison.
[HIGH] src/swarm_powerbi_bot/agents/planner.py:367 — Comparison fallback blindly reuses `question.last_topic` as the aggregate id and ignores the current question’s explicit topic. After an `outflow` answer, `сравни выручку за март и февраль` will still compare the previous topic, not revenue; if `last_topic` came from the legacy path (`outflow`, `services`, etc.), it is not even a catalog aggregate id.
[HIGH] src/swarm_powerbi_bot/agents/planner.py:370 — Every fallback comparison is hard-coded to “previous full month vs current month-to-date”. On 2026-04-15, `сравни за март и февраль` becomes `2026-03-01..2026-03-31` vs `2026-04-01..2026-04-15`, and edge cases from the spec such as `сравни по салонам` or `сравни за три месяца` are forced into the wrong query shape.
[HIGH] src/swarm_powerbi_bot/agents/planner.py:375 — The fallback client-comparison queries never copy `question.object_id` into `params`, even though catalog client aggregates require `object_id`; if this path is executed through the aggregate runner, registry validation rejects the follow-up instead of answering it.
[MEDIUM] src/swarm_powerbi_bot/agents/planner.py:318 — `_llm_plan_multi()` persists the LLM’s free-form `topic` verbatim, but the new follow-up mechanism assumes `last_topic` is a concrete aggregate id such as `clients_outflow`. If the model returns the schema example `statistics`, the next turn sends `last_topic=statistics`, which is too coarse to recover the correct aggregate and makes the new context handoff nondeterministic.
```

