"""Regression baseline: multi-aggregate composer queries.

Covers ≥3 multi-aggregate scenarios as required by acceptance criteria.
"""
from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from swarm_powerbi_bot.agents.composer import ComposedAnswer, MultiAggregateComposer


# ── helpers ───────────────────────────────────────────────────────────────────


def _dm(rows: list[dict]) -> MagicMock:
    m = MagicMock()
    m.fetch.return_value = rows
    return m


def _llm(aggregates: list[str]) -> MagicMock:
    m = MagicMock()
    m.select_aggregates.return_value = aggregates
    return m


def _renderer(png: bytes | None = b"PNG") -> MagicMock:
    m = MagicMock()
    m.render_comparison_multi.return_value = png
    return m


def _rows(n: int = 5) -> list[dict]:
    return [{"period": f"2026-0{i % 9 + 1}-01", "value": (i + 1) * 100} for i in range(n)]


# ── regression baselines ──────────────────────────────────────────────────────


def test_regression_revenue_and_churn_march() -> None:
    """сравни выручку март и отток за март — 2 агрегата, есть график."""
    catalog = {
        "revenue_by_period": _dm(_rows()),
        "churn_by_period": _dm(_rows()),
    }
    answer = MultiAggregateComposer(
        llm_client=_llm(["revenue_by_period", "churn_by_period"]),
        chart_renderer=_renderer(),
        catalog=catalog,
    ).compose(
        "сравни выручку март и отток за март",
        date_from=date(2026, 3, 1),
        date_to=date(2026, 3, 31),
    )
    assert set(answer.aggregate_names) == {"revenue_by_period", "churn_by_period"}
    assert answer.chart is not None
    assert answer.row_count == 10


def test_regression_revenue_and_churn_quarter() -> None:
    """выручка и отток за квартал — 2 агрегата."""
    catalog = {
        "revenue_quarterly": _dm(_rows(3)),
        "churn_quarterly": _dm(_rows(3)),
    }
    answer = MultiAggregateComposer(
        llm_client=_llm(["revenue_quarterly", "churn_quarterly"]),
        chart_renderer=_renderer(),
        catalog=catalog,
    ).compose(
        "выручка и отток за квартал",
        date_from=date(2026, 1, 1),
        date_to=date(2026, 3, 31),
    )
    assert len(answer.aggregate_names) == 2
    assert answer.row_count == 6


def test_regression_three_metrics_comparison() -> None:
    """три метрики за период — выручка, отток, средний чек."""
    catalog = {
        "revenue_by_period": _dm(_rows()),
        "churn_by_period": _dm(_rows()),
        "avg_check": _dm(_rows()),
    }
    answer = MultiAggregateComposer(
        llm_client=_llm(["revenue_by_period", "churn_by_period", "avg_check"]),
        chart_renderer=_renderer(),
        catalog=catalog,
        max_aggregates=3,
    ).compose(
        "сравни выручку, отток и средний чек",
        date_from=date(2026, 3, 1),
        date_to=date(2026, 3, 31),
    )
    assert len(answer.aggregate_names) == 3
    assert answer.chart is not None


def test_regression_single_aggregate_text_only() -> None:
    """один агрегат — нет сравнительного графика, только текст."""
    catalog = {"revenue_by_period": _dm(_rows())}
    answer = MultiAggregateComposer(
        llm_client=_llm(["revenue_by_period"]),
        chart_renderer=_renderer(None),
        catalog=catalog,
    ).compose(
        "выручка за март",
        date_from=date(2026, 3, 1),
        date_to=date(2026, 3, 31),
    )
    assert len(answer.aggregate_names) == 1
    assert answer.description


def test_regression_clamped_to_max_aggregates() -> None:
    """LLM вернул >max → усечение до max_aggregates."""
    catalog = {name: _dm(_rows(2)) for name in "abcd"}
    answer = MultiAggregateComposer(
        llm_client=_llm(list("abcd")),
        chart_renderer=_renderer(),
        catalog=catalog,
        max_aggregates=3,
    ).compose(
        "все метрики",
        date_from=date(2026, 3, 1),
        date_to=date(2026, 3, 31),
    )
    assert len(answer.aggregate_names) == 3


def test_regression_no_chart_single_point() -> None:
    """<2 точек на серию → chart=None, описание есть."""
    catalog = {
        "revenue_by_period": _dm([{"val": 100}]),
        "churn_by_period": _dm([{"val": 50}]),
    }
    renderer = _renderer(None)
    renderer.render_comparison_multi.return_value = None
    answer = MultiAggregateComposer(
        llm_client=_llm(["revenue_by_period", "churn_by_period"]),
        chart_renderer=renderer,
        catalog=catalog,
    ).compose(
        "сравни выручку и отток",
        date_from=date(2026, 3, 1),
        date_to=date(2026, 3, 31),
    )
    assert answer.chart is None
    assert answer.description


def test_regression_invariant_never_raises() -> None:
    """compose() никогда не бросает исключений."""
    llm = MagicMock()
    llm.select_aggregates.side_effect = Exception("unexpected")
    answer = MultiAggregateComposer(
        llm_client=llm,
        chart_renderer=_renderer(),
        catalog={},
    ).compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert isinstance(answer, ComposedAnswer)
