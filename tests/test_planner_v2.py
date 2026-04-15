"""T022: Тесты PlannerAgent v2 — одношаговое LLM-планирование с каталогом агрегатов.

Покрывает:
- Mock LLM returns valid JSON → parses into MultiPlan correctly
- Mock LLM returns invalid JSON → graceful fallback (no crash)
- aggregate_id not in catalog whitelist → falls back to TopicRegistry
- Cross-domain query → multiple aggregates in plan
"""
from __future__ import annotations

import textwrap
from unittest.mock import AsyncMock

import pytest

from swarm_powerbi_bot.agents.planner import PlannerAgent
from swarm_powerbi_bot.models import MultiPlan, UserQuestion
from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry
from swarm_powerbi_bot.services.llm_client import LLMClient


# ── Fixtures ──────────────────────────────────────────────────────────────────

CATALOG_YAML = textwrap.dedent("""\
    aggregates:
      - id: revenue_total
        name: Общая выручка
        description: Суммарная выручка за период
        procedure: spKDO_Aggregate
        allowed_group_by:
          - total
          - week
          - month
      - id: outflow_clients
        name: Отток клиентов
        description: Клиенты со статусом outflow
        procedure: spKDO_ClientList
        allowed_group_by:
          - list
          - master
      - id: communications_all
        name: Коммуникации
        description: Все коммуникации по типу звонка
        procedure: spKDO_CommAgg
        allowed_group_by:
          - reason
          - result
          - manager
""")


@pytest.fixture()
def catalog_path(tmp_path):
    p = tmp_path / "aggregate-catalog.yaml"
    p.write_text(CATALOG_YAML, encoding="utf-8")
    return str(p)


@pytest.fixture()
def registry(catalog_path):
    return AggregateRegistry(catalog_path)


def _parsed_or_none(json_text: str | None) -> dict | None:
    """Парсит JSON-строку или возвращает None (имитирует plan_aggregates)."""
    import json
    import re
    if not json_text:
        return None
    m = re.search(r"\{.*\}", json_text, re.DOTALL)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if "queries" not in data:
        return None
    return data


def _make_planner(llm_json: str | None, registry: AggregateRegistry) -> PlannerAgent:
    from swarm_powerbi_bot.config import Settings
    llm = LLMClient(Settings())
    # Mock plan_aggregates directly — bypasses ollama_api_key check
    llm.plan_aggregates = AsyncMock(return_value=_parsed_or_none(llm_json))
    return PlannerAgent(llm_client=llm, aggregate_registry=registry)


# ── T022-1: Valid JSON → MultiPlan ───────────────────────────────────────────

class TestValidJsonToMultiPlan:
    """Mock LLM returns valid JSON → parses into MultiPlan correctly."""

    def test_single_aggregate_returns_multiplan(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [
                {"aggregate_id": "revenue_total", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15", "group_by": "total"}, "label": "Выручка за период"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="Покажи выручку за апрель")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))

        assert isinstance(plan, MultiPlan)
        assert plan.intent == "single"
        assert len(plan.queries) == 1
        assert plan.queries[0].aggregate_id == "revenue_total"
        assert plan.queries[0].label == "Выручка за период"

    def test_multiplan_objective_set_from_question(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "revenue_total", "params": {}, "label": "Revenue"}],
            "topic": "statistics",
            "render_needed": false
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="общая выручка")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert plan.objective == "общая выручка"

    def test_multiplan_render_needed_false(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "outflow_clients", "params": {}, "label": "Outflow"}],
            "topic": "outflow",
            "render_needed": false
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="отток без картинки")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert plan.render_needed is False

    def test_multiplan_topic_preserved(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "outflow_clients", "params": {}, "label": "Отток"}],
            "topic": "outflow",
            "render_needed": true
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="отток")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert plan.topic == "outflow"

    def test_llm_note_added_on_success(self, registry):
        valid_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "revenue_total", "params": {}, "label": "X"}],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(valid_json, registry)
        q = UserQuestion(user_id="1", text="статистика")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert "planner_v2:llm" in plan.notes


# ── T022-2: Invalid JSON → graceful fallback ──────────────────────────────────

class TestInvalidJsonFallback:
    """Mock LLM returns invalid JSON → graceful fallback (no crash)."""

    def test_invalid_json_returns_fallback_multiplan(self, registry):
        planner = _make_planner("это не JSON, а просто текст", registry)
        q = UserQuestion(user_id="1", text="отток за месяц")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)
        assert "planner_v2:keyword" in plan.notes

    def test_empty_llm_response_falls_back(self, registry):
        planner = _make_planner(None, registry)
        q = UserQuestion(user_id="1", text="покажи статистику")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)
        assert "planner_v2:keyword" in plan.notes

    def test_json_with_no_queries_array_falls_back(self, registry):
        planner = _make_planner('{"intent": "single", "topic": "statistics"}', registry)
        q = UserQuestion(user_id="1", text="что-то")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)

    def test_broken_json_no_exception(self, registry):
        planner = _make_planner("{broken json[[[", registry)
        q = UserQuestion(user_id="1", text="выручка")
        import asyncio
        # Must not raise
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)

    def test_null_llm_response_no_exception(self, registry):
        planner = _make_planner("", registry)
        q = UserQuestion(user_id="1", text="мастера")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)


# ── T022-3: aggregate_id not in whitelist → TopicRegistry fallback ────────────

class TestAggregateIdNotInWhitelist:
    """Если LLM вернул aggregate_id не из каталога → fallback на TopicRegistry."""

    def test_unknown_aggregate_id_triggers_fallback(self, registry):
        bad_json = """{
            "intent": "single",
            "queries": [{"aggregate_id": "not_in_catalog", "params": {}, "label": "X"}],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(bad_json, registry)
        q = UserQuestion(user_id="1", text="отток")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert "planner_v2:keyword" in plan.notes

    def test_any_invalid_aggregate_id_triggers_fallback(self, registry):
        """Если ЛЮБОЙ aggregate_id неверный — весь план → fallback."""
        mixed_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total", "params": {}, "label": "OK"},
                {"aggregate_id": "sql_injection_here", "params": {}, "label": "Bad"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(mixed_json, registry)
        q = UserQuestion(user_id="1", text="сравни выручку")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert "planner_v2:keyword" in plan.notes

    def test_empty_queries_array_fallback(self, registry):
        planner = _make_planner('{"intent": "single", "queries": [], "topic": "statistics", "render_needed": true}', registry)
        q = UserQuestion(user_id="1", text="что-то")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert "planner_v2:keyword" in plan.notes


# ── T022-4: Cross-domain query → multiple aggregates ─────────────────────────

class TestCrossDomainMultipleAggregates:
    """Cross-domain вопрос → несколько агрегатов в плане."""

    def test_two_valid_aggregates(self, registry):
        multi_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15"}, "label": "Выручка"},
                {"aggregate_id": "outflow_clients", "params": {"date_from": "2026-04-01", "date_to": "2026-04-15"}, "label": "Отток"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(multi_json, registry)
        q = UserQuestion(user_id="1", text="покажи выручку и отток")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert isinstance(plan, MultiPlan)
        assert plan.intent == "comparison"
        assert len(plan.queries) == 2
        ids = {aq.aggregate_id for aq in plan.queries}
        assert ids == {"revenue_total", "outflow_clients"}
        assert "planner_v2:llm" in plan.notes

    def test_three_aggregates_cross_domain(self, registry):
        multi_json = """{
            "intent": "decomposition",
            "queries": [
                {"aggregate_id": "revenue_total", "params": {}, "label": "Выручка"},
                {"aggregate_id": "outflow_clients", "params": {}, "label": "Отток"},
                {"aggregate_id": "communications_all", "params": {}, "label": "Коммуникации"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(multi_json, registry)
        q = UserQuestion(user_id="1", text="полный дашборд: выручка, отток и коммуникации")
        import asyncio
        plan = asyncio.run(planner.run_multi(q))
        assert len(plan.queries) == 3
        assert plan.intent == "decomposition"
