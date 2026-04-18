from __future__ import annotations

import logging
import time
import warnings
from dataclasses import dataclass
from datetime import date
from typing import Any

logger = logging.getLogger("composer_multi")


@dataclass(frozen=True)
class ComposedAnswer:
    description: str
    data_sources: list[str]
    aggregate_names: list[str]
    row_count: int
    chart: bytes | None


class MultiAggregateComposer:
    """Composer that selects multiple aggregates via LLM and renders a comparison chart."""

    def __init__(
        self,
        llm_client: Any,
        chart_renderer: Any,
        catalog: dict[str, Any] | None = None,
        *,
        max_aggregates: int = 3,
    ) -> None:
        self._llm = llm_client
        self._renderer = chart_renderer
        self._catalog: dict[str, Any] = catalog if catalog is not None else {}
        self._max_aggregates = max_aggregates

    def compose(
        self,
        question: str,
        *,
        date_from: date,
        date_to: date,
    ) -> ComposedAnswer:
        try:
            return self._compose(question, date_from=date_from, date_to=date_to)
        except Exception:
            logger.exception("composer_multi: unexpected error")
            return ComposedAnswer(
                description="не могу подобрать данные",
                data_sources=[],
                aggregate_names=[],
                row_count=0,
                chart=None,
            )

    def _compose(
        self,
        question: str,
        *,
        date_from: date,
        date_to: date,
    ) -> ComposedAnswer:
        raw: list[str] = self._llm.select_aggregates(question, date_from, date_to)

        seen: set[str] = set()
        aggregates: list[str] = []
        for agg in raw:
            if agg not in seen:
                seen.add(agg)
                aggregates.append(agg)

        if len(aggregates) > self._max_aggregates:
            logger.warning(
                "composer_multi: LLM returned %d aggregates, clamping to %d",
                len(aggregates),
                self._max_aggregates,
            )
            aggregates = aggregates[: self._max_aggregates]

        if not aggregates:
            logger.debug("composer_multi: empty aggregates list from LLM")
            return ComposedAnswer(
                description="не могу подобрать данные",
                data_sources=[],
                aggregate_names=[],
                row_count=0,
                chart=None,
            )

        data_frames: list[list[dict[str, Any]]] = []
        data_sources: list[str] = []
        latency_ms_per_source: dict[str, int] = {}

        for agg_name in aggregates:
            data_method = self._catalog.get(agg_name)
            if data_method is None:
                logger.warning("composer_multi: unknown aggregate %r, skipping", agg_name)
                continue
            t0 = time.monotonic()
            try:
                rows: list[dict[str, Any]] = data_method.fetch(
                    date_from=date_from, date_to=date_to
                )
            except Exception:
                logger.warning(
                    "composer_multi: fetch failed for %r", agg_name, exc_info=True
                )
                continue
            latency_ms_per_source[agg_name] = int((time.monotonic() - t0) * 1000)
            data_frames.append(rows)
            data_sources.append(agg_name)

        if not data_frames:
            logger.warning("composer_multi: all fetches failed")
            return ComposedAnswer(
                description="не могу подобрать данные",
                data_sources=[],
                aggregate_names=aggregates,
                row_count=0,
                chart=None,
            )

        total_rows = sum(len(df) for df in data_frames)

        chart: bytes | None = None
        chart_rendered = False
        try:
            chart = self._renderer.render_comparison_multi(data_frames, data_sources)
            chart_rendered = chart is not None
        except Exception:
            logger.warning("composer_multi: chart render failed", exc_info=True)

        logger.debug(
            "composer_multi: aggregates_selected=%r latency_ms_per_source=%r chart_rendered=%r",
            data_sources,
            latency_ms_per_source,
            chart_rendered,
        )

        description = _build_description(data_sources, data_frames)

        return ComposedAnswer(
            description=description,
            data_sources=data_sources,
            aggregate_names=aggregates,
            row_count=total_rows,
            chart=chart,
        )


def _build_description(sources: list[str], data_frames: list[list[dict[str, Any]]]) -> str:
    parts = [f"{src}: {len(df)} записей" for src, df in zip(sources, data_frames)]
    return "; ".join(parts)


class SingleAggregateComposer:
    """Deprecated: use MultiAggregateComposer with max_aggregates=1."""

    def __init__(
        self,
        llm_client: Any,
        chart_renderer: Any,
        catalog: dict[str, Any] | None = None,
    ) -> None:
        warnings.warn(
            "SingleAggregateComposer is deprecated, use MultiAggregateComposer",
            DeprecationWarning,
            stacklevel=2,
        )
        self._inner = MultiAggregateComposer(
            llm_client=llm_client,
            chart_renderer=chart_renderer,
            catalog=catalog,
            max_aggregates=1,
        )

    def compose(
        self,
        question: str,
        *,
        date_from: date,
        date_to: date,
    ) -> ComposedAnswer:
        return self._inner.compose(question, date_from=date_from, date_to=date_to)
