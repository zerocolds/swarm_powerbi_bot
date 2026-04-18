import re
import time
import inspect
import pytest
from datetime import date, timedelta

from swarm_powerbi_bot.services.sql_client import (
    extract_date_params,
    has_period_hint,
    _RE_MONTH,
    _RE_MONTH_BARE,
    _RE_RANGE,
)
import swarm_powerbi_bot.services.sql_client as _sql_client_module


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


# ── Acceptance: _RE_MONTH uses explicit alternations (no greedy \w*) ─────────

def test_re_month_no_greedy_suffix():
    """_RE_MONTH pattern must NOT use \\w* (greedy suffix) — only explicit alternations."""
    pattern = _RE_MONTH.pattern
    # The za-month branch must not fall back to \w* catch-all
    assert r"\w*" not in pattern, (
        "_RE_MONTH still uses \\w* greedy suffix; must use explicit alternations per spec"
    )


def test_re_month_has_all_12_months():
    """_RE_MONTH pattern must reference all 12 Russian month stems."""
    pattern = _RE_MONTH.pattern.lower()
    stems = ["январ", "феврал", "март", "апрел", "ма", "июн", "июл", "август",
             "сентябр", "октябр", "ноябр", "декабр"]
    for stem in stems:
        assert stem in pattern, f"Stem '{stem}' missing from _RE_MONTH pattern"


def test_i7_comment_present_in_source():
    """Source file must contain I-7 ReDoS-safe invariant comment."""
    source = inspect.getsource(_sql_client_module)
    assert "I-7" in source, "I-7 ReDoS-safe invariant comment missing from sql_client.py"


# ── ReDoS guard: <10ms on adversarial 10k-char input ────────────────────────

_ADVERSARIAL_10K = "за " + "а" * 9997  # no valid month — worst-case backtrack path


def test_redos_guard_re_month():
    """_RE_MONTH must match (or reject) a 10k adversarial string in <10ms."""
    start = time.perf_counter()
    _RE_MONTH.search(_ADVERSARIAL_10K)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 10, f"_RE_MONTH took {elapsed_ms:.1f}ms on 10k input — possible ReDoS"


def test_redos_guard_re_month_bare():
    """_RE_MONTH_BARE must match (or reject) a 10k adversarial string in <10ms."""
    adversarial = "а" * 10_000
    start = time.perf_counter()
    _RE_MONTH_BARE.search(adversarial)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 10, f"_RE_MONTH_BARE took {elapsed_ms:.1f}ms on 10k input — possible ReDoS"


def test_redos_guard_re_range():
    """_RE_RANGE must match (or reject) a 10k adversarial string in <10ms."""
    adversarial = "с 1 по 2 " + "а" * 9991
    start = time.perf_counter()
    _RE_RANGE.search(adversarial)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 10, f"_RE_RANGE took {elapsed_ms:.1f}ms on 10k input — possible ReDoS"


# ── Bare-month strategy does not break when _RE_MONTH changes ─────────────────

@pytest.mark.parametrize("query,expected_month", [
    ("выручка март", 3),
    ("выручка апрель", 4),
    ("сентябрь 2025", 9),
    ("январь", 1),
    ("декабрь 2024", 12),
])
def test_bare_month_strategy_intact(query, expected_month):
    """_RE_MONTH_BARE (bare-month strategy) must still recognise standalone months."""
    m = _RE_MONTH_BARE.search(query.lower())
    assert m is not None, f"_RE_MONTH_BARE did not match '{query}'"
    from swarm_powerbi_bot.services.sql_client import _match_month
    assert _match_month(m.group(1)) == expected_month


# ── Range strategy does not break ────────────────────────────────────────────

@pytest.mark.parametrize("query,day_from,day_to,month,year", [
    ("с 1 по 15 марта 2025", 1, 15, 3, 2025),
    ("с 5 по 20 апреля 2026", 5, 20, 4, 2026),
    ("с 10 по 31 декабря 2023", 10, 31, 12, 2023),
])
def test_range_strategy_intact(query, day_from, day_to, month, year):
    """Range strategy (с X по Y месяц) must remain unaffected."""
    params = extract_date_params(query)
    assert params["DateFrom"] == date(year, month, day_from)
    assert params["DateTo"] == date(year, month, day_to)


# ── Additional edge cases from spec ──────────────────────────────────────────

def test_za_unknown_garbage_various():
    """Various non-month words after «за» must all fallback to default 30 days."""
    today = date.today()
    default_from = today - timedelta(days=30)
    for bad in ["хрущовка", "собака", "123abc", "маяк", "сентябрина"]:
        params = extract_date_params(f"выручка за {bad} 2026")
        assert params["DateFrom"] == default_from, f"Unexpected match for «за {bad}»"


def test_za_may_forms():
    """«май» and «мая» are both valid and map to month 5."""
    for form in ("май", "мая"):
        params = extract_date_params(f"выручка за {form} 2026")
        assert params["DateFrom"].month == 5, f"Form «{form}» not matched"
        assert params["DateFrom"].year == 2026


def test_za_month_correct_last_day_february():
    """«за февраль 2024» (leap year) → DateTo == 2024-02-29."""
    params = extract_date_params("за февраль 2024")
    assert params["DateTo"] == date(2024, 2, 29)


def test_za_month_correct_last_day_december():
    """«за декабрь 2025» → DateTo == 2025-12-31."""
    params = extract_date_params("за декабрь 2025")
    assert params["DateTo"] == date(2025, 12, 31)


def test_za_month_takes_priority_over_bare_month():
    """When both «за месяц» and bare month are present, za-month is matched first."""
    params = extract_date_params("за январь 2026 и февраль")
    assert params["DateFrom"].month == 1
    assert params["DateFrom"].year == 2026
