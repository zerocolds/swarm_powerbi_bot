import pytest
from datetime import date, timedelta

from swarm_powerbi_bot.services.sql_client import extract_date_params, has_period_hint


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
    "question",
    [
        pytest.param(
            "пред-март",
            id="hyphen",
            marks=pytest.mark.xfail(
                strict=True,
                reason="open issue: \\b matches after hyphen — _RE_MONTH_BARE needs negative lookbehind",
            ),
        ),
        pytest.param(
            "март'ом",
            id="apostrophe",
            marks=pytest.mark.xfail(
                strict=True,
                reason="open issue: \\b matches before apostrophe — _RE_MONTH_BARE needs lookahead",
            ),
        ),
        pytest.param("март_2026", id="underscore"),
    ],
)
def test_bare_month_rejects_non_boundary(question):
    assert has_period_hint(question) is False


@pytest.mark.parametrize(
    "question",
    [
        pytest.param("март-апрель", id="hyphen_two_months"),
        pytest.param("март.", id="dot"),
        pytest.param("март,", id="comma"),
        pytest.param("(март)", id="parens"),
        pytest.param("март 2026", id="with_year"),
        pytest.param("март", id="bare"),
        pytest.param("с 1 по 15 марта", id="genitive_in_range"),
    ],
)
def test_bare_month_valid_forms_still_detected(question):
    assert has_period_hint(question) is True
