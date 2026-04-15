import asyncio

from swarm_powerbi_bot.models import AnalysisResult, ModelInsight, Plan, RenderedArtifact, SQLInsight, UserQuestion
from swarm_powerbi_bot.orchestrator import SwarmOrchestrator


class DummyPlanner:
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
