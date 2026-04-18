"""Тесты для has_period_hint() в sql_client.

- «выручка март» → True (bare-month триггер)
- «сравни март и апрель» → True (два bare-month)
- «отток за прошлый месяц» → True (обратная совместимость через ключевое слово)
- «как дела» → False (без периода)

Смоук-тесты поведения has_period_hint. Не привязаны к конкретным
задачам в tasks.md — именованные кейсы ниже (test_bare_month_with_soft_sign_*,
test_has_period_hint_bare_month_all_cases и др.) покрывают явные T-IDs.
"""

import pytest

from swarm_powerbi_bot.services.sql_client import has_period_hint


def test_bare_month_in_question():
    """Месяц без предлога «за» должен распознаваться как подсказка периода."""
    assert has_period_hint("выручка март") is True


def test_compare_two_months():
    """«сравни март и апрель» должен давать True — два месяца без «за»."""
    assert has_period_hint("сравни март и апрель") is True


def test_backward_compat_month_with_za():
    """Классический вариант «за прошлый месяц» должен по-прежнему давать True."""
    assert has_period_hint("отток за прошлый месяц") is True


def test_no_period_hint():
    """Фраза без периода должна давать False."""
    assert has_period_hint("как дела") is False


def test_collision_on_name_marta():
    """После 012-fix-bare-months «Марта» распознаётся как родительный падеж «март»

    (см. spec clarification Q1 + FR-001). Принятая коллизия между
    именем собственным «Марта» и падежной формой «марта».
    """
    assert has_period_hint("мастер Марта") is True


def test_bare_month_with_year():
    """«выручка за май 2025» → True (месяц + год)."""
    assert has_period_hint("выручка за май 2025") is True


def test_range_format():
    """«с 1 по 15 апреля» → True (диапазон)."""
    assert has_period_hint("с 1 по 15 апреля") is True


def test_no_false_positive_on_similar_word():
    """«мартышка» не должна распознаваться как месяц."""
    assert has_period_hint("расскажи про мартышку") is False


def test_no_false_positive_on_masters():
    """«выручка мастеров» без периода → False."""
    assert has_period_hint("выручка мастеров") is False


def test_bare_month_with_soft_sign_april():
    """«выручка апрель» — мягкий знак не должен ломать распознавание."""
    assert has_period_hint("выручка апрель") is True


def test_bare_month_with_soft_sign_january():
    """«выручка январь» — мягкий знак."""
    assert has_period_hint("выручка январь") is True


def test_bare_month_with_soft_sign_september():
    """«сентябрь 2026» — мягкий знак + год."""
    assert has_period_hint("сентябрь 2026") is True


@pytest.mark.parametrize(
    "question",
    [
        # именительный для всех 12 месяцев
        "январь 2026",
        "февраль 2026",
        "март 2026",
        "апрель 2026",
        "май 2026",
        "июнь 2026",
        "июль 2026",
        "август 2026",
        "сентябрь 2026",
        "октябрь 2026",
        "ноябрь 2026",
        "декабрь 2026",
        # творительный падеж — проверяем расширение для всех 12
        "январём 2026",
        "февралём 2026",
        "мартом 2026",
        "апрелем 2026",
        "маем 2026",
        "июнем 2026",
        "июлем 2026",
        "августом 2026",
        "сентябрём 2026",
        "октябрём 2026",
        "ноябрём 2026",
        "декабрём 2026",
    ],
)
def test_has_period_hint_bare_month_all_cases(question):
    """T020a: has_period_hint распознаёт 12 месяцев × 2 формы (именительный + творительный)."""
    assert has_period_hint(question) is True


@pytest.mark.parametrize(
    "question",
    [
        "январский отчёт",
        "мартышка в зоопарке",
        "августовский путч",
    ],
)
def test_has_period_hint_bare_month_negatives(question):
    """T020b: составные слова не дают ложных срабатываний."""
    assert has_period_hint(question) is False
