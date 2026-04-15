"""T007: Тесты fallback-текстов AnalystAgent — перевод полей, дельты, topic formatters."""
from __future__ import annotations

from unittest.mock import AsyncMock

from swarm_powerbi_bot.agents.analyst import AnalystAgent
from swarm_powerbi_bot.config import Settings
from swarm_powerbi_bot.models import AggregateResult, MultiPlan
from swarm_powerbi_bot.services.llm_client import LLMClient


def _make_analyst() -> AnalystAgent:
    llm = LLMClient(Settings())
    llm.synthesize = AsyncMock(side_effect=lambda sys, usr, fb: fb)  # always return fallback
    return AnalystAgent(llm_client=llm)


# ── _fallback_multi: comparison с дельтами ──────────────────────


class TestFallbackMultiComparison:
    """#7: _fallback_multi для comparison показывает метрики + дельты."""

    def test_comparison_shows_metrics_and_deltas(self):
        analyst = _make_analyst()
        ok_results = [
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
        plan = MultiPlan(
            objective="сравни", intent="comparison",
            queries=[], topic="clients_outflow",
            render_needed=True,
        )
        text = analyst._fallback_multi("сравни", ok_results, plan, 0)
        assert "Март 2026" in text
        assert "Апрель 2026" in text
        assert "%" in text  # дельта

    def test_comparison_no_raw_row_count(self):
        """Не должно быть 'N записей' в comparison."""
        analyst = _make_analyst()
        ok_results = [
            AggregateResult(
                aggregate_id="r", label="A", status="ok",
                rows=[{"Revenue": 100000}],
            ),
            AggregateResult(
                aggregate_id="r", label="B", status="ok",
                rows=[{"Revenue": 90000}],
            ),
        ]
        plan = MultiPlan(
            objective="", intent="comparison",
            queries=[], topic="r", render_needed=True,
        )
        text = analyst._fallback_multi("", ok_results, plan, 0)
        assert "записей" not in text


# ── _fallback_summary: перевод полей ────────────────────────────


class TestFallbackSummaryTranslation:
    """#5: _fallback_summary переводит имена полей и скрывает Phone."""

    def test_outflow_no_raw_fields(self):
        from swarm_powerbi_bot.models import Plan, SQLInsight, ModelInsight, UserQuestion
        analyst = _make_analyst()
        rows = [
            {"ClientName": "Иванов", "Phone": "79001234567",
             "DaysOverdue": 45, "TotalSpent": 15000, "TotalVisits": 10,
             "DaysSinceLastVisit": 60, "SalonName": "Тест"},
            {"ClientName": "Петров", "Phone": "79007654321",
             "DaysOverdue": 90, "TotalSpent": 22000, "TotalVisits": 20,
             "DaysSinceLastVisit": 100, "SalonName": "Тест"},
        ]
        q = UserQuestion(user_id="1", text="отток")
        plan = Plan(objective="отток", topic="outflow")
        sql = SQLInsight(rows=rows, summary="ok")
        model = ModelInsight(metrics={}, summary="")
        text = analyst._fallback_summary(q, plan, sql, model, {})
        # Не должно быть raw field names
        assert "ClientName" not in text
        assert "Phone" not in text
        assert "DaysOverdue" not in text
        # Должна быть агрегация
        assert "клиентов: 2" in text.lower() or "клиентов" in text.lower()
        assert "45" in text  # min overdue
        assert "90" in text  # max overdue

    def test_statistics_shows_russian_labels(self):
        from swarm_powerbi_bot.models import Plan, SQLInsight, ModelInsight, UserQuestion
        analyst = _make_analyst()
        rows = [{"Visits": 150, "UniqueClients": 80, "Revenue": 250000.0, "AvgCheck": 1666.0}]
        q = UserQuestion(user_id="1", text="статистика")
        plan = Plan(objective="статистика", topic="statistics")
        sql = SQLInsight(rows=rows, summary="ok")
        model = ModelInsight(metrics={}, summary="")
        text = analyst._fallback_summary(q, plan, sql, model, {})
        assert "Визиты" in text
        assert "Выручка" in text
        assert "Visits" not in text  # no raw field names
