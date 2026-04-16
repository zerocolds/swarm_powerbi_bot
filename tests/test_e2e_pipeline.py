"""End-to-end тесты pipeline: вопрос → topic → SQL params → chart → ответ.

Проверяет полную цепочку без обращения к MSSQL/LLM (моки).
"""
import asyncio
from datetime import date

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

from conftest import build_mock_orchestrator_multi

pytestmark = pytest.mark.e2e


# ── Mock агенты с реалистичными данными ──────────────────────

class MockSQL:
    """Возвращает данные как настоящие хранимки — 11 тем (10 из checklist + leaving)."""
    MOCK_DATA = {
        "outflow": [
            {"ClientName": "Козлова Р.", "Phone": "79001111111", "TotalSpent": 8112.6,
             "DaysSinceLastVisit": 275, "DaysOverdue": 240, "TotalVisits": 11,
             "ServicePeriodDays": 35, "SalonName": "Dream"},
            {"ClientName": "Белова Т.", "Phone": "79002222222", "TotalSpent": 57054.0,
             "DaysSinceLastVisit": 283, "DaysOverdue": 238, "TotalVisits": 59,
             "ServicePeriodDays": 45, "SalonName": "Dream"},
        ],
        "statistics": [
            {"TotalVisits": 219, "UniqueClients": 137, "TotalRevenue": 422028.50,
             "AvgCheck": 1954.33, "ActiveMasters": 14, "SalonName": "Dream"},
        ],
        "trend": [
            {"WeekEnd": "2026-03-02", "Visits": 45, "Revenue": 77424, "UniqueClients": 30, "AvgCheck": 1720, "ActiveMasters": 7},
            {"WeekEnd": "2026-03-09", "Visits": 50, "Revenue": 85000, "UniqueClients": 35, "AvgCheck": 1700, "ActiveMasters": 8},
        ],
        "masters": [
            {"MasterName": "Мастер А", "TotalRevenue": 120000, "TotalVisits": 50, "AvgCheck": 2400, "SalonName": "Dream"},
        ],
        "referrals": [
            {"AcquisitionChannel": "Instagram", "ClientCount": 50},
            {"AcquisitionChannel": "Рекомендация", "ClientCount": 30},
        ],
        "birthday": [
            {"ClientName": "Иванова А.", "Phone": "79003333333", "BirthDate": "2000-04-16"},
        ],
        "communications": [
            {"Reason": "outflow", "Result": "Вернулся", "TotalCount": 15},
            {"Reason": "leaving", "Result": "Нет ответа", "TotalCount": 8},
        ],
        "forecast": [
            {"ClientName": "Петрова М.", "ExpectedNextVisit": "2026-04-17", "ServicePeriodDays": 28},
        ],
        "services": [
            {"ServiceName": "Стрижка", "Revenue": 85000, "ServiceCount": 120},
            {"ServiceName": "Окрашивание", "Revenue": 65000, "ServiceCount": 40},
        ],
        "quality": [
            {"ClientName": "Сидоров К.", "DaysOverdue": 5, "TotalVisits": 3, "SalonName": "Dream"},
        ],
        "leaving": [
            {"ClientName": "Нова Е.", "DaysOverdue": 15, "TotalSpent": 12000, "TotalVisits": 7, "SalonName": "Dream"},
        ],
    }

    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
        rows = self.MOCK_DATA.get(plan.topic, [])
        return SQLInsight(
            rows=rows,
            summary=f"SQL вернул {len(rows)} строк по теме «{plan.topic}»",
            topic=plan.topic,
            params={"DateFrom": date(2026, 3, 15), "DateTo": date(2026, 4, 14)},
        )


class MockPBI:
    async def run(self, question, plan):
        return ModelInsight(metrics={}, summary="model skipped")


class MockRender:
    async def run(self, question, plan):
        return None


class MockAnalyst:
    """Возвращает canned output для проверки маршрутизации pipeline.

    Реальную фильтрацию полей и качество формулировок проверяют
    интеграционные тесты в tests/integration/test_real_e2e.py.
    """
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


# ── T004: Comparison / Composition pipeline ─────────────────────

class TestMultiPlanPipeline:
    def test_comparison_pipeline(self):
        """MultiPlan comparison → SwarmResponse с ответом и chart."""
        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="сравни отток за два месяца"),
        ))
        assert result.answer is not None
        assert "Сравнение" in result.answer
        assert result.confidence in ("low", "medium", "high")

    def test_comparison_pipeline_second_question(self):
        """Второй comparison-вопрос через MultiPlan → корректный ответ."""
        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="сравни отток по салонам"),
        ))
        assert result.answer
        assert len(result.answer) > 0

    def test_decomposition_pipeline(self):
        """MultiPlan decomposition → SwarmResponse с multi-result анализом."""
        orch = build_mock_orchestrator_multi(intent="decomposition", topic="revenue_total")
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="почему упала выручка?"),
        ))
        assert result.answer is not None
        assert result.confidence in ("low", "medium", "high")


# ── T005: 10 checklist questions ────────────────────────────────

_CHECKLIST_QUESTIONS = [
    ("отток за месяц", "outflow"),
    ("покажи статистику за неделю", "statistics"),
    ("динамика по неделям", "trend"),
    ("загрузка мастеров", "masters"),
    ("реферальная программа", "referrals"),
    ("именинники на этой неделе", "birthday"),
    ("результаты обзвонов", "communications"),
    ("прогноз визитов", "forecast"),
    ("популярные услуги", "services"),
    ("контроль качества", "quality"),
]


class TestChecklistQuestions:
    @pytest.mark.parametrize("question_text,expected_topic", _CHECKLIST_QUESTIONS)
    def test_10_checklist_questions(self, question_text, expected_topic):
        """Каждый из 10 вопросов чеклиста → non-empty SwarmResponse."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text=question_text),
        ))
        assert result.answer is not None
        assert len(result.answer) > 0
        assert result.topic == expected_topic


# ── T006: Follow-up chains ──────────────────────────────────────

class TestFollowUpChains:
    def test_follow_up_chain(self):
        """Цепочка follow-up: тема сохраняется через last_topic."""
        orch = _build_orchestrator()
        r1 = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert r1.topic == "outflow"

        r2 = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="подробнее", last_topic="outflow"),
        ))
        assert r2.topic == "outflow"

        r3 = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="а по неделям?", last_topic="outflow"),
        ))
        assert r3.topic == "outflow"

    def test_follow_up_to_comparison(self):
        """Follow-up «сравни» с last_topic → comparison через MultiPlan."""
        orch = build_mock_orchestrator_multi(intent="comparison", topic="clients_outflow")
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="сравни по месяцам", last_topic="clients_outflow"),
        ))
        assert result.answer is not None
        assert len(result.answer) > 0


# ── T007: Negative scenarios ────────────────────────────────────

class TestNegativeScenarios:
    def test_negative_sql_injection(self):
        """SQL-инъекция в тексте не ломает pipeline."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="'; DROP TABLE clients; --"),
        ))
        assert result.answer
        assert "sql_error" not in result.diagnostics

    def test_negative_off_topic(self):
        """Вопрос не по теме → всё равно ответ (fallback topic)."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="какая погода в Москве?"),
        ))
        assert result.answer
        assert result.topic  # непустой topic (fallback)

    def test_negative_empty_text(self):
        """Пустой текст запроса → не падаем."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text=""),
        ))
        assert result.answer
        assert result.topic

    def test_negative_no_period(self):
        """KPI-вопрос без указания периода → не падаем."""
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи выручку"),
        ))
        assert result.answer
        assert result.topic

    def test_negative_long_text(self):
        """Очень длинный текст → не падаем."""
        orch = _build_orchestrator()
        long_text = "отток " * 500
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text=long_text),
        ))
        assert result.answer
        assert result.topic == "outflow"


# ── T008: Smoke / fallback quality ──────────────────────────────
# NB: MockAnalyst возвращает canned output — эти тесты проверяют маршрутизацию
# pipeline, а не качество формулировок аналитика. Реальное качество ответов
# (отсутствие сырых SQL-полей, форматирование чисел) проверяют интеграционные
# тесты в tests/integration/test_real_e2e.py.

class TestFallbackQuality:
    def test_outflow_fallback_no_raw_fields(self):
        """Mock pipeline: ответ не содержит сырых SQL-имён.

        NB: MockAnalyst возвращает canned output — реальную фильтрацию
        полей проверяет integration/test_real_e2e::test_e2e_fallback_no_raw_fields.
        """
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        raw_fields = {"DaysSinceLastVisit", "DaysOverdue", "TotalSpent", "ServicePeriodDays", "Phone"}
        for field in raw_fields:
            assert field not in result.answer, f"Сырое поле {field} в ответе"

    def test_statistics_pipeline_returns_correct_topic(self):
        """Mock pipeline: маршрутизация statistics возвращает непустой ответ.

        NB: MockAnalyst возвращает canned output — качество текста проверяют
        интеграционные тесты в tests/integration/test_real_e2e.py.
        """
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи статистику за неделю"),
        ))
        assert result.topic == "statistics"
        assert result.answer
        assert result.confidence in ("low", "medium", "high")

    def test_statistics_pipeline_has_follow_ups(self):
        """Mock pipeline: statistics возвращает follow-up подсказки.

        NB: MockAnalyst возвращает canned output — содержание follow-ups
        проверяют интеграционные тесты в tests/integration/test_real_e2e.py.
        """
        orch = _build_orchestrator()
        result = asyncio.run(orch.handle_question(
            UserQuestion(user_id="1", text="покажи статистику за неделю"),
        ))
        assert result.topic == "statistics"
        assert len(result.follow_ups) > 0
