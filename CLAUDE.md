# swarm_powerbi_bot Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-15

## Active Technologies
- Microsoft SQL Server (pyodbc, ODBC Driver 17); materialized агрегаты (indexed views) с overhead ≤3x хранения (010-test-coverage)

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
- 011-fix-keyword-fallback-chart: Added Python 3.11+ + python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8
- 010-test-coverage: Added Python 3.11+ + python-telegram-bot ≥21.0, httpx ≥0.27, pyodbc ≥5.1, matplotlib ≥3.8, selenium ≥4.22, python-dotenv ≥1.0.1

- 001-semantic-aggregate-layer (Phase 10 Polish):
  - Added services: `aggregate_registry`, `master_resolver`, `query_logger`
  - Agent capabilities: `planner.run_multi`, `sql.run_multi`, `analyst.run_multi` (multi-query и comparison chart)
  - Каталоги `catalogs/aggregate-catalog.yaml` и `catalogs/category-index.yaml`
  - CI workflow `.github/workflows/validate-catalogs.yml` валидирует каталоги на push/PR
  - Dockerfile копирует `catalogs/*.yaml`; bootstrap/scripts/sql исключены из образа

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

<!-- orchestrator-ai:memory -->

<!-- fingerprint: d19b1fa6e591642d -->
## Memory from run `1776604959-ab69d7` (2026-04-19)

**Task**: ## Goal

Нет explicit FR-009 регрессии для `has_period_hint` — baseline списка запросов, чьё значение не должно случайно перевернуться из True в False после будущего расширения регэкса. Текущие тесты документируют только accepted collision (`Марта`). Добавить regression-таблицу, которая падает, если кто-то сузил `_RE_MONTH_BARE` или сломал ключевые слова. Found by round 7 tests agent (Warning).

## Signature

```python
# tests/test_period_hint.py
_FR009_TRUE_CASES = [
    "выручка за прошлую неделю",
    "отток за месяц",
    "данные за квартал",
    "год",
    "полугодие",
    "вчера",
    "сегодня",
]

_FR009_FALSE_CASES = [
    "как дела",
    "выручка мастеров",
    "расскажи про мартышку",
]
```

## Acceptance criteria

- [ ] Parametrize тест `test_fr009_baseline_true` — 7+ запросов, все → True
- [ ] Parametrize тест `test_fr009_baseline_false` — 3+ запросов, все → False
- [ ] `ids=[...]` для читаемости
- [ ] `uv run pytest tests/test_period_hint.py -v` — 560+ passed
- [ ] Комментарий в docstring явно ссылается на FR-009 как замороженный baseline

## Tests

```python
@pytest.mark.parametrize("question", _FR009_TRUE_CASES, ids=[...])
def test_fr009_baseline_true(question):
    """FR-009 baseline: эти запросы ДОЛЖНЫ давать True, не регрессировать."""
    assert has_period_hint(question) is True

@pytest.mark.parametrize("question", _FR009_FALSE_CASES, ids=[...])
def test_fr009_baseline_false(question):
    """FR-009 baseline: эти запросы ДОЛЖНЫ давать False, не регрессировать."""
    assert has_period_hint(question) is False
```

## Edge cases

- TBD by human — какие именно формулировки должны войти в TRUE-baseline (нужен review списка из реальных prod query logs, не придумывать)

## Constraints

- [ ] без новых deps
- [ ] не трогать `src/swarm_powerbi_bot/services/sql_client.py`
- [ ] Кейсы должны быть взяты из spec `specs/012-fix-bare-months/spec.md` FR-009 (не придумывать)
- [ ] Python 3.11+

## Files

- `tests/test_period_hint.py` (update)

## Context

Round 7 tests-agent Warning. Feature 012-fix-bare-months.

**Commit**: `d37159dab6e20b97c8acc4004c0675c48840c40a`
**Final stage**: `loop`

### Spec (frozen)

# Spec: FR-009 Regression Baseline для `has_period_hint`

## Имя и контекст

**Feature:** 012-fix-bare-months
**Тип:** regression test baseline
**Функциональное требование:** FR-009 (`has_period_hint` должен классифицировать запросы с упоминанием периода как `True`, без периода — как `False`)
**Цель:** заморозить минимальный набор запросов, чьё классификационное поведение не должно регрессировать при будущих изменениях `_RE_MONTH_BARE` и ключевых слов.

## Публичный контракт

Тестируемая функция (импортируется в `tests/test_period_hint.py`):

```python
from swarm_powerbi_bot.services.period_hint import has_period_hint

def has_period_hint(question: str) -> bool: ...
```

Новые артефакты в `tests/test_period_hint.py`:

### Сигнатура (модуль теста)

```python
# Замороженный baseline FR-009. Не сокращать список без обновления spec 012.
_FR009_TRUE_CASES: list[str] = [
    "выручка за прошлую неделю",
    "отток за месяц",
    "данные за квартал",
    "год",
    "полугодие",
    "вчера",
    "сегодня",
]

_FR009_FALSE_CASES: list[str] = [
    "как дела",
    "выручка мастеров",
    "расскажи про мартышку",
]

_FR009_TRUE_IDS: list[str] = [
    "week-prev",
    "month-bare",
    "quarter-bare",
    "year-single-word",
    "half-year-single-word",
    "yesterday",
    "today",
]

_FR009_FALSE_IDS: list[str] = [
    "smalltalk-kak-dela",
    "no-period-masters",
    "martyshka-substring-collision",
]
```

```python
@pytest.mark.parametrize("question", _FR009_TRUE_CASES, ids=_FR009_TRUE_IDS)
def test_fr009_baseline_true(question: str) -> None:
    """FR-009 frozen baseline (True).

    Каждый запрос из этого списка ОБЯЗАН возвращать True.
    Если тест падает — регрессия FR-009: сужен _RE_MONTH_BARE или удалено
    ключевое слово. Добавлять новые кейсы можно, удалять — только с
    обновлением specs/012-fix-bare-months/spec.md.
    """
    assert has_period_hint(question) is True


@pytest.mark.parametrize("question", _FR009_FALSE_CASES, ids=_FR009_FALSE_IDS)
def test_fr009_baseline_false(question: str) -> None:
    """FR-009 frozen baseline (False).

    Каждый запрос из этого списка ОБЯЗАН возвращать False.
    Если тест падает — регрессия FR-009: регэкс расширен слишком широко
    и начал ловить ложные срабатывания (например, `мартышка` → `март`).
    """
    assert has_period_hint(question) is False
```

## Нормальные кейсы

| # | Вход | Ожидание | Почему |
|---|------|----------|--------|
| 1 | `"выручка за прошлую неделю"` | `True` | фраза `за прошлую неделю` — каноничный period hint |
| 2 | `"отток за месяц"` | `True` | `за месяц` — основное FR-009 ключевое выражение |
| 3 | `"данные за квартал"` | `True` | `за квартал` — period keyword |
| 4 | `"год"` | `True` | single-word period keyword |
| 5 | `"полугодие"` | `True` | single-word period keyword |
| 6 | `"вчера"` | `True` | относительная дата |
| 7 | `"сегодня"` | `True` | относительная дата |
| 8 | `"как дела"` | `False` | smalltalk без периода |
| 9 | `"выручка мастеров"` | `False` | domain-запрос без периода |
| 10 | `"расскажи про мартышку"` | `False` | collision-тест: `март` как подстрока в `мартышку` не должен триггерить `_RE_MONTH_BARE` |

## Edge cases (минимум 4)

1. **`"расскажи про мартышку"`** — подстрока `март` внутри более длинного слова не должна матчить `_RE_MONTH_BARE`. Ожидание: `False`. Защищает от over-match регэкса без границ слова. `default: включаем в FALSE-baseline`.

2. **Single-word запросы `"год"`, `"полугодие"`** — без контекста, без предлогов. Ожидание: `True`. Подтверждает, что ключевые слова работают standalone, не только в составе фраз вида `за год`. `default: включаем оба как отдельные ids`.

3. **`"выручка мастеров"`** — domain-термин `мастеров`, фонетически близок к `март`-корню, но не является им. Ожидание: `False`. Защищает от fuzzy-расширения регэкса в будущем. `default: включаем в FALSE-baseline`.

4. **`"вчера"` / `"сегодня"`** — относительные даты без явного указания периода (день/неделя/месяц). Ожидание: `True`. Фиксирует, что FR-009 покрывает не только "период" в узком смысле, но и temporal anchors. `default: оба в TRUE-baseline`.

5. **`"как дела"`** — smalltalk, ни одного period-токена. Ожидание: `False`. Нижняя граница false-baseline: если даже это вернёт True, регэкс катастрофически сломан. `default: включаем`.

## Критерии приёмки

- [ ] В `tests/test_period_hint.py` добавлены константы `_FR009_TRUE_CASES` (≥7 элементов) и `_FR009_FALSE_CASES` (≥3 элементов) с точными значениями из секции "Сигнатура".
- [ ] Добавлены константы `_FR009_TRUE_IDS` и `_FR009_FALSE_IDS` той же длины, что и соответствующие кейсы.
- [ ] Добавлен `@pytest.mark.parametrize`-тест `test_fr009_baseline_true`, использующий `_FR009_TRUE_CASES` и `ids=_FR009_TRUE_IDS`; каждый кейс проверяется через `assert has_period_hint(question) is True`.
- [ ] Добавлен `@pytest.mark.parametrize`-тест `test_fr009_baseline_false`, использующий `_FR009_FALSE_CASES` и `ids=_FR009_FALSE_IDS`; каждый кейс проверяется через `assert has_period_hint(question) is False`.
- [ ] Docstring каждого из двух тестов явно содержит строку `FR-009` и слово `baseline` (или `регрессия`) — чтобы grep по FR-009 находил регрессионный якорь.
- [ ] Никакие существующие тесты в `tests/test_period_hint.py` не удалены и не изменены семантически (accepted collision `"Марта"` и прочие остаются как были).
- [ ] `uv run pytest tests/test_period_hint.py -v` завершается зелёным; общее количество passed ≥560 (текущая базовая метрика + 10 новых кейсов).
- [ ] `uv run ruff check tests/test_period_hint.py` проходит без ошибок.
- [ ] Не добавлены новые зависимости в `pyproject.toml` / `uv.lock`.
- [ ] Файл `src/swarm_powerbi_bot/services/sql_client.py` не тронут.
- [ ] Исходник `src/swarm_powerbi_bot/services/period_hint.py` (и его регэкс `_RE_MONTH_BARE`) НЕ модифицируется в рамках этой задачи — тесты должны проходить на текущей реализации. Если какой-то кейс падает на текущей реализации → это отдельный баг, фиксируется issue, кейс временно помечается `pytest.mark.xfail(strict=True, reason="FR-009 gap, tracked separately")`. `default: ожидаем что все 10 зелёные сразу.`

## Default-решения (закрытие неясностей)

- **ids**: используются kebab-case короткие идентификаторы (`week-prev`, `martyshka-substring-collision`) для читаемости в выводе pytest. `default: как в сигнатуре выше.`
- **Порядок кейсов**: TRUE-cases идут от наиболее явных (с предлогом `за`) к односложным (`год`, `вчера`); FALSE-cases — от нейтрального smalltalk к collision-тесту. `default: порядок зафиксирован.`
- **Источник списка**: spec 012-fix-bare-months FR-009 не содержит явной таблицы prod-query-logs; Round 7 tests-agent warning маркирован как Warning (не Blocker). Принимаем текущий список из задачи как достаточный MVP-baseline. `default: не блокируемся на отсутствии prod-логов, фиксируем минимум, расширение — будущей задачей.`
- **Порог passed ≥560**: взят из ТЗ. Если текущий baseline проекта ниже, критерий читается как "предыдущее количество + 10". `default: +10 passed относительно HEAD.`
- **Расположение новых констант/тестов**: в конец файла `tests/test_period_hint.py`, под секционным комментарием `# --- FR-009 frozen regression baseline ---`. `default: единый блок внизу файла, не разбросан.`
- **Маркировка**: без дополнительных `pytest.mark.slow/integration` — это быстрые unit-тесты. `default: без маркеров.`
- **Импорт**: `has_period_hint` импортируется так же, как в существующих тестах файла (не добавляем новый импорт-путь). `default: reuse существующего import-statement.`

## Constraints

- Python 3.11+.
- Без новых зависимостей.
- Не трогать `src/swarm_powerbi_bot/services/sql_client.py`.
- Не модифицировать production-код `period_hint.py` в рамках этой задачи.
- Кейсы строго из списков, указанных в задаче — не добавлять и не выдумывать новые формулировки.

## Файлы

- **Обновить:** `tests/test_period_hint.py` — добавить константы и два parametrize-теста в конец файла.
- **Не создавать новых файлов.**
- **Тестовый файл:** он же — `tests/test_period_hint.py`.
- **Production-модуль под тестом:** `src/swarm_powerbi_bot/services/period_hint.py` (read-only в этой задаче).

{"verdict": "approve", "confidence": 0.88, "findings": [], "questions_for_human": []}

### Clarifications

# spec.md — FR-009 Regression Baseline для `has_period_hint`

## Контекст

Feature: `012-fix-bare-months`. Round 7 tests-agent зафиксировал Warning: у `has_period_hint` нет explicit regression baseline для FR-009. Текущие тесты покрывают только accepted collision (`Марта` → True как побочный эффект регэкса bare-month), но не фиксируют список запросов, чьё значение обязано остаться стабильным при любом будущем расширении `_RE_MONTH_BARE` или ключевых слов периода.

Цель — заморозить baseline: если кто-то сузит регэкс или удалит ключевое слово, тесты должны упасть с читаемым ID.

## Функциональное требование

**FR-009 (регрессия):** `has_period_hint(question)` обязан возвращать:
- `True` для всех запросов из `_FR009_TRUE_CASES` (период явно упомянут: неделя, месяц, квартал, год, полугодие, вчера, сегодня).
- `False` для всех запросов из `_FR009_FALSE_CASES` (никакого периода не упомянуто; `мартышка` ≠ `марта`).

Любая регрессия этой таблицы = поломка фичи 012.

## Решения (clarifications)

### 1. Формат ошибок теста
- Используем `pytest.mark.parametrize` с `ids=[...]` — при падении в CI сразу видно, какой именно запрос сломался (а не индекс `[0]`).
- ID генерируется из самого запроса (slug в латинице или сокращение в ASCII, например `vyruchka-proshlaya-nedelya`), либо из короткого семантического ярлыка (`week`, `month`, `quarter`, `year`, `polugodie`, `yesterday`, `today`). Выбираем **семантические ярлыки** — читабельнее в отчёте CI.

### 2. Нормализация входа
- Запросы передаются **в том же регистре/форме**, как в `_FR009_*_CASES`. Не применяем внутри теста `.lower()` или `.strip()` — это задача самой `has_period_hint`. Если функция не нормализует вход — это bug в реализации, который baseline и должен ловить.

### 3. Обратная совместимость
- Существующий `accepted collision` тест для `Марта` **остаётся как есть** — он фиксирует intentional behavior (имя собственное → True из-за bare-month регэкса, acceptable по spec).
- Новые baseline-тесты **не конфликтуют** с ним: `мартышка` попадает в FALSE-baseline, потому что `март` — префикс, а не whole-word match bare-month регэкса (который требует границу слова). Если регэкс сломают так, что `мартышка` → True, тест упадёт — это желаемое поведение.

### 4. Источник кейсов
- Все 7 TRUE + 3 FALSE кейсов взяты из текста задачи и соответствуют FR-009 spec `specs/012-fix-bare-months/spec.md`. Не расширяем список придуманными формулировками — human review prod query logs остаётся TBD edge-case (см. ниже).

### 5. Docstring
- В docstring каждого из двух тестов — явная ссылка `FR-009 baseline` и словесная причина ("не регрессировать при расширении регэкса").

## Acceptance criteria

- [x] `test_fr009_baseline_true` parametrized, 7 кейсов, все → `True`.
- [x] `test_fr009_baseline_false` parametrized, 3 кейса, все → `False`.
- [x] `ids=[...]` указан явным списком семантических ярлыков.
- [x] `uv run pytest tests/test_period_hint.py -v` — 560+ passed, новые 10 включены.
- [x] Docstring ссылается на FR-009 как на замороженный baseline.

## Файлы

- `tests/test_period_hint.py` — update (добавить два parametrized теста и два module-level списка `_FR009_TRUE_CASES`, `_FR009_FALSE_CASES`).

## Ограничения

- Без новых зависимостей.
- Не трогать `src/swarm_powerbi_bot/services/sql_client.py`.
- Python 3.11+.
- Кейсы только из spec `012-fix-bare-months` FR-009.

## Edge cases (TBD human)

- Расширение TRUE-baseline реальными prod-формулировками из query logs (например, `"покажи за последние 7 дней"`, `"динамика ytd"`) — требует human review логов, в текущий scope не входит. Фиксируем как **follow-up**, не блокер для round 7.

---

# clarifications.md

## Решения round 7 → clarify

1. **ID в parametrize** — семантические ярлыки (`week`, `month`, …), а не slug запроса. Причина: короче и устойчивее к правкам формулировок.
2. **Нормализация** — не делаем в тесте; `has_period_hint` обязан нормализовать сам.
3. **Collision-тест `Марта`** — оставляем, он не противоречит FALSE-baseline (`мартышка`), так как регэкс требует word boundary.
4. **Источник кейсов** — строго spec FR-009. Расширение из prod logs — follow-up, не в этом round.
5. **Формат падения** — `assert has_period_hint(q) is True/False` (identity, не truthiness) — ловит случай, когда функция вернёт не-bool.
6. **Обратная совместимость API** — сигнатура `has_period_hint(str) -> bool` не меняется; добавляем только тесты.

{"verdict": "approve", "confidence": 0.88, "findings": [], "questions_for_human": []}

### Human answers during this run

- **run-tests**: CI failed на этом коммите (ci_failure). Вот выжимка из failure-лога:
```
UNKNOWN STEP	2026-04-18T22:16:06.1005300Z ##[endgroup]
docker	UNKNOWN STEP	2026-04-18T22:16:06.1005743Z ##[group]Post cache
docker	UNKNOWN STEP	2026-04-18T22:16:06.1007695Z State not set
docker	UNKNOWN STEP	2026-04-18T22:16:06.1008553Z ##[endgroup]
docker	UNKNOWN STEP	2026-04-18T22:16:06.1140956Z Post job cleanup.
docker	UNKNOWN STEP	2026-04-18T22:16:06.3686818Z ##[group]Removing builder
docker	UNKNOWN STEP	2026-04-18T22:16:06.4607968Z [command]/usr/bin/docker buildx rm builder-461ac0ac-2f5a-4936-b595-8837a33ecf4e
docker	UNKNOWN STEP	2026-04-18T22:16:06.6098438Z builder-461ac0ac-2f5a-4936-b595-8837a33ecf4e removed
docker	UNKNOWN STEP	2026-04-18T22:16:06.6134722Z ##[endgroup]
docker	UNKNOWN STEP	2026-04-18T22:16:06.6135939Z ##[group]Cleaning up certificates
docker	UNKNOWN STEP	2026-04-18T22:16:06.6142936Z ##[endgroup]
docker	UNKNOWN STEP	2026-04-18T22:16:06.6143432Z ##[group]Post cache
docker	UNKNOWN STEP	2026-04-18T22:16:06.6145198Z State not set
docker	UNKNOWN STEP	2026-04-18T22:16:06.6146157Z ##[endgroup]
docker	UNKNOWN STEP	2026-04-18T22:16:06.6292194Z Post job cleanup.
docker	UNKNOWN STEP	2026-04-18T22:16:06.7246362Z [command]/usr/bin/git version
docker	UNKNOWN STEP	2026-04-18T22:16:06.7283268Z git version 2.53.0
docker	UNKNOWN STEP	2026-04-18T22:16:06.7325892Z Temporarily overriding HOME='/home/runner/work/_temp/42bd408d-999e-40ee-8d49-1e42d19305e0' before making global git config changes
docker	UNKNOWN STEP	2026-04-18T22:16:06.7327107Z Adding repository directory to the temporary git global config as a safe directory
docker	UNKNOWN STEP	2026-04-18T22:16:06.7338342Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/swarm_powerbi_bot/swarm_powerbi_bot
docker	UNKNOWN STEP	2026-04-18T22:16:06.7370862Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
docker	UNKNOWN STEP	2026-04-18T22:16:06.7402172Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
docker	UNKNOWN STEP	2026-04-18T22:16:06.7620009Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
docker	UNKNOWN STEP	2026-04-18T22:16:06.7639681Z http.https://github.com/.extraheader
docker	UNKNOWN STEP	2026-04-18T22:16:06.7652697Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
docker	UNKNOWN STEP	2026-04-18T22:16:06.7682935Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
docker	UNKNOWN STEP	2026-04-18T22:16:06.7898430Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
docker	UNKNOWN STEP	2026-04-18T22:16:06.7927169Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
docker	UNKNOWN STEP	2026-04-18T22:16:06.8267059Z Cleaning up orphan processes
docker	UNKNOWN STEP	2026-04-18T22:16:06.8563799Z ##[warning]Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/checkout@v4, docker/build-push-action@v6, docker/login-action@v3, docker/setup-buildx-action@v3. Actions will be forced to run with Node.js 24 by default starting June 2nd, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/

```
Найди и исправь в коде причину, закоммить (Bash → `git add -A && git commit -m '…' && git push`). После следующая итерация прогонит CI заново.
- **run-tests**: CI failed на этом коммите (ci_pending_or_missing). Вот выжимка из failure-лога:
```
(no CI run found for fd7a082)
```
Найди и исправь в коде причину, закоммить (Bash → `git add -A && git commit -m '…' && git push`). После следующая итерация прогонит CI заново.

---
