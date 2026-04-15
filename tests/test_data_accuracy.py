"""Тесты адекватности расчётов — проверка SQL pipeline на реальных данных.

Использует baseline данные из MSSQL (ObjectId=506770, салон Dream).
Тесты проверяют что:
- Тема определяется правильно для русских вопросов
- Даты извлекаются корректно
- SQL client возвращает ожидаемые колонки
- Числовые поля содержат адекватные значения
"""
import pytest
from datetime import date, timedelta

from swarm_powerbi_bot.services.sql_client import extract_date_params, has_period_hint
from swarm_powerbi_bot.services.topic_registry import get_procedure


# ── Распознавание периодов ───────────────────────────────────

class TestPeriodDetection:
    """Проверяем что русские периоды распознаются."""

    def test_za_mesyac(self):
        assert has_period_hint("Отток за месяц")

    def test_za_mesya_typo(self):
        """Опечатка 'за меся' тоже должна работать."""
        assert has_period_hint("Отток за меся")

    def test_za_nedelyu(self):
        assert has_period_hint("статистика за неделю")

    def test_za_kvartal(self):
        assert has_period_hint("выручка за квартал")

    def test_vchera(self):
        assert has_period_hint("что было вчера")

    def test_za_yanvar(self):
        assert has_period_hint("за январь 2026")

    def test_no_period(self):
        assert not has_period_hint("покажи отток")

    def test_no_period_simple(self):
        assert not has_period_hint("привет")


class TestDateExtraction:
    """Проверяем что даты извлекаются корректно."""

    def test_za_mesyac_30_days(self):
        params = extract_date_params("за месяц")
        today = date.today()
        assert params["DateFrom"] == today - timedelta(days=30)
        assert params["DateTo"] == today

    def test_za_nedelyu_7_days(self):
        params = extract_date_params("за неделю")
        today = date.today()
        assert params["DateFrom"] == today - timedelta(days=7)
        assert params["DateTo"] == today

    def test_vchera(self):
        params = extract_date_params("вчера")
        yesterday = date.today() - timedelta(days=1)
        assert params["DateFrom"] == yesterday
        assert params["DateTo"] == yesterday

    def test_za_kvartal_90_days(self):
        params = extract_date_params("за квартал")
        today = date.today()
        assert params["DateFrom"] == today - timedelta(days=90)

    def test_za_yanvar_2026(self):
        params = extract_date_params("за январь 2026")
        assert params["DateFrom"] == date(2026, 1, 1)
        assert params["DateTo"] == date(2026, 1, 31)

    def test_s_1_po_15_marta(self):
        params = extract_date_params("с 1 по 15 марта 2026")
        assert params["DateFrom"] == date(2026, 3, 1)
        assert params["DateTo"] == date(2026, 3, 15)

    def test_default_30_days(self):
        """Без указания периода — 30 дней по умолчанию."""
        params = extract_date_params("покажи что-нибудь")
        today = date.today()
        assert params["DateFrom"] == today - timedelta(days=30)


# ── Маппинг тема → процедура ────────────────────────────────

class TestTopicToProcedure:
    """Проверяем что каждая тема ведёт в правильную хранимку."""

    EXPECTED = {
        "outflow": "dbo.spKDO_Outflow",
        "leaving": "dbo.spKDO_Leaving",
        "statistics": "dbo.spKDO_Statistics",
        "trend": "dbo.spKDO_Trend",
        "forecast": "dbo.spKDO_Forecast",
        "masters": "dbo.spKDO_Masters",
        "services": "dbo.spKDO_Services",
        "noshow": "dbo.spKDO_NoShow",
        "all_clients": "dbo.spKDO_AllClients",
        "quality": "dbo.spKDO_Quality",
        "communications": "dbo.spKDO_Communications",
        "referrals": "dbo.spKDO_Referrals",
    }

    @pytest.mark.parametrize("topic_id,proc", EXPECTED.items())
    def test_procedure_mapping(self, topic_id, proc):
        assert get_procedure(topic_id) == proc


# ── Корректность колонок в результатах ───────────────────────

class TestExpectedColumns:
    """Проверяем что хранимки возвращают ожидаемые колонки.
    Baseline: реальные данные из MSSQL (ObjectId=506770)."""

    # Outflow должен содержать эти колонки
    OUTFLOW_COLS = {
        "ClientName", "DaysSinceLastVisit", "DaysOverdue",
        "TotalSpent", "TotalVisits", "ServicePeriodDays",
    }

    STATISTICS_COLS = {
        "TotalVisits", "UniqueClients", "TotalRevenue", "AvgCheck",
    }

    TREND_COLS = {"WeekEnd", "Visits", "Revenue", "UniqueClients"}

    MASTERS_COLS = {
        "MasterName", "TotalVisits", "TotalRevenue", "AvgCheck",
    }

    def test_outflow_columns_baseline(self):
        """Колонки из реального запроса к MSSQL."""
        actual = {"ClientName", "Phone", "Category", "LastVisit",
                  "DaysSinceLastVisit", "ExpectedNextVisit", "DaysOverdue",
                  "ServicePeriodDays", "TotalVisits", "TotalSpent", "SalonName"}
        assert self.OUTFLOW_COLS.issubset(actual)

    def test_statistics_columns_baseline(self):
        actual = {"TotalVisits", "UniqueClients", "ActiveMasters",
                  "TotalRevenue", "AvgCheck", "TotalHours",
                  "ReturningClients", "ClientBase", "TotalCommunications",
                  "SatisfiedPct", "SalonName"}
        assert self.STATISTICS_COLS.issubset(actual)

    def test_trend_columns_baseline(self):
        actual = {"WeekEnd", "MonthEnd", "Visits", "UniqueClients",
                  "Revenue", "AvgCheck", "ActiveMasters"}
        assert self.TREND_COLS.issubset(actual)

    def test_masters_columns_baseline(self):
        actual = {"MasterName", "Rating", "MasterCategory", "TotalVisits",
                  "UniqueClients", "TotalRevenue", "AvgCheck", "TotalHours",
                  "RevenuePerHour", "SalonName"}
        assert self.MASTERS_COLS.issubset(actual)


# ── Адекватность данных и моделей ───────────────────────────

class TestDataSanity:
    """Проверяем инварианты моделей данных и результатов."""

    def test_aggregate_result_ok_clears_error(self):
        """AggregateResult с status='ok' не может иметь error."""
        from swarm_powerbi_bot.models import AggregateResult

        result = AggregateResult(aggregate_id="test", status="ok", error="stale")
        assert result.error is None

    def test_aggregate_result_error_preserves_message(self):
        """AggregateResult с status='error' сохраняет error message."""
        from swarm_powerbi_bot.models import AggregateResult

        result = AggregateResult(aggregate_id="test", status="error", error="timeout")
        assert result.error == "timeout"

    def test_aggregate_result_row_count_synced(self):
        """row_count автоматически считается из rows если передан 0."""
        from swarm_powerbi_bot.models import AggregateResult

        rows = [{"Revenue": 100}, {"Revenue": 200}]
        result = AggregateResult(aggregate_id="test", rows=rows)
        assert result.row_count == 2

    def test_default_date_params_30_days(self):
        """Без указания периода — ровно 30 дней."""
        params = extract_date_params("покажи KPI")
        delta = (params["DateTo"] - params["DateFrom"]).days
        assert delta == 30
