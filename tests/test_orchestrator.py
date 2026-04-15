import asyncio

from swarm_powerbi_bot.models import (
    AggregateResult, AnalysisResult, ModelInsight, MultiPlan, Plan,
    RenderedArtifact, SQLInsight, UserQuestion,
)
from swarm_powerbi_bot.orchestrator import SwarmOrchestrator


class DummyPlanner:
    aggregate_registry = None

    async def run(self, question: UserQuestion) -> Plan:
        return Plan(objective=question.text, topic="statistics", sql_needed=True, powerbi_needed=True, render_needed=True)


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
        # All results failed
        return [
            AggregateResult(aggregate_id="clients_outflow", status="error", rows=[]),
            AggregateResult(aggregate_id="clients_outflow", status="error", rows=[]),
        ]


class DummyPlannerWithRegistry(DummyPlanner):
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


class DummyRegistry:
    """Minimal registry stub."""
    pass


class DummyAnalystMulti(DummyAnalyst):
    async def run_multi(self, question, results, plan):
        return AnalysisResult(answer="multi analysis", confidence="medium", diagnostics={})


def test_multi_all_failed_skips_legacy_sql():
    """#4: Если все multi_results failed, legacy SQL НЕ должен вызываться."""
    registry = DummyRegistry()
    sql_spy = DummySQLSpy()
    orchestrator = SwarmOrchestrator(
        planner=DummyPlannerWithRegistry(registry),
        sql_agent=sql_spy,
        powerbi_agent=DummyPBI(),
        render_agent=DummyRender(),
        analyst_agent=DummyAnalystMulti(),
        aggregate_registry=registry,
    )

    result = asyncio.run(orchestrator.handle_question(UserQuestion(user_id="1", text="сравни отток")))
    assert not sql_spy.run_called, "Legacy SQL should NOT be called when all multi_results failed"
    assert result.diagnostics.get("multi_all_failed") == "true"
