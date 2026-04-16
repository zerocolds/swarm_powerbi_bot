"""Тесты для has_period_hint() в sql_client.

T018 [US4] «выручка март» → True
T019 [US4] «сравни март и апрель» → True
T020 [US4] «отток за прошлый месяц» → True (обратная совместимость)
T021 [US4] «как дела» → False
"""

from swarm_powerbi_bot.services.sql_client import has_period_hint


def test_T018_bare_month_in_question():
    """Месяц без предлога «за» должен распознаваться как подсказка периода."""
    assert has_period_hint("выручка март") is True


def test_T019_compare_two_months():
    """«сравни март и апрель» должен давать True — два месяца без «за»."""
    assert has_period_hint("сравни март и апрель") is True


def test_T020_backward_compat_month_with_za():
    """Классический вариант «за прошлый месяц» должен по-прежнему давать True."""
    assert has_period_hint("отток за прошлый месяц") is True


def test_T021_no_period_hint():
    """Фраза без периода должна давать False."""
    assert has_period_hint("как дела") is False
