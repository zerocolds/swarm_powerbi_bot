from datetime import date, timedelta

import pytest

from swarm_powerbi_bot.services import sql_client
from swarm_powerbi_bot.services.sql_client import extract_date_params, has_period_hint

# T032: детерминированная «сегодняшняя» дата для всех тестов модуля.
# Замораживает sql_client.date на фиксированную точку, чтобы избежать флаков
# на границе полуночи и дрейфа hardcoded годов в параметризованных данных.
_FROZEN_TODAY = date(2026, 4, 17)


class _FixedDate(date):
    """Подмена `date.today()` на фиксированную дату для стабильности тестов."""

    @classmethod
    def today(cls) -> date:
        return _FROZEN_TODAY


@pytest.fixture(autouse=True)
def freeze_today(monkeypatch):
    """Замораживает `sql_client.date` на `_FROZEN_TODAY` для всех тестов модуля."""
    monkeypatch.setattr(sql_client, "date", _FixedDate)


def test_has_period_hint_with_week():
    assert has_period_hint("Покажи выручку за неделю") is True


def test_has_period_hint_with_month_name():
    assert has_period_hint("Отчёт за январь 2025") is True


def test_has_period_hint_with_range():
    assert has_period_hint("с 1 по 15 марта") is True


def test_has_period_hint_with_yesterday():
    assert has_period_hint("Что было вчера?") is True


def test_has_period_hint_with_today():
    assert has_period_hint("Покажи данные за сегодня") is True


def test_has_period_hint_with_quarter():
    assert has_period_hint("Статистика за квартал") is True


def test_has_period_hint_with_year():
    assert has_period_hint("Покажи за год") is True


def test_has_period_hint_with_half_year():
    assert has_period_hint("За полгода") is True


def test_has_period_hint_absent():
    assert has_period_hint("Покажи отток клиентов") is False


def test_has_period_hint_absent_generic():
    assert has_period_hint("Топ мастеров по загрузке") is False


def test_extract_yesterday():
    params = extract_date_params("что было вчера")
    yesterday = _FROZEN_TODAY - timedelta(days=1)
    assert params["DateFrom"] == yesterday
    assert params["DateTo"] == yesterday


def test_extract_today():
    params = extract_date_params("за сегодня")
    assert params["DateFrom"] == _FROZEN_TODAY
    assert params["DateTo"] == _FROZEN_TODAY


def test_extract_month_name():
    params = extract_date_params("отчёт за март 2025")
    assert params["DateFrom"] == date(2025, 3, 1)
    assert params["DateTo"] == date(2025, 3, 31)


def test_extract_range():
    params = extract_date_params("с 5 по 20 апреля 2025")
    assert params["DateFrom"] == date(2025, 4, 5)
    assert params["DateTo"] == date(2025, 4, 20)


def test_extract_week():
    params = extract_date_params("за неделю")
    assert params["DateFrom"] == _FROZEN_TODAY - timedelta(days=7)
    assert params["DateTo"] == _FROZEN_TODAY


def test_extract_half_year():
    params = extract_date_params("за полгода")
    assert params["DateFrom"] == _FROZEN_TODAY - timedelta(days=180)


def test_extract_default_30_days():
    params = extract_date_params("покажи всё")
    assert params["DateFrom"] == _FROZEN_TODAY - timedelta(days=30)
    assert params["DateTo"] == _FROZEN_TODAY


# ── US1: bare-month парсинг ──────────────────────────────────


@pytest.mark.parametrize(
    "question,year,month,last_day",
    [
        ("выручка январь 2026", 2026, 1, 31),
        ("услуги февраль 2025", 2025, 2, 28),
        ("итоги март 2026", 2026, 3, 31),
        ("отчёт апрель 2026", 2026, 4, 30),
        ("продажи май 2026", 2026, 5, 31),
        ("данные июнь 2026", 2026, 6, 30),
        ("трафик июль 2026", 2026, 7, 31),
        ("статистика август 2026", 2026, 8, 31),
        ("расходы сентябрь 2026", 2026, 9, 30),
        ("выручка октябрь 2026", 2026, 10, 31),
        ("клиенты ноябрь 2026", 2026, 11, 30),
        ("отчёт декабрь 2026", 2026, 12, 31),
    ],
)
def test_bare_month_nominative_all_12_months(question, year, month, last_day):
    """T005: именительный падеж для всех 12 месяцев → период первый..последний день."""
    params = extract_date_params(question)
    assert params["DateFrom"] == date(year, month, 1)
    assert params["DateTo"] == date(year, month, last_day)


@pytest.mark.parametrize(
    "question,year,month,last_day",
    [
        ("итоги марта 2026", 2026, 3, 31),
        ("отчёту февралю 2026", 2026, 2, 28),
        ("в апреле 2026", 2026, 4, 30),
        ("мартом 2026", 2026, 3, 31),
        ("августом 2025", 2025, 8, 31),
        ("в сентябре 2026", 2026, 9, 30),
        ("к октябрю 2026", 2026, 10, 31),
        ("январём 2024", 2024, 1, 31),
        # T027: май падежные формы — предложный/дательный/творительный
        ("в мае 2026", 2026, 5, 31),
        ("к маю 2026", 2026, 5, 31),
        ("маем 2026", 2026, 5, 31),
    ],
)
def test_bare_month_padezh_cases(question, year, month, last_day):
    """T006/T027: ≥8 падежных форм (родительный/дательный/предложный/творительный)."""
    params = extract_date_params(question)
    assert params["DateFrom"] == date(year, month, 1)
    assert params["DateTo"] == date(year, month, last_day)


@pytest.mark.parametrize(
    "question,year,last_day",
    [
        ("февраль 2024", 2024, 29),  # високосный
        ("февраль 2025", 2025, 28),
        ("февраль 2100", 2100, 28),  # делится на 100, но не на 400 → не високосный
        ("февраль 2000", 2000, 29),  # делится на 400 → високосный
    ],
)
def test_bare_month_leap_year(question, year, last_day):
    """T007: февраль 28/29 в зависимости от високосности года."""
    params = extract_date_params(question)
    assert params["DateFrom"] == date(year, 2, 1)
    assert params["DateTo"] == date(year, 2, last_day)


@pytest.mark.parametrize(
    "question,year,month,last_day",
    [
        ("отчёт за месяц март 2026", 2026, 3, 31),
        ("за неделю июня 2026", 2026, 6, 30),
        ("за год январь 2025", 2025, 1, 31),
        ("за квартал октября 2025", 2025, 10, 31),
    ],
)
def test_bare_month_priority_over_keyword(question, year, month, last_day):
    """T008: bare-month побеждает keyword-периоды (неделя/месяц/квартал/год)."""
    params = extract_date_params(question)
    assert params["DateFrom"] == date(year, month, 1)
    assert params["DateTo"] == date(year, month, last_day)


# ── US2: регрессия существующего поведения ──────────────────


@pytest.mark.parametrize(
    "question,year,month,last_day",
    [
        ("выручка за март 2025", 2025, 3, 31),
        ("за январь 2025", 2025, 1, 31),
        ("за декабрь 2024", 2024, 12, 31),
    ],
)
def test_regression_za_month(question, year, month, last_day):
    """T010: «за <месяц> [<год>]» не меняется после фикса (FR-004)."""
    params = extract_date_params(question)
    assert params["DateFrom"] == date(year, month, 1)
    assert params["DateTo"] == date(year, month, last_day)


@pytest.mark.parametrize(
    "question,year,month,day_from,day_to",
    [
        ("с 5 по 20 апреля 2025", 2025, 4, 5, 20),
        ("с 1 по 15 марта 2026", 2026, 3, 1, 15),
    ],
)
def test_regression_range(question, year, month, day_from, day_to):
    """T011a: диапазон «с X по Y <месяц> [<год>]» не меняется."""
    params = extract_date_params(question)
    assert params["DateFrom"] == date(year, month, day_from)
    assert params["DateTo"] == date(year, month, day_to)


def test_regression_absolute_anchors():
    """T011b: абсолютные якоря «вчера» и «сегодня» не меняются."""
    yesterday = _FROZEN_TODAY - timedelta(days=1)
    p_yd = extract_date_params("что было вчера")
    assert p_yd == {"DateFrom": yesterday, "DateTo": yesterday}
    p_td = extract_date_params("за сегодня")
    assert p_td == {"DateFrom": _FROZEN_TODAY, "DateTo": _FROZEN_TODAY}


@pytest.mark.parametrize(
    "question,days",
    [
        ("за неделю", 7),
        ("за месяц", 30),
        ("за квартал", 90),
        ("за полгода", 180),
        ("за год", 365),
    ],
)
def test_regression_keyword_periods(question, days):
    """T012: keyword-периоды — скользящие окна от сегодняшней даты (FR-004)."""
    params = extract_date_params(question)
    assert params["DateFrom"] == _FROZEN_TODAY - timedelta(days=days)
    assert params["DateTo"] == _FROZEN_TODAY


def test_za_month_beats_bare_month():
    """T013: «за <месяц1> <год> <месяц2>» → месяц1 (bare-month2 игнорируется). FR-005."""
    params = extract_date_params("за январь 2025 февраль")
    assert params["DateFrom"] == date(2025, 1, 1)
    assert params["DateTo"] == date(2025, 1, 31)


# ── US3: single-query fallback для сравнений ───────────────


@pytest.mark.parametrize(
    "question,year,month,last_day",
    [
        ("сравни март 2026 и апрель 2026", 2026, 3, 31),
        ("разница между январём 2025 и февралём 2026", 2025, 1, 31),
        ("май 2026 vs июнь 2026", 2026, 5, 31),
    ],
)
def test_compare_first_month_wins(question, year, month, last_day):
    """T015: если месяцев несколько — возвращается период первого. FR-006.

    Годы у каждого месяца указываются явно — согласно R-005 (single-search,
    year привязан к первому совпадению).
    """
    params = extract_date_params(question)
    assert params["DateFrom"] == date(year, month, 1)
    assert params["DateTo"] == date(year, month, last_day)


def test_compare_with_explicit_year_on_first():
    """T016: «сравни январь 2025 и февраль 2026» → январь 2025 (первый месяц со своим годом)."""
    params = extract_date_params("сравни январь 2025 и февраль 2026")
    assert params["DateFrom"] == date(2025, 1, 1)
    assert params["DateTo"] == date(2025, 1, 31)


# ── Polish: negative, ReDoS, caplog, default year ──────────


@pytest.mark.parametrize(
    "question",
    [
        "январский отчёт",
        "февральский бюджет",
        "мартышка на дереве",
        "апрельский дождь",
        "майонез с салатом",
        "июньский жук",
        "июльский полдень",
        "августовский путч",
        "сентябрьский урожай",
        "октябрятский сбор",
        "ноябрьский туман",
        "декабрьский снег",
        "мартини со льдом",
        "маяковский поэт",
        "подмайский пикник",
    ],
)
def test_bare_month_no_false_positives(question):
    """T018: ≥15 negative-кейсов — составные слова → default last-30-days (SC-003)."""
    params = extract_date_params(question)
    assert params["DateFrom"] == _FROZEN_TODAY - timedelta(days=30)
    assert params["DateTo"] == _FROZEN_TODAY
    assert has_period_hint(question) is False


def test_redos_guard():
    """T019: regex не страдает catastrophic backtracking на длинных строках (I-7)."""
    import time

    payload = "а" * 10_000
    t0 = time.perf_counter()
    extract_date_params(payload)
    dt_extract = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    has_period_hint(payload)
    dt_hint = (time.perf_counter() - t0) * 1000

    assert dt_extract < 10, f"extract_date_params took {dt_extract:.2f} ms (>10)"
    assert dt_hint < 10, f"has_period_hint took {dt_hint:.2f} ms (>10)"


@pytest.mark.parametrize(
    "question,strategy",
    [
        ("выручка март 2026", "bare_month"),
        ("выручка за март 2025", "za_month"),
        ("с 5 по 20 апреля 2025", "range"),
        ("что было вчера", "absolute"),
        ("за неделю", "keyword"),
        ("отток клиентов", "default"),
    ],
)
def test_period_extracted_log_strategy(caplog, question, strategy):
    """T021: в DEBUG-логе ровно одно сообщение period_extracted со стратегией (FR-011 / I-8)."""
    import logging

    caplog.set_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client")
    extract_date_params(question)
    matching = [r for r in caplog.records if r.getMessage() == "period_extracted"]
    assert len(matching) == 1, f"expected 1 period_extracted log, got {len(matching)}"
    assert matching[0].__dict__["strategy"] == strategy
    # полный текст question не логируется — только длина
    assert matching[0].__dict__["question_len"] == len(question)


def test_bare_month_without_year_uses_today_year():
    """T022: bare-month без явного года → текущий календарный год (FR-003).

    autouse-фикстура `freeze_today` замораживает `sql_client.date` на `_FROZEN_TODAY`;
    дополнительный monkeypatch не нужен.
    """
    params = extract_date_params("выручка март")
    assert params["DateFrom"] == date(_FROZEN_TODAY.year, 3, 1)
    assert params["DateTo"] == date(_FROZEN_TODAY.year, 3, 31)


@pytest.mark.parametrize(
    "question",
    [
        "с 30 по 31 февраля 2025",  # невалидный день в феврале
        "с 1 по 32 марта 2026",  # день > 31
        "январь 0000",  # год вне диапазона date()
        "выручка апрель 0000",  # bare-month с невалидным годом
    ],
)
def test_invariant_i1_edge_inputs(question):
    """T028: I-1 «никогда не бросает» — невалидные даты/годы возвращают валидный period (graceful fallback).

    Конкретная ветка fallback'а (last-30-days / bare-month bounds / current-month) —
    деталь реализации; инвариант I-1 требует только чтобы функция не падала
    и вернула корректный dict с date-объектами DateFrom ≤ DateTo.
    """
    params = extract_date_params(question)
    assert isinstance(params["DateFrom"], date)
    assert isinstance(params["DateTo"], date)
    assert params["DateFrom"] <= params["DateTo"]


@pytest.mark.parametrize(
    "question, expected_from, expected_to",
    [
        # Без явного года → current year (_FROZEN_TODAY.year = 2026).
        ("ВЫРУЧКА МАРТ", date(2026, 3, 1), date(2026, 3, 31)),
        # С явным годом — проверяем полную дату, чтобы uppercase не ломал \d{4} группу.
        ("Март 2026", date(2026, 3, 1), date(2026, 3, 31)),
        ("НОЯБРЁМ 2025", date(2025, 11, 1), date(2025, 11, 30)),
        ("за Январь 2024", date(2024, 1, 1), date(2024, 1, 31)),
        ("ВЫРУЧКА МАРТА 2026", date(2026, 3, 1), date(2026, 3, 31)),
    ],
    ids=[
        "mart_upper_noyear",
        "mart_titled",
        "noyabrem_upper",
        "za_yanvar",
        "marta_upper",
    ],
)
def test_i5_case_insensitive(question, expected_from, expected_to):
    """T036: I-5 — `.lower()` внутри extract_date_params. Регистр не должен влиять
    ни на month-extraction, ни на year-extraction."""
    params = extract_date_params(question)
    assert params["DateFrom"] == expected_from
    assert params["DateTo"] == expected_to


@pytest.mark.parametrize(
    "question",
    ["", "   ", "\n\t  "],
    ids=["empty", "spaces", "mixed_ws"],
)
def test_i1_empty_or_whitespace_input(question):
    """T037: I-1 — пустая строка / whitespace не должны бросать.

    Инвариант (а не деталь реализации): возвращается валидный dict с date-объектами
    и DateFrom ≤ DateTo. Конкретная fallback-ветка — деталь.
    """
    params = extract_date_params(question)
    assert isinstance(params["DateFrom"], date)
    assert isinstance(params["DateTo"], date)
    assert params["DateFrom"] <= params["DateTo"]


@pytest.mark.parametrize(
    "question",
    [
        "новый год",
        "новый год 2026",
    ],
    ids=["bare", "with_year"],
)
def test_novy_god_not_parsed_as_year(question):
    """T038: «новый год» — carveout в keyword-ветке, не должно интерпретироваться
    как период «год».

    Carveout — проверка подстроки `"новый год" not in text` в sql_client.
    Обе формы содержат подстроку «новый год» буквально → falls to default last-30-days.
    Падежные формы вроде «новым годом» не содержат подстроку «новый год», поэтому
    попадают в year-keyword branch (365 дней) — это известная узость carveout,
    не покрывается этим тестом.
    """
    params = extract_date_params(question)
    assert params["DateFrom"] == _FROZEN_TODAY - timedelta(days=30)
    assert params["DateTo"] == _FROZEN_TODAY


@pytest.mark.parametrize(
    "question, strategy",
    [
        ("выручка март 2026", "bare_month"),
        ("за апрель 2025", "za_month"),
        ("с 1 по 15 мая 2026", "range"),
        ("вчера", "absolute"),
        ("за неделю", "keyword"),
        ("как дела", "default"),
    ],
    ids=["bare_month", "za_month", "range", "absolute", "keyword", "default"],
)
def test_i3_i4_return_shape_all_strategies(question, strategy):
    """T039: I-3 (date, не datetime) + I-4 (ровно два ключа DateFrom/DateTo)
    для всех шести стратегий, не только bare_month.

    Проверка I-3: isinstance(..., date) AND NOT isinstance(..., datetime).
    Нельзя использовать `type(...) is date` из-за autouse fixture, который
    подменяет sql_client.date → _FixedDate (subclass of date) для фризинга.
    """
    from datetime import datetime

    params = extract_date_params(question)
    assert set(params.keys()) == {"DateFrom", "DateTo"}, f"I-4 violated for {strategy}"
    for key in ("DateFrom", "DateTo"):
        assert isinstance(params[key], date), f"I-3 violated: {key} for {strategy}"
        assert not isinstance(params[key], datetime), (
            f"I-3 violated: {key} is datetime for {strategy}"
        )
