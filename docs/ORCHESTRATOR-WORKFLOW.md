# Daemon resume / status workflow

Короткая памятка о том, как orchestrator-ai daemon работает с карточками MAQA
на этом репо, и что делать, если он зациклился.

## Правильный запуск daemon'а

```bash
orchestrator-ai daemon \
  --source github \
  --repo zerocolds/swarm_powerbi_bot \
  --repo-path /path/to/swarm_powerbi_bot \
  --poll-interval 30
```

`--source github` обязателен: он заставляет daemon читать `GithubIssuesBacklogSource`
(lebels `maqa:backlog` / `maqa:in-progress` / `maqa:blocked` / `maqa:done`)
а не GitHub Projects v2 board (который в текущем main не интегрирован
как source, только как checkbox-sync).

Если запустить с `--source projects` (устаревший или кастомный source), daemon
уйдёт в цикл `picked up → blocked → dropped as stale`: он сверяет с Projects,
а метки мы выставляем на Issues.

## Правила переходов (см. `src/orchestrator_ai/backlog.py`)

| Событие          | Метки после                           |
|------------------|---------------------------------------|
| `next()`         | `-maqa:backlog` `+maqa:in-progress`   |
| `blocked()`      | `+maqa:blocked` (in-progress остаётся)|
| `complete()`     | `-maqa:in-progress` `+maqa:done` + close |
| `release()`      | `+maqa:backlog` `-maqa:in-progress -maqa:blocked` |

## Ответ на эскалацию

Daemon слушает комментарии с префиксом `@orchestrator answer:` (см.
`src/orchestrator_ai/daemon.py::_extract_answer`).

Формат одного комментария:

```
@orchestrator answer:

<свободный текст с решением, может быть многострочным, может содержать
code blocks, markdown, что угодно — всё, что идёт после двоеточия, попадает
в промпт worker'а как `answer` параметр>
```

**Важно:** комментарий от ревьюера БЕЗ этого префикса daemon игнорирует.

## Ручной resume

Если daemon отвалился или нужен контроль:

```bash
orchestrator-ai resume runs/<run_id>/state.json \
  --answer-file /tmp/answer.md \
  --repo-path /path/to/swarm_powerbi_bot \
  --complete   # опционально: закрыть issue + поставить maqa:done
```

## Частые блокеры

### `install-deps` / `deps install failed`

`pyodbc` требует системные headers. В worktree-venv проверь:

```bash
dpkg -l | grep -E 'unixodbc-dev|msodbcsql17'
```

Если отсутствует — поставь на хост/образ, либо переключи `install-deps`
runner на `uv sync --frozen` вместо `pip install -e .`.

### `ci_gate_blocked` без видимых причин

Проверь, что ветка `maqa/run-<id>` запушена в `origin`:

```bash
git ls-remote origin "maqa/run-<id>"
```

Если пустой вывод — `GitCommitRunner` коммитит, но не пушит. Руками:

```bash
git -C .maqa/worktrees/<id> push -u origin maqa/run-<id>
```

Или снять `run-tests` из `MaqaConfig.ci_gate_stages` для этого репо.

### `Agent did not return JSON verdict`

Runtime glitch ревьюера (таймаут, 429, non-JSON output). Resume с
`--answer "retry reviewer"` или увеличь `AgentConfig.timeout_seconds`.
