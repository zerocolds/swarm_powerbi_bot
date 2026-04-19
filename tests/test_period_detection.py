import logging
import sys
from datetime import date, timedelta

import pytest

from swarm_powerbi_bot.services.sql_client import extract_date_params, has_period_hint

_FROZEN_TODAY = date(2026, 4, 17)


class _FixedDateClass(date):
    @classmethod
    def today(cls):
        return _FROZEN_TODAY


@pytest.fixture(autouse=True)
def _FixedDate(monkeypatch):
    import swarm_powerbi_bot.services.sql_client as _sql_mod

    monkeypatch.setattr(_sql_mod, "date", _FixedDateClass)
    monkeypatch.setattr(sys.modules[__name__], "date", _FixedDateClass)


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
    yesterday = date.today() - timedelta(days=1)
    assert params["DateFrom"] == yesterday
    assert params["DateTo"] == yesterday


def test_extract_today():
    params = extract_date_params("за сегодня")
    today = date.today()
    assert params["DateFrom"] == today
    assert params["DateTo"] == today


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
    today = date.today()
    assert params["DateFrom"] == today - timedelta(days=7)
    assert params["DateTo"] == today


def test_extract_half_year():
    params = extract_date_params("за полгода")
    today = date.today()
    assert params["DateFrom"] == today - timedelta(days=180)


def test_extract_default_30_days():
    params = extract_date_params("покажи всё")
    today = date.today()
    assert params["DateFrom"] == today - timedelta(days=30)
    assert params["DateTo"] == today


@pytest.mark.parametrize(
    "query, exp_year, exp_month, exp_day_from, exp_day_to",
    [
        ("с 1 по 15 марта", 2026, 3, 1, 15),
        ("с 1 по 15 мая", 2026, 5, 1, 15),
        ("с 10 по 20 декабря", 2026, 12, 10, 20),
    ],
    ids=["march_no_year", "may_no_year", "december_no_year"],
)
def test_regression_range(query, exp_year, exp_month, exp_day_from, exp_day_to):
    params = extract_date_params(query)
    assert params["DateFrom"] == date(exp_year, exp_month, exp_day_from)
    assert params["DateTo"] == date(exp_year, exp_month, exp_day_to)


def test_period_extracted_log_strategy(caplog):
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        extract_date_params("выручка март")
    matching = [r for r in caplog.records if r.message == "period_extracted"]
    assert matching, "period_extracted лог должен быть emitted"
    strategy = getattr(matching[0], "strategy", None)
    assert strategy is not None, "period_extracted record should carry strategy= extra"
    assert strategy == "bare_month"


def test_extract_bare_month():
    params = extract_date_params("выручка март")
    today = date.today()
    assert params["DateFrom"] == date(today.year, 3, 1)
    assert params["DateTo"] == date(today.year, 3, 31)


def test_redos_guard():
    import time

    long_input = "март " * 10000
    start = time.perf_counter()
    has_period_hint(long_input)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 50.0, f"ReDoS suspected: {elapsed_ms:.1f}ms"


def test_redos_guard_alternating():
    """Alternated trigger words — still orders-of-magnitude fast."""
    import time

    long_input = "март апрель " * 5000
    start = time.perf_counter()
    has_period_hint(long_input)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 50.0, f"ReDoS suspected on alternating input: {elapsed_ms:.1f}ms"


def test_redos_guard_pure_noise():
    """Pure noise with no period triggers — must not cause backtracking."""
    import time

    long_input = "x" * 10000
    start = time.perf_counter()
    has_period_hint(long_input)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 50.0, f"ReDoS suspected on noise input: {elapsed_ms:.1f}ms"


def test_match_month_all_may_cases():
    from swarm_powerbi_bot.services.sql_client import _match_month

    assert _match_month("май") == 5
    assert _match_month("мая") == 5
    assert _match_month("маю") == 5
    assert _match_month("мае") == 5
    assert _match_month("маем") == 5


def test_match_month_march_no_collision():
    from swarm_powerbi_bot.services.sql_client import _match_month

    assert _match_month("март") == 3
    assert _match_month("марта") == 3
    assert _match_month("мартом") == 3
    assert _match_month("марте") == 3


def test_match_month_empty_string():
    from swarm_powerbi_bot.services.sql_client import _match_month

    assert _match_month("") == 0


def test_match_month_bare_ma_prefix_no_greedy_collision():
    """«ма» как префикс не должен фолбэчить в май через жадный startswith."""
    from swarm_powerbi_bot.services.sql_client import _match_month

    assert _match_month("ма") == 0
    assert _match_month("мам") == 0
    assert _match_month("мас") == 0


def test_match_month_order_independent(monkeypatch):
    """Результат не должен зависеть от порядка вставки в _MONTH_MAP."""
    import random

    import swarm_powerbi_bot.services.sql_client as _sql_mod

    items = list(_sql_mod._MONTH_MAP.items())
    rng = random.Random(42)
    rng.shuffle(items)
    shuffled = dict(items)

    monkeypatch.setattr(_sql_mod, "_MONTH_MAP", shuffled)
    monkeypatch.setattr(
        _sql_mod,
        "_MONTH_STEMS_SORTED",
        tuple(sorted(shuffled.items(), key=lambda kv: len(kv[0]), reverse=True)),
    )

    assert _sql_mod._match_month("маем") == 5
    assert _sql_mod._match_month("мае") == 5
    assert _sql_mod._match_month("мая") == 5
    assert _sql_mod._match_month("май") == 5
    assert _sql_mod._match_month("март") == 3
    assert _sql_mod._match_month("мартом") == 3


def test_match_month_all_twelve_cases():
    from swarm_powerbi_bot.services.sql_client import _match_month

    cases = {
        1: ["январь", "января", "январю", "январе", "январём"],
        2: ["февраль", "февраля", "февралю", "феврале", "февралём"],
        3: ["март", "марта", "марту", "марте", "мартом"],
        4: ["апрель", "апреля", "апрелю", "апреле", "апрелем"],
        5: ["май", "мая", "маю", "мае", "маем"],
        6: ["июнь", "июня", "июню", "июне", "июнем"],
        7: ["июль", "июля", "июлю", "июле", "июлем"],
        8: ["август", "августа", "августу", "августе", "августом"],
        9: ["сентябрь", "сентября", "сентябрю", "сентябре", "сентябрём"],
        10: ["октябрь", "октября", "октябрю", "октябре", "октябрём"],
        11: ["ноябрь", "ноября", "ноябрю", "ноябре", "ноябрём"],
        12: ["декабрь", "декабря", "декабрю", "декабре", "декабрём"],
    }
    for expected, forms in cases.items():
        for form in forms:
            assert _match_month(form) == expected, f"{form!r} → expected {expected}"
