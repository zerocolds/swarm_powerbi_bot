# Quickstart — Парсинг bare-months

**Feature**: 012-fix-bare-months
**Spec**: [spec.md](./spec.md)

Быстрый гайд по ручной верификации фикса после реализации.

## Prerequisites

- `uv` установлен (см. конституцию IX).
- Виртуальное окружение развёрнуто: `uv sync`.

## 1. Запустить автотесты

```bash
uv run pytest tests/test_period_detection.py tests/test_period_hint.py -v
```

Ожидание: все тесты (существующие + новые bare-month) ПРОХОДЯТ.

## 2. Запустить все тесты (регрессия)

```bash
uv run pytest -q
```

Ожидание: нет регрессий в `test_comparison.py`, `test_keyword_fallback.py`, `test_multi_query.py`, `test_orchestrator.py`, `test_planner*.py`.

## 3. Линтинг

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Ожидание: 0 замечаний.

## 4. Ручная проверка в Python REPL

```bash
uv run python -c "
from swarm_powerbi_bot.services.sql_client import extract_date_params, has_period_hint

checks = [
    'выручка март',
    'услуги февраль 2025',
    'итоги марта',
    'в августе',
    'сравни март и апрель',
    'отчёт за месяц март',
    'за неделю июня',
    # regressions
    'выручка за март',
    'за январь 2025',
    'с 5 по 20 апреля 2025',
    'что было вчера',
    'за неделю',
    # negative
    'мартышка',
    'августовский',
    'отток клиентов',
]
for q in checks:
    print(f'{q!r:40} hint={has_period_hint(q)!s:5} params={extract_date_params(q)}')
"
```

**Ожидание** (на 2026-04-17):
- `'выручка март'` → `2026-03-01..2026-03-31`, `hint=True`.
- `'услуги февраль 2025'` → `2025-02-01..2025-02-28`, `hint=True`.
- `'итоги марта'` → `2026-03-01..2026-03-31`, `hint=True`.
- `'в августе'` → `2026-08-01..2026-08-31`, `hint=True`.
- `'сравни март и апрель'` → `2026-03-01..2026-03-31` (первый — март), `hint=True`.
- `'отчёт за месяц март'` → `2026-03-01..2026-03-31`, `hint=True`.
- `'за неделю июня'` → `2026-06-01..2026-06-30`, `hint=True`.
- `'выручка за март'` → `2026-03-01..2026-03-31`, `hint=True` *(регрессия)*.
- `'за январь 2025'` → `2025-01-01..2025-01-31`, `hint=True` *(регрессия)*.
- `'с 5 по 20 апреля 2025'` → `2025-04-05..2025-04-20`, `hint=True` *(регрессия)*.
- `'что было вчера'` → `today−1..today−1`, `hint=True` *(регрессия)*.
- `'за неделю'` → `today−7..today`, `hint=True` *(регрессия)*.
- `'мартышка'` → `today−30..today`, `hint=False` *(без ложных срабатываний)*.
- `'августовский'` → `today−30..today`, `hint=False` *(без ложных срабатываний)*.
- `'отток клиентов'` → `today−30..today`, `hint=False` *(регрессия)*.

## 4.1. Проверка ReDoS-стража

```bash
uv run python -c "
import time
from swarm_powerbi_bot.services.sql_client import extract_date_params, has_period_hint
t = time.perf_counter()
extract_date_params('а' * 10000)
has_period_hint('а' * 10000)
dt = (time.perf_counter() - t) * 1000
print(f'elapsed={dt:.2f} ms (expected <10 ms per call)')
"
```

Ожидание: общий elapsed <20 мс (по <10 мс на каждый вызов).

## 4.2. Проверка structured logging (SC-006)

```bash
uv run python -c "
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s %(extra)s' if False else '%(levelname)s %(name)s %(message)s')
from swarm_powerbi_bot.services.sql_client import extract_date_params
extract_date_params('выручка март 2026')   # ожидаем strategy=bare_month
extract_date_params('выручка за март 2025') # ожидаем strategy=za_month
extract_date_params('за неделю')            # ожидаем strategy=keyword
extract_date_params('отток клиентов')       # ожидаем strategy=default
"
```

В логе должны появиться 4 записи уровня DEBUG с сообщением `period_extracted` и соответствующим `strategy` в `extra`.

## 5. E2E-проверка через Telegram (опционально)

Если `.env` настроен и подключение к MSSQL доступно:

```bash
uv run python -m swarm_powerbi_bot
```

Отправить боту: «выручка март». Проверить в логах (`query_logger`), что параметры `@DateFrom=2026-03-01`, `@DateTo=2026-03-31` корректно прокинулись в хранимую процедуру.

## 6. Готовность к мержу

- [ ] `pytest -q` — pass
- [ ] `ruff check && ruff format --check` — clean
- [ ] `speckit.review.run` — PASS
- [ ] `speckit.staff-review.run` — PASS
- [ ] `speckit.verify.run` — PASS
- [ ] `speckit.verify-tasks.run` — PASS
- [ ] `/speckit.adversarial-review` (DeepSeek ∥ Codex) — PASS
- [ ] Issue [#17](https://github.com/k-p-i-bi/swarm_powerbi_bot/issues/17) — закрывается PR'ом
