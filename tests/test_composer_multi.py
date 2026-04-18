from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

from swarm_powerbi_bot.agents.composer import ComposedAnswer, MultiAggregateComposer, SingleAggregateComposer


# ── helpers ───────────────────────────────────────────────────────────────────


def _make_data_method(rows: list[dict]) -> MagicMock:
    m = MagicMock()
    m.fetch.return_value = rows
    return m


def _make_llm(aggregates: list[str]) -> MagicMock:
    m = MagicMock()
    m.select_aggregates.return_value = aggregates
    return m


def _make_renderer(png: bytes | None = b"PNG_CHART") -> MagicMock:
    m = MagicMock()
    m.render_comparison_multi.return_value = png
    return m


def _rows(n: int = 3, prefix: str = "x") -> list[dict]:
    return [{"period": f"2026-0{i+1}-01", "value": (i + 1) * 100, "label": f"{prefix}{i}"}
            for i in range(n)]


def _catalog(*names: str, rows_per: int = 3) -> dict:
    return {name: _make_data_method(_rows(rows_per, name)) for name in names}


# ── core acceptance criteria ──────────────────────────────────────────────────


def test_compose_two_aggregates() -> None:
    catalog = _catalog("revenue_by_period", "churn_by_period")
    composer = MultiAggregateComposer(
        llm_client=_make_llm(["revenue_by_period", "churn_by_period"]),
        chart_renderer=_make_renderer(),
        catalog=catalog,
    )
    answer = composer.compose(
        "сравни выручку и отток за март",
        date_from=date(2026, 3, 1),
        date_to=date(2026, 3, 31),
    )
    assert set(answer.aggregate_names) == {"revenue_by_period", "churn_by_period"}
    assert answer.chart is not None
    assert answer.row_count == 6


def test_compose_max_aggregates_clamp() -> None:
    composer = MultiAggregateComposer(
        llm_client=_make_llm(["a", "b", "c", "d", "e"]),
        chart_renderer=_make_renderer(),
        catalog=_catalog("a", "b", "c", "d", "e"),
        max_aggregates=3,
    )
    answer = composer.compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert len(answer.aggregate_names) == 3


def test_compose_no_chart_if_single_point_series() -> None:
    catalog = {
        "revenue_by_period": _make_data_method([{"val": 100}]),
        "churn_by_period": _make_data_method([{"val": 50}]),
    }
    renderer = _make_renderer(None)
    renderer.render_comparison_multi.return_value = None
    composer = MultiAggregateComposer(
        llm_client=_make_llm(["revenue_by_period", "churn_by_period"]),
        chart_renderer=renderer,
        catalog=catalog,
    )
    answer = composer.compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert answer.chart is None
    assert answer.description


def test_compose_single_aggregate_backward_compat() -> None:
    composer = MultiAggregateComposer(
        llm_client=_make_llm(["revenue_by_period"]),
        chart_renderer=_make_renderer(None),
        catalog=_catalog("revenue_by_period"),
    )
    answer = composer.compose(
        "выручка за март",
        date_from=date(2026, 3, 1),
        date_to=date(2026, 3, 31),
    )
    assert answer.aggregate_names == ["revenue_by_period"]
    assert answer.row_count == 3


# ── edge cases ────────────────────────────────────────────────────────────────


def test_compose_empty_aggregates_fallback() -> None:
    composer = MultiAggregateComposer(
        llm_client=_make_llm([]),
        chart_renderer=_make_renderer(),
        catalog={},
    )
    answer = composer.compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert answer.description == "не могу подобрать данные"
    assert answer.chart is None
    assert answer.aggregate_names == []


def test_compose_deduplicates_aggregates() -> None:
    composer = MultiAggregateComposer(
        llm_client=_make_llm(["a", "a", "b"]),
        chart_renderer=_make_renderer(),
        catalog=_catalog("a", "b"),
    )
    answer = composer.compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert answer.aggregate_names == ["a", "b"]


def test_compose_all_fetches_fail_graceful() -> None:
    dm = MagicMock()
    dm.fetch.side_effect = RuntimeError("DB connection lost")
    composer = MultiAggregateComposer(
        llm_client=_make_llm(["revenue_by_period"]),
        chart_renderer=_make_renderer(),
        catalog={"revenue_by_period": dm},
    )
    answer = composer.compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert answer.description == "не могу подобрать данные"
    assert answer.chart is None


def test_compose_partial_fetch_failure_continues() -> None:
    dm_ok = _make_data_method(_rows(3))
    dm_fail = MagicMock()
    dm_fail.fetch.side_effect = RuntimeError("timeout")
    catalog = {"ok_agg": dm_ok, "fail_agg": dm_fail}
    composer = MultiAggregateComposer(
        llm_client=_make_llm(["ok_agg", "fail_agg"]),
        chart_renderer=_make_renderer(None),
        catalog=catalog,
    )
    answer = composer.compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert "ok_agg" in answer.data_sources
    assert "fail_agg" not in answer.data_sources
    assert answer.row_count == 3


def test_compose_invariant_never_raises_on_llm_error() -> None:
    llm = MagicMock()
    llm.select_aggregates.side_effect = RuntimeError("LLM crashed")
    composer = MultiAggregateComposer(
        llm_client=llm,
        chart_renderer=_make_renderer(),
        catalog={},
    )
    answer = composer.compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert isinstance(answer, ComposedAnswer)
    assert answer.chart is None


def test_compose_unknown_aggregate_skipped() -> None:
    composer = MultiAggregateComposer(
        llm_client=_make_llm(["unknown_agg", "revenue_by_period"]),
        chart_renderer=_make_renderer(None),
        catalog=_catalog("revenue_by_period"),
    )
    answer = composer.compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert "unknown_agg" not in answer.data_sources
    assert "revenue_by_period" in answer.data_sources


def test_compose_answer_chart_none_is_valid() -> None:
    renderer = _make_renderer(None)
    renderer.render_comparison_multi.return_value = None
    composer = MultiAggregateComposer(
        llm_client=_make_llm(["a", "b"]),
        chart_renderer=renderer,
        catalog=_catalog("a", "b"),
    )
    answer = composer.compose("test", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert answer.chart is None
    assert answer.description


# ── backward compat: SingleAggregateComposer ─────────────────────────────────


def test_single_aggregate_composer_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match="SingleAggregateComposer"):
        composer = SingleAggregateComposer(
            llm_client=_make_llm(["revenue_by_period"]),
            chart_renderer=_make_renderer(None),
            catalog=_catalog("revenue_by_period"),
        )
    answer = composer.compose("выручка", date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
    assert isinstance(answer, ComposedAnswer)
    assert answer.aggregate_names == ["revenue_by_period"]
