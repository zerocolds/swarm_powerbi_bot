"""Tests for _match_month() — feature 012-fix-bare-months.

Covers all acceptance criteria and edge cases from the spec:
- All 12 months in multiple Russian inflection forms → correct month number
- May (май) all 5 forms: маем, мая, май, мае, маю → 5
- No collision: март-forms never → 5; май-forms never → 3
- Short prefix "ма" → 0 (no spurious match)
- Empty string → 0 (sentinel)
- Case-insensitivity (Май, МАЙ, МАРТ)
- Result is INDEPENDENT of _MONTH_MAP insertion order (multiple seeds)
"""

from __future__ import annotations

import random

import pytest

import swarm_powerbi_bot.services.sql_client as _sql_mod
from swarm_powerbi_bot.services.sql_client import _MONTH_MAP, _match_month


# ---------------------------------------------------------------------------
# Acceptance criteria: explicit cases from spec
# ---------------------------------------------------------------------------


def test_match_month_maem():
    assert _match_month("маем") == 5


def test_match_month_maya():
    assert _match_month("мая") == 5


def test_match_month_may():
    assert _match_month("май") == 5


def test_match_month_mae():
    assert _match_month("мае") == 5


def test_match_month_mart():
    assert _match_month("март") == 3


def test_match_month_martom():
    assert _match_month("мартом") == 3


def test_match_month_empty():
    assert _match_month("") == 0


# ---------------------------------------------------------------------------
# Parametrized: all 12 months, inflected forms
# ---------------------------------------------------------------------------

_MONTH_FORMS: list[tuple[str, int]] = [
    # январь = 1
    ("январь", 1),
    ("января", 1),
    ("январю", 1),
    ("январём", 1),
    ("январе", 1),
    # февраль = 2
    ("февраль", 2),
    ("февраля", 2),
    ("февралю", 2),
    ("февралём", 2),
    ("феврале", 2),
    # март = 3
    ("март", 3),
    ("марта", 3),
    ("марту", 3),
    ("мартом", 3),
    ("марте", 3),
    # апрель = 4
    ("апрель", 4),
    ("апреля", 4),
    ("апрелю", 4),
    ("апрелем", 4),
    ("апреле", 4),
    # май = 5 (all 5 forms, critical for fix-012)
    ("май", 5),
    ("мая", 5),
    ("маю", 5),
    ("маем", 5),
    ("мае", 5),
    # июнь = 6
    ("июнь", 6),
    ("июня", 6),
    ("июню", 6),
    ("июнем", 6),
    ("июне", 6),
    # июль = 7
    ("июль", 7),
    ("июля", 7),
    ("июлю", 7),
    ("июлем", 7),
    ("июле", 7),
    # август = 8
    ("август", 8),
    ("августа", 8),
    ("августу", 8),
    ("августом", 8),
    ("августе", 8),
    # сентябрь = 9
    ("сентябрь", 9),
    ("сентября", 9),
    ("сентябрю", 9),
    ("сентябрём", 9),
    ("сентябре", 9),
    # октябрь = 10
    ("октябрь", 10),
    ("октября", 10),
    ("октябрю", 10),
    ("октябрём", 10),
    ("октябре", 10),
    # ноябрь = 11
    ("ноябрь", 11),
    ("ноября", 11),
    ("ноябрю", 11),
    ("ноябрём", 11),
    ("ноябре", 11),
    # декабрь = 12
    ("декабрь", 12),
    ("декабря", 12),
    ("декабрю", 12),
    ("декабрём", 12),
    ("декабре", 12),
]


@pytest.mark.parametrize("token,expected", _MONTH_FORMS)
def test_match_month_all_forms(token: str, expected: int):
    assert _match_month(token) == expected


# ---------------------------------------------------------------------------
# No-collision: май-forms must never return 3, март-forms never return 5
# ---------------------------------------------------------------------------

_MAY_FORMS = ["май", "мая", "маю", "маем", "мае"]
_MARCH_FORMS = ["март", "марта", "марту", "мартом", "марте"]


@pytest.mark.parametrize("token", _MAY_FORMS)
def test_may_forms_not_march(token: str):
    assert _match_month(token) != 3


@pytest.mark.parametrize("token", _MARCH_FORMS)
def test_march_forms_not_may(token: str):
    assert _match_month(token) != 5


# ---------------------------------------------------------------------------
# Edge case: short prefix "ма" must NOT greedily match "май"
# ---------------------------------------------------------------------------

def test_match_month_short_prefix_ma_no_match():
    # "ма" is not a valid month token — must return 0
    assert _match_month("ма") == 0


def test_match_month_short_prefix_ян_no_match():
    # partial prefix, no stem reaches it
    assert _match_month("ян") == 0


def test_match_month_unrelated_no_match():
    assert _match_month("понедельник") == 0
    assert _match_month("квартал") == 0
    assert _match_month("год") == 0


# ---------------------------------------------------------------------------
# Case-insensitivity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("token,expected", [
    ("Май", 5),
    ("МАЙ", 5),
    ("Мая", 5),
    ("МАЕМ", 5),
    ("Март", 3),
    ("МАРТ", 3),
    ("Январь", 1),
    ("ДЕКАБРЬ", 12),
])
def test_match_month_case_insensitive(token: str, expected: int):
    assert _match_month(token) == expected


# ---------------------------------------------------------------------------
# Order-independence: shuffled _MONTH_MAP must yield identical results
# Multiple seeds to reduce flakiness probability to near zero.
# ---------------------------------------------------------------------------

_ORDER_INDEPENDENCE_CASES = [
    ("маем", 5),
    ("мая", 5),
    ("май", 5),
    ("мае", 5),
    ("маю", 5),
    ("март", 3),
    ("мартом", 3),
    ("январь", 1),
    ("декабрь", 12),
]


@pytest.mark.parametrize("seed", [0, 1, 42, 99, 12345])
def test_match_month_order_independent_multi_seed(seed: int, monkeypatch):
    """Result must not depend on _MONTH_MAP insertion order."""
    items = list(_MONTH_MAP.items())
    rng = random.Random(seed)
    rng.shuffle(items)
    shuffled = dict(items)
    monkeypatch.setattr(_sql_mod, "_MONTH_MAP", shuffled)

    for token, expected in _ORDER_INDEPENDENCE_CASES:
        assert _match_month(token) == expected, (
            f"seed={seed}: _match_month({token!r}) should be {expected}"
        )


def test_match_month_reversed_map_order(monkeypatch):
    """Reversed map (worst-case for insertion-order bugs) must still work."""
    reversed_map = dict(reversed(list(_MONTH_MAP.items())))
    monkeypatch.setattr(_sql_mod, "_MONTH_MAP", reversed_map)

    assert _match_month("маем") == 5
    assert _match_month("мая") == 5
    assert _match_month("май") == 5
    assert _match_month("мае") == 5
    assert _match_month("март") == 3
    assert _match_month("январь") == 1
    assert _match_month("декабрь") == 12
    assert _match_month("") == 0


# ---------------------------------------------------------------------------
# Negative: verify that naive insertion-order iteration WOULD fail on reversed map
# (documents the bug that was fixed; this test should PASS because we prove
# the fix works, not that the old code works)
# ---------------------------------------------------------------------------

def test_match_month_maem_not_ambiguous():
    """'маем' must resolve to 5 (May), not mis-matched via a shorter stem."""
    # Without longest-match, a naive iteration could pick "мае" before "маем",
    # or miss "мае" entirely if "май" was first in the map.
    # All May forms must resolve to 5.
    assert _match_month("маем") == 5
    assert _match_month("мае") == 5
    assert _match_month("мая") == 5
    assert _match_month("маю") == 5
    assert _match_month("май") == 5
