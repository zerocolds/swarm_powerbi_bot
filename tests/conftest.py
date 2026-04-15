"""Shared mock classes and fixtures for E2E and orchestrator tests."""
from __future__ import annotations

from swarm_powerbi_bot.models import (
    AggregateResult,
    AnalysisResult,
    ModelInsight,
    MultiPlan,
    Plan,
    RenderedArtifact,
    SQLInsight,
    UserQuestion,
)
from swarm_powerbi_bot.orchestrator import SwarmOrchestrator


# ── Base Dummy classes ──────────────────────────────────────────


class DummyPlanner:
    aggregate_registry = None

    async def run(self, question: UserQuestion) -> Plan:
        return Plan(
            objective=question.text, topic="statistics",
            sql_needed=True, powerbi_needed=True, render_needed=True,
        )


class DummySQL:
    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
        return SQLInsight(rows=[{"kpi": "sales", "value": 100}], summary="sql ok")


class DummyPBI:
    async def run(self, question: UserQuestion, plan: Plan) -> ModelInsight:
        return ModelInsight(metrics={"margin": 0.32}, summary="model ok")


class DummyRender:
    async def run(self, question: UserQuestion, plan: Plan) -> RenderedArtifact:
        _ = question, plan
        return RenderedArtifact(image_bytes=b"png-bytes", source_url="http://report")


class DummyAnalyst:
    async def run(self, question, plan, sql_insight, model_insight, diagnostics, *, has_chart=False):
        _ = question, plan, sql_insight, model_insight, has_chart
        return AnalysisResult(answer="analysis", confidence="high", diagnostics=diagnostics)


# ── MultiPlan-aware mocks ──────────────────────────────────────


class MockRegistry:
    """Minimal AggregateRegistry stub."""

    def get_aggregate(self, agg_id: str):
        return {"id": agg_id, "procedure": "spKDO_Aggregate", "parameters": []}

    def list_aggregates(self):
        return [{"id": "revenue_total"}, {"id": "clients_outflow"}]


class MockPlannerWithRegistry(DummyPlanner):
    def __init__(self, registry=None, *, intent="comparison", topic="clients_outflow", n_queries=2):
        self.aggregate_registry = registry or MockRegistry()
        self._intent = intent
        self._topic = topic
        self._n_queries = n_queries

    async def run_multi(self, question):
        return MultiPlan(
            objective=question.text,
            intent=self._intent,
            queries=[{"aggregate_id": self._topic}] * self._n_queries,
            topic=self._topic,
            render_needed=True,
            notes=["planner_v2:llm"],
        )

    def multi_plan_to_plan(self, multi_plan, question):
        return Plan(
            objective=multi_plan.objective,
            topic=multi_plan.topic,
            notes=list(multi_plan.notes),
        )


class MockSQLMulti(DummySQL):
    """SQL agent that supports run_multi() with configurable results."""

    def __init__(self, results: list[AggregateResult] | None = None):
        self._results = results or [
            AggregateResult(
                aggregate_id="clients_outflow", label="Март 2026",
                group_by="status", status="ok",
                rows=[
                    {"ClientStatus": "Отток", "ClientCount": 20},
                    {"ClientStatus": "Уходящие", "ClientCount": 15},
                ],
            ),
            AggregateResult(
                aggregate_id="clients_outflow", label="Апрель 2026",
                group_by="status", status="ok",
                rows=[
                    {"ClientStatus": "Отток", "ClientCount": 18},
                    {"ClientStatus": "Уходящие", "ClientCount": 12},
                ],
            ),
        ]

    async def run_multi(self, multi_plan, registry, *, logger_=None):
        return self._results


class MockAnalystMulti(DummyAnalyst):
    async def run_multi(self, question, results, plan):
        ok = [r for r in results if r.status == "ok"]
        return AnalysisResult(
            answer=f"Сравнение: {ok[0].label} vs {ok[1].label}\n• Клиенты: +17%",
            confidence="medium",
            diagnostics={},
        )


def build_mock_orchestrator_multi(*, intent="comparison", topic="clients_outflow"):
    """Build orchestrator wired for MultiPlan flow."""
    registry = MockRegistry()
    return SwarmOrchestrator(
        planner=MockPlannerWithRegistry(registry, intent=intent, topic=topic),
        sql_agent=MockSQLMulti(),
        powerbi_agent=DummyPBI(),
        render_agent=DummyRender(),
        analyst_agent=MockAnalystMulti(),
        aggregate_registry=registry,
    )
