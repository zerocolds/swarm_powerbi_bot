import asyncio

from swarm_powerbi_bot.models import (
    AggregateResult, MultiPlan, Plan, UserQuestion,
)
from swarm_powerbi_bot.orchestrator import SwarmOrchestrator

from conftest import (
    DummyAnalyst, DummyPBI, DummyPlanner, DummyRender, DummySQL,
    MockAnalystMulti, MockRegistry,
)


def test_orchestrator_happy_path():
    orchestrator = SwarmOrchestrator(
        planner=DummyPlanner(),
        sql_agent=DummySQL(),
        powerbi_agent=DummyPBI(),
        render_agent=DummyRender(),
        analyst_agent=DummyAnalyst(),
    )

    result = asyncio.run(orchestrator.handle_question(UserQuestion(user_id="1", text="test")))
    assert result.answer == "analysis"
    # Графики: matplotlib генерирует PNG из SQL данных, или Power BI рендер
    assert result.image is not None
    assert result.confidence == "high"


# ── #4: multi_all_failed → legacy SQL не вызывается ──────────


class DummySQLSpy(DummySQL):
    """SQL agent that records whether run() was called."""
    def __init__(self):
        self.run_called = False

    async def run(self, question, plan):
        self.run_called = True
        return await super().run(question, plan)

    async def run_multi(self, multi_plan, registry, *, logger_=None):
        return [
            AggregateResult(aggregate_id="clients_outflow", status="error", rows=[]),
            AggregateResult(aggregate_id="clients_outflow", status="error", rows=[]),
        ]


class DummyPlannerWithRegistryFail(DummyPlanner):
    def __init__(self, registry):
        self.aggregate_registry = registry

    async def run_multi(self, question):
        return MultiPlan(
            objective="сравни",
            intent="comparison",
            queries=[{"aggregate_id": "clients_outflow"}],
            topic="clients_outflow",
            render_needed=True,
            notes=["planner_v2:llm"],
        )

    def multi_plan_to_plan(self, multi_plan, question):
        return Plan(
            objective=multi_plan.objective,
            topic=multi_plan.topic,
            notes=list(multi_plan.notes),
        )


def test_multi_all_failed_skips_legacy_sql():
    """#4: Если все multi_results failed, legacy SQL НЕ должен вызываться."""
    registry = MockRegistry()
    sql_spy = DummySQLSpy()
    orchestrator = SwarmOrchestrator(
        planner=DummyPlannerWithRegistryFail(registry),
        sql_agent=sql_spy,
        powerbi_agent=DummyPBI(),
        render_agent=DummyRender(),
        analyst_agent=MockAnalystMulti(),
        aggregate_registry=registry,
    )

    result = asyncio.run(orchestrator.handle_question(UserQuestion(user_id="1", text="сравни отток")))
    assert not sql_spy.run_called, "Legacy SQL should NOT be called when all multi_results failed"
    assert result.diagnostics.get("multi_all_failed") == "true"
