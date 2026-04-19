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


def test_invalid_range_logs_debug(caplog):
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        extract_date_params("с 30 по 31 февраля 2025")
    assert any("invalid date" in r.message for r in caplog.records)


def test_invariant_i1_invalid_range_returns_default():
    params = extract_date_params("с 30 по 31 февраля 2025")
    assert hasattr(params["DateFrom"], "year")
    assert hasattr(params["DateTo"], "year")
    assert params["DateFrom"] <= params["DateTo"]


def test_invariant_i1_invalid_day_in_range():
    params = extract_date_params("с 1 по 32 марта 2026")
    assert hasattr(params["DateFrom"], "year")
    assert params["DateFrom"] <= params["DateTo"]


def test_invariant_i1_year_zero():
    params = extract_date_params("за январь 0000")
    assert hasattr(params["DateFrom"], "year")
    assert params["DateFrom"] <= params["DateTo"]


def test_invalid_date_log_excludes_full_question(caplog):
    question = "с 30 по 31 февраля 2025 секретный текст"
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        extract_date_params(question)
    invalid_records = [r for r in caplog.records if "invalid date" in r.message]
    assert invalid_records
    for rec in invalid_records:
        assert "секретный" not in rec.getMessage()
        assert getattr(rec, "question", None) is None
        assert getattr(rec, "question_len", None) == len(question)


def test_invalid_date_log_strategy_range(caplog):
    """Branch 'range' (с N по M <month>) emits DEBUG with strategy_name."""
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        extract_date_params("с 30 по 31 февраля 2025")
    invalid = [r for r in caplog.records if "invalid date" in r.message]
    assert invalid, "range branch must emit DEBUG on ValueError"
    assert any("range" in r.getMessage() for r in invalid)


def test_invalid_date_log_strategy_za_month(caplog):
    """Branch 'za_month' (за <month> <year>) with year=0 emits DEBUG."""
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        extract_date_params("за январь 0000")
    invalid = [r for r in caplog.records if "invalid date" in r.message]
    assert invalid, "za_month branch must emit DEBUG on ValueError (year=0)"
    assert any("za_month" in r.getMessage() for r in invalid)


def test_invalid_date_log_strategy_bare_month(caplog):
    """Branch 'bare_month' (<month> <year>) with year=0 emits DEBUG."""
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        extract_date_params("январь 0000")
    invalid = [r for r in caplog.records if "invalid date" in r.message]
    assert invalid, "bare_month branch must emit DEBUG on ValueError"
    assert any("bare_month" in r.getMessage() for r in invalid)


def test_invalid_date_log_has_exc_info(caplog):
    """exc_info=True — запись содержит информацию об exception."""
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        extract_date_params("с 30 по 31 февраля 2025")
    invalid = [r for r in caplog.records if "invalid date" in r.message]
    assert invalid
    assert any(r.exc_info is not None for r in invalid), (
        "exc_info=True требуется для диагностики по телеметрии"
    )


def test_valid_input_no_invalid_date_log(caplog):
    """Валидный input — НЕ должен триггерить 'invalid date' DEBUG."""
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        params = extract_date_params("за март 2025")
    assert params["DateFrom"] == date(2025, 3, 1)
    invalid = [r for r in caplog.records if "invalid date" in r.message]
    assert not invalid, "valid input must not emit 'invalid date' DEBUG"


def test_valid_range_no_invalid_date_log(caplog):
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        params = extract_date_params("с 5 по 20 апреля 2025")
    assert params["DateFrom"] == date(2025, 4, 5)
    invalid = [r for r in caplog.records if "invalid date" in r.message]
    assert not invalid


def test_valid_bare_month_no_invalid_date_log(caplog):
    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
        params = extract_date_params("выручка март 2025")
    assert params["DateFrom"] == date(2025, 3, 1)
    invalid = [r for r in caplog.records if "invalid date" in r.message]
    assert not invalid


def test_invariant_i1_day_32_march():
    """Edge case из spec: 'с 1 по 32 марта 2026' → default, не бросает."""
    params = extract_date_params("с 1 по 32 марта 2026")
    assert hasattr(params["DateFrom"], "year")
    assert hasattr(params["DateTo"], "year")
    assert params["DateFrom"] <= params["DateTo"]


def test_invariant_i1_feb_30_31():
    """Edge case: 'с 30 по 31 февраля 2025' — не существующие дни февраля."""
    params = extract_date_params("с 30 по 31 февраля 2025")
    assert hasattr(params["DateFrom"], "year")
    assert hasattr(params["DateTo"], "year")
    assert params["DateFrom"] <= params["DateTo"]


def test_invariant_i1_year_zero_za_month():
    """'за январь 0000' → ValueError от date(0,1,1) → default, не бросает."""
    params = extract_date_params("за январь 0000")
    assert hasattr(params["DateFrom"], "year")
    assert params["DateFrom"] <= params["DateTo"]


def test_privacy_question_len_not_full_question_all_branches(caplog):
    """R-008: В extra кладётся question_len, но не полный текст question."""
    secret = "супер-секретное-поле-которое-не-должно-утечь"
    questions = [
        f"с 30 по 31 февраля 2025 {secret}",
        f"за январь 0000 {secret}",
        f"январь 0000 {secret}",
    ]
    for q in questions:
        caplog.clear()
        with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.sql_client"):
            extract_date_params(q)
        invalid = [r for r in caplog.records if "invalid date" in r.message]
        assert invalid, f"no invalid-date log for: {q}"
        for rec in invalid:
            assert secret not in rec.getMessage()
            assert getattr(rec, "question", None) is None
            assert getattr(rec, "question_len", None) == len(q)


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
