import asyncio

from swarm_powerbi_bot.agents.planner import PlannerAgent
from swarm_powerbi_bot.models import UserQuestion


def test_planner_extracts_report_and_flags():
    planner = PlannerAgent()
    q = UserQuestion(user_id="1", text="Сравни выручку report:sales/kpi без картинки")

    plan = asyncio.run(planner.run(q))

    assert plan.render_needed is False
    assert plan.sql_needed is True
    assert plan.powerbi_needed is True
    assert plan.render_report_id == "sales/kpi"
    assert "comparison_requested" in plan.notes


def test_planner_detects_topic_outflow():
    planner = PlannerAgent()
    q = UserQuestion(user_id="1", text="Покажи отток клиентов за месяц")

    plan = asyncio.run(planner.run(q))

    assert plan.topic == "outflow"
    assert "topic:outflow" in plan.notes
    assert "period:month" in plan.notes


def test_planner_detects_topic_services():
    planner = PlannerAgent()
    q = UserQuestion(user_id="1", text="Какая выручка и средний чек за неделю?")

    plan = asyncio.run(planner.run(q))

    assert plan.topic == "services"
    assert "period:week" in plan.notes


def test_planner_detects_breakdown_by_master():
    planner = PlannerAgent()
    q = UserQuestion(user_id="1", text="Покажи статистику по мастерам за квартал")

    plan = asyncio.run(planner.run(q))

    assert "breakdown_by_master" in plan.notes
    assert "period:quarter" in plan.notes


def test_planner_detects_trend_and_forecast():
    planner = PlannerAgent()
    q = UserQuestion(user_id="1", text="Покажи тренд и прогноз визитов")

    plan = asyncio.run(planner.run(q))

    assert "trend_requested" in plan.notes
    assert "forecast_requested" in plan.notes


def test_planner_detects_ranking():
    planner = PlannerAgent()
    q = UserQuestion(user_id="1", text="Топ лучших мастеров по выручке")

    plan = asyncio.run(planner.run(q))

    assert "ranking_requested" in plan.notes


def test_planner_fallback_topic():
    planner = PlannerAgent()
    q = UserQuestion(user_id="1", text="Привет, расскажи что нового")

    plan = asyncio.run(planner.run(q))

    assert plan.topic == "statistics"
