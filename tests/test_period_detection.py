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


@pytest.mark.parametrize("month_form,expected_month", [
    ("январь", 1), ("января", 1), ("январю", 1), ("январе", 1), ("январём", 1),
    ("февраль", 2), ("февраля", 2), ("февралю", 2), ("феврале", 2), ("февралём", 2),
    ("март", 3), ("марта", 3), ("марту", 3), ("марте", 3), ("мартом", 3),
    ("апрель", 4), ("апреля", 4), ("апрелю", 4), ("апреле", 4), ("апрелём", 4),
    ("май", 5), ("мая", 5),
    ("июнь", 6), ("июня", 6), ("июню", 6), ("июне", 6), ("июнем", 6),
    ("июль", 7), ("июля", 7), ("июлю", 7), ("июле", 7), ("июлем", 7),
    ("август", 8), ("августа", 8), ("августу", 8), ("августе", 8), ("августом", 8),
    ("сентябрь", 9), ("сентября", 9), ("сентябрю", 9), ("сентябре", 9), ("сентябрём", 9),
    ("октябрь", 10), ("октября", 10), ("октябрю", 10), ("октябре", 10), ("октябрём", 10),
    ("ноябрь", 11), ("ноября", 11), ("ноябрю", 11), ("ноябре", 11), ("ноябрём", 11),
    ("декабрь", 12), ("декабря", 12), ("декабрю", 12), ("декабре", 12), ("декабрём", 12),
])
def test_za_month_all_cases(month_form, expected_month):
    params = extract_date_params(f"выручка за {month_form} 2026")
    assert params["DateFrom"].year == 2026
    assert params["DateFrom"].month == expected_month


def test_za_unknown_word_not_matched():
    params = extract_date_params("выручка за хрущовка 2026")
    today = date.today()
    assert params["DateFrom"] == today - timedelta(days=30)


def test_za_month_no_year_uses_current_year():
    today = date.today()
    params = extract_date_params("выручка за апрель")
    assert params["DateFrom"] == date(today.year, 4, 1)


def test_za_first_match_wins():
    params = extract_date_params("выручка за январь декабрь 2026")
    assert params["DateFrom"].month == 1
