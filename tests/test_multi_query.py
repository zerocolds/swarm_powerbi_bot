"""T028: Тесты для SQLAgent.run_multi (Phase 7 — Multi-query SQLAgent)."""

from __future__ import annotations

import asyncio
import textwrap
from unittest.mock import AsyncMock, MagicMock

import pytest

from swarm_powerbi_bot.agents.sql import SQLAgent
from swarm_powerbi_bot.config import Settings
from swarm_powerbi_bot.models import AggregateQuery, AggregateResult, MultiPlan
from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry


# ── fixtures ──────────────────────────────────────────────────────────────────

CATALOG_YAML = textwrap.dedent("""\
    aggregates:
      - id: revenue_by_master
        name: Выручка по мастерам
        procedure: spKDO_Aggregate
        allowed_group_by:
          - master
          - day
      - id: visits_by_object
        name: Визиты по объектам
        procedure: spKDO_Aggregate
        allowed_group_by:
          - object
          - week
""")


@pytest.fixture()
def catalog_file(tmp_path):
    p = tmp_path / "catalog.yaml"
    p.write_text(CATALOG_YAML, encoding="utf-8")
    return str(p)


@pytest.fixture()
def registry(catalog_file):
    return AggregateRegistry(catalog_file)


@pytest.fixture()
def settings():
    return Settings(
        sql_max_queries=10,
        sql_max_concurrency=5,
        sql_query_timeout=10,
    )


def _make_agent(settings):
    sql_client_mock = MagicMock()
    agent = SQLAgent(client=sql_client_mock, settings=settings)
    return agent, sql_client_mock


def _ok_result(aggregate_id: str, label: str = "") -> AggregateResult:
    return AggregateResult(
        aggregate_id=aggregate_id,
        label=label or aggregate_id,
        rows=[{"val": 1}],
        row_count=1,
        duration_ms=5,
        status="ok",
    )


def _make_plan(queries: list[AggregateQuery]) -> MultiPlan:
    return MultiPlan(
        objective="test",
        intent="single",
        queries=queries,
        topic="statistics",
    )


# ── T028-1: 2 запроса → оба выполняются → список из 2 AggregateResult ────────


@pytest.mark.asyncio
async def test_two_queries_both_execute(registry, settings):
    agent, sql_client_mock = _make_agent(settings)

    sql_client_mock.execute_aggregate = AsyncMock(
        side_effect=lambda agg_id, params, reg: _ok_result(agg_id)
    )

    queries = [
        AggregateQuery(aggregate_id="revenue_by_master", params={}, label="выручка"),
        AggregateQuery(aggregate_id="visits_by_object", params={}, label="визиты"),
    ]
    plan = _make_plan(queries)

    results = await agent.run_multi(plan, registry, sql_client=sql_client_mock)

    assert len(results) == 2
    assert all(r.status == "ok" for r in results)
    called_ids = {
        call.args[0] for call in sql_client_mock.execute_aggregate.call_args_list
    }
    assert called_ids == {"revenue_by_master", "visits_by_object"}


# ── T028-2: 12 запросов → только первые 10 выполняются (лимит) ───────────────


@pytest.mark.asyncio
async def test_limit_enforced_to_max_queries(registry, settings):
    agent, sql_client_mock = _make_agent(settings)

    sql_client_mock.execute_aggregate = AsyncMock(
        side_effect=lambda agg_id, params, reg: _ok_result(agg_id)
    )

    # 12 запросов, все с одним aggregate_id из каталога
    queries = [
        AggregateQuery(aggregate_id="revenue_by_master", params={}, label=f"q{i}")
        for i in range(12)
    ]
    plan = _make_plan(queries)

    results = await agent.run_multi(plan, registry, sql_client=sql_client_mock)

    assert len(results) == 10
    assert sql_client_mock.execute_aggregate.call_count == 10


# ── T028-3: Частичный сбой: 1 из 3 запросов → timeout ───────────────────────


@pytest.mark.asyncio
async def test_partial_timeout_other_queries_succeed(registry, settings):
    agent, sql_client_mock = _make_agent(settings)

    call_count = 0

    async def _side_effect(agg_id, params, reg):
        nonlocal call_count
        call_count += 1
        if agg_id == "visits_by_object" and call_count == 2:
            # Имитируем долгое ожидание, которое приведёт к TimeoutError
            await asyncio.sleep(999)
        return _ok_result(agg_id)

    sql_client_mock.execute_aggregate = _side_effect

    # Устанавливаем очень маленький timeout чтобы второй запрос упал
    fast_settings = Settings(
        sql_max_queries=10,
        sql_max_concurrency=5,
        sql_query_timeout=0.1,  # 100 мс — достаточно мало для timeout теста, но стабильно на CI
    )
    agent_fast = SQLAgent(client=sql_client_mock, settings=fast_settings)

    queries = [
        AggregateQuery(aggregate_id="revenue_by_master", params={}, label="первый"),
        AggregateQuery(aggregate_id="visits_by_object", params={}, label="второй"),
        AggregateQuery(aggregate_id="revenue_by_master", params={}, label="третий"),
    ]
    plan = _make_plan(queries)

    results = await agent_fast.run_multi(plan, registry, sql_client=sql_client_mock)

    assert len(results) == 3

    statuses = {r.label: r.status for r in results}
    assert statuses["первый"] == "ok"
    assert statuses["второй"] == "timeout"
    assert statuses["третий"] == "ok"


# ── T028-4: Семафор ограничивает конкурентность до 5 ─────────────────────────


@pytest.mark.asyncio
async def test_semaphore_limits_concurrency(registry, settings):
    agent, sql_client_mock = _make_agent(settings)

    active_count = 0
    max_observed = 0

    async def _tracked(agg_id, params, reg):
        nonlocal active_count, max_observed
        active_count += 1
        max_observed = max(max_observed, active_count)
        # небольшая задержка чтобы конкурентность была видна
        await asyncio.sleep(0.01)
        active_count -= 1
        return _ok_result(agg_id)

    sql_client_mock.execute_aggregate = _tracked

    # 10 запросов при max_concurrency=5
    queries = [
        AggregateQuery(aggregate_id="revenue_by_master", params={}, label=f"q{i}")
        for i in range(10)
    ]
    plan = _make_plan(queries)

    results = await agent.run_multi(plan, registry, sql_client=sql_client_mock)

    assert len(results) == 10
    assert all(r.status == "ok" for r in results)
    # Максимальная конкурентность не должна превышать sql_max_concurrency=5
    assert max_observed <= settings.sql_max_concurrency


# ── T032: QueryLogger вызывается для каждого агрегата ────────────────────────


@pytest.mark.asyncio
async def test_query_logger_called_for_each_aggregate(registry, settings):
    agent, sql_client_mock = _make_agent(settings)

    sql_client_mock.execute_aggregate = AsyncMock(
        side_effect=lambda agg_id, params, reg: _ok_result(agg_id)
    )

    mock_logger = MagicMock()
    mock_logger.log = MagicMock()

    queries = [
        AggregateQuery(aggregate_id="revenue_by_master", params={}, label="a"),
        AggregateQuery(aggregate_id="visits_by_object", params={}, label="b"),
    ]
    plan = _make_plan(queries)

    results = await agent.run_multi(
        plan, registry, sql_client=sql_client_mock, logger_=mock_logger
    )

    assert len(results) == 2
    assert mock_logger.log.call_count == 2

    logged_agg_ids = {
        call.kwargs.get("aggregate_id") or call.args[1]
        for call in mock_logger.log.call_args_list
    }
    assert "revenue_by_master" in logged_agg_ids
    assert "visits_by_object" in logged_agg_ids


# ── Дополнительно: ошибка в одном запросе не ломает весь батч ────────────────


@pytest.mark.asyncio
async def test_error_in_one_query_does_not_fail_batch(registry, settings):
    agent, sql_client_mock = _make_agent(settings)

    async def _side_effect(agg_id, params, reg):
        if agg_id == "visits_by_object":
            raise RuntimeError("DB connection failed")
        return _ok_result(agg_id)

    sql_client_mock.execute_aggregate = _side_effect

    queries = [
        AggregateQuery(aggregate_id="revenue_by_master", params={}, label="ok"),
        AggregateQuery(aggregate_id="visits_by_object", params={}, label="err"),
    ]
    plan = _make_plan(queries)

    results = await agent.run_multi(plan, registry, sql_client=sql_client_mock)

    assert len(results) == 2
    statuses = {r.label: r.status for r in results}
    assert statuses["ok"] == "ok"
    assert statuses["err"] == "error"


# ── Дополнительно: пустой план возвращает пустой список ──────────────────────


@pytest.mark.asyncio
async def test_empty_plan_returns_empty_list(registry, settings):
    agent, sql_client_mock = _make_agent(settings)
    sql_client_mock.execute_aggregate = AsyncMock()

    plan = _make_plan([])
    results = await agent.run_multi(plan, registry, sql_client=sql_client_mock)

    assert results == []
    sql_client_mock.execute_aggregate.assert_not_called()
