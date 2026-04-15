"""End-to-end тесты pipeline: вопрос → topic → SQL params → chart → ответ.

Проверяет полную цепочку без обращения к MSSQL/LLM (моки).
"""
import asyncio

import pytest

from swarm_powerbi_bot.agents.planner import PlannerAgent
from swarm_powerbi_bot.models import (
    AnalysisResult,
    ModelInsight,
    Plan,
    SQLInsight,
    UserQuestion,
)
from swarm_powerbi_bot.orchestrator import SwarmOrchestrator
from swarm_powerbi_bot.services.chart_renderer import HAS_MPL


# ── Mock агенты с реалистичными данными ──────────────────────

class MockSQL:
    """Возвращает данные как настоящие хранимки."""
    MOCK_DATA = {
        "outflow": [
            {"ClientName": "Козлова Р.", "TotalSpent": 8112.6, "DaysSinceLastVisit": 275,
             "DaysOverdue": 240, "TotalVisits": 11, "ServicePeriodDays": 35, "SalonName": "Dream"},
            {"ClientName": "Белова Т.", "TotalSpent": 57054.0, "DaysSinceLastVisit": 283,
             "DaysOverdue": 238, "TotalVisits": 59, "ServicePeriodDays": 45, "SalonName": "Dream"},
        ],
        "statistics": [
            {"TotalVisits": 219, "UniqueClients": 137, "TotalRevenue": 422028.0,
             "AvgCheck": 1954.0, "ActiveMasters": 14, "SalonName": "Dream"},
        ],
        "trend": [
            {"WeekEnd": "2026-03-02", "Visits": 45, "Revenue": 77424, "UniqueClients": 30, "AvgCheck": 1720, "ActiveMasters": 7},
            {"WeekEnd": "2026-03-09", "Visits": 50, "Revenue": 85000, "UniqueClients": 35, "AvgCheck": 1700, "ActiveMasters": 8},
        ],
        "masters": [
            {"MasterName": "Мастер А", "TotalRevenue": 120000, "TotalVisits": 50, "AvgCheck": 2400, "SalonName": "Dream"},
        ],
    }

    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
        rows = self.MOCK_DATA.get(plan.topic, [])
        return SQLInsight(
            rows=rows,
            summary=f"SQL вернул {len(rows)} строк по теме «{plan.topic}»",
            topic=plan.topic,
            params={"DateFrom": "2026-03-15", "DateTo": "2026-04-14"},
        )


class MockPBI:
    async def run(self, question, plan):
        return ModelInsight(metrics={}, summary="model skipped")


class MockRender:
    async def run(self, question, plan):
        return None


class MockAnalyst:
    async def run(self, question, plan, sql_insight, model_insight, diagnostics, *, has_chart=False):
        return AnalysisResult(
            answer=f"Тема: {plan.topic}, строк: {len(sql_insight.rows)}",
            confidence="medium",
            follow_ups=["follow1"],
        )


def _build_orchestrator():
    return SwarmOrchestrator(
        planner=PlannerAgent(),
        sql_agent=MockSQL(),
        powerbi_agent=MockPBI(),
        render_agent=MockRender(),
        analyst_agent=MockAnalyst(),
    )


# ── E2E тесты ────────────────────────────────────────────────

class TestE2EPipeline:
    def test_outflow_question(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert "outflow" in result.answer
        assert result.topic == "outflow"

    def test_statistics_question(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи статистику за неделю"),
        ))
        assert "statistics" in result.answer
        assert result.topic == "statistics"

    def test_masters_question(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="загрузка мастеров"),
        ))
        assert "masters" in result.answer

    def test_followup_keeps_topic(self):
        """Follow-up вопрос сохраняет тему."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="подробнее по неделям", last_topic="outflow"),
        ))
        assert result.topic == "outflow"

    def test_response_has_follow_ups(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert len(result.follow_ups) > 0

    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
    def test_outflow_generates_chart(self):
        """Отток с данными → matplotlib-график."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert result.image is not None
        assert result.image[:4] == b"\x89PNG"

    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
    def test_trend_generates_line_chart(self):
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи тренд за квартал"),
        ))
        assert result.image is not None

    def test_empty_data_no_crash(self):
        """Если SQL вернул 0 строк — не падаем."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи именинников"),
        ))
        assert result.answer is not None


# ── Planner тесты ────────────────────────────────────────────

class TestPlannerNotes:
    def test_comparison_note(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="сравни отток по неделям"),
        ))
        assert "comparison_requested" in plan.notes

    def test_period_note_week(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="статистика за неделю"),
        ))
        assert "period:week" in plan.notes

    def test_breakdown_by_master(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="выручка по мастерам"),
        ))
        assert "breakdown_by_master" in plan.notes
