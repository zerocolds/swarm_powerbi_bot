# Contract: `extract_date_params`

**Module**: `src/swarm_powerbi_bot/services/sql_client.py`
**Type**: Internal API (pure function)
**Change scope**: behavioural extension, signature unchanged.

## Signature

```python
def extract_date_params(question: str) -> dict[str, date]: ...
```

## Inputs

| Name | Type | Description |
|---|---|---|
| `question` | `str` | Русскоязычный пользовательский запрос. Может содержать месяц (с «за» или без), диапазон, ключевые слова периода. |

## Outputs

| Key | Type | Description |
|---|---|---|
| `"DateFrom"` | `datetime.date` | Начало периода (включительно). |
| `"DateTo"` | `datetime.date` | Конец периода (включительно). |

Всегда возвращает словарь с ровно двумя указанными ключами.

## Decision Order (after fix)

1. `_RE_MONTH` — «за <месяц> [<год>]» → весь месяц.
2. `_RE_RANGE` — «с X по Y <месяц> [<год>]» → указанные дни.
3. «вчера» → позавчерашний день как DateFrom=DateTo.
4. «сегодн» → сегодняшний день как DateFrom=DateTo.
5. **`_RE_MONTH_BARE` — bare-month → весь месяц** *(NEW)*
6. «недел» → last 7 days.
7. «месяц»/«меся» → last 30 days.
8. «квартал» → last 90 days.
9. «полугод»/«полгод» → last 180 days.
10. «год» (кроме «новый год») → last 365 days.
11. Default → last 30 days.

## Behavior Contract

### Positive cases (new behavior)

| Input | Expected DateFrom | Expected DateTo |
|---|---|---|
| `"выручка март"` (год=2026) | `2026-03-01` | `2026-03-31` |
| `"услуги февраль 2025"` | `2025-02-01` | `2025-02-28` |
| `"услуги февраль 2024"` | `2024-02-01` | `2024-02-29` |
| `"итоги марта"` (год=2026) | `2026-03-01` | `2026-03-31` |
| `"в августе 2025"` | `2025-08-01` | `2025-08-31` |
| `"январём 2024"` | `2024-01-01` | `2024-01-31` |
| `"сравни март и апрель"` (год=2026) | `2026-03-01` | `2026-03-31` (первый) |
| `"отчёт за месяц март"` (год=2026) | `2026-03-01` | `2026-03-31` |
| `"за неделю июня"` (год=2026) | `2026-06-01` | `2026-06-30` |

### Preserved cases (no regression)

| Input | Expected DateFrom | Expected DateTo |
|---|---|---|
| `"выручка за март"` (год=2026) | `2026-03-01` | `2026-03-31` |
| `"за январь 2025"` | `2025-01-01` | `2025-01-31` |
| `"с 5 по 20 апреля 2025"` | `2025-04-05` | `2025-04-20` |
| `"что было вчера"` | `today − 1 day` | `today − 1 day` |
| `"за сегодня"` | `today` | `today` |
| `"за неделю"` | `today − 7 days` | `today` |
| `"за квартал"` | `today − 90 days` | `today` |
| `"за полгода"` | `today − 180 days` | `today` |
| `"за год"` | `today − 365 days` | `today` |
| `"новый год"` | default (last 30 days) | default (last 30 days) |

### Negative cases (no false positives)

| Input | Expected |
|---|---|
| `"мартышка"` | default last-30-days |
| `"августовский"` | default last-30-days |
| `"майонез"` | default last-30-days |
| `"отток клиентов"` | default last-30-days |

## Invariants

- I-1. Функция не бросает исключений на любом Unicode-вводе.
- I-2. `DateFrom ≤ DateTo` всегда.
- I-3. Тип значений — `datetime.date` (не `datetime.datetime`, не `str`).
- I-4. Словарь содержит ровно два ключа: `"DateFrom"`, `"DateTo"`.
- I-5. Парсинг регистронечувствителен (`question.lower()` внутри).
- I-6. Для високосного года февраль возвращает 29 дней, для невисокосного — 28.
- I-7. **ReDoS-инвариант**: все regex-паттерны модуля (`_RE_MONTH`, `_RE_RANGE`, `_RE_MONTH_BARE`) удовлетворяют правилам:
  - плоские альтернации без вложенных квантификаторов `*`/`+`/`{m,n}`;
  - падежные окончания — только опциональная группа вида `(?:...|...)?` без повторений;
  - различимые стемы у альтернатив, никакого общего префикса с квантификатором.
  Верифицируется страж-тестом: `extract_date_params("а"*10_000)` и `has_period_hint("а"*10_000)` возвращаются за <10 мс, без `RecursionError`.
- I-8. **Структурированный лог**: ровно одно DEBUG-сообщение `period_extracted` на вызов, с полем `strategy ∈ {bare_month, za_month, range, absolute, keyword, default}`. Полный текст `question` в лог не попадает (только `len`).

## Related

- `has_period_hint(question: str) -> bool` — использует те же regex'ы; контракт не меняется, но покрытие тестами расширяется.
