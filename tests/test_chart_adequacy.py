"""Тесты адекватности графиков — правильный тип и оси для каждой темы.

Проверяет что:
- Для каждой темы выбирается осмысленный тип графика
- Value-колонка выбирается адекватно (не DaysSinceLastVisit для оттока)
- Таблицы рендерятся как PNG (не None)
- Пустые данные не ломают рендерер
"""
import pytest

from swarm_powerbi_bot.services.chart_renderer import (
    HAS_MPL,
    _pick_label_value,
    choose_chart_type,
    render_chart,
)


# ── Тип графика по теме ──────────────────────────────────────

class TestChartTypeSelection:
    """Каждая тема → осмысленный тип графика."""

    def test_outflow_hbar(self):
        assert choose_chart_type("outflow", []) == "hbar"

    def test_trend_line(self):
        assert choose_chart_type("trend", []) == "line"

    def test_referrals_pie(self):
        assert choose_chart_type("referrals", []) == "pie"

    def test_statistics_bar(self):
        assert choose_chart_type("statistics", []) == "bar"

    def test_birthday_table(self):
        assert choose_chart_type("birthday", []) == "table_only"

    def test_masters_hbar(self):
        assert choose_chart_type("masters", []) == "hbar"


# ── Value-колонка: адекватный выбор ──────────────────────────

class TestValueColumnSelection:
    """Для оттока показываем TotalSpent (₽), а не DaysSinceLastVisit."""

    OUTFLOW_ROW = {
        "ClientName": "Иванов",
        "DaysSinceLastVisit": 270,
        "DaysOverdue": 240,
        "ServicePeriodDays": 30,
        "TotalVisits": 15,
        "TotalSpent": 45000.0,
    }

    def test_outflow_shows_total_spent(self):
        """Отток: value = TotalSpent, не DaysSinceLastVisit."""
        _, value_col = _pick_label_value([self.OUTFLOW_ROW], topic="outflow")
        assert value_col == "TotalSpent"

    def test_outflow_label_is_client_name(self):
        """Отток: label = ClientName."""
        label_col, _ = _pick_label_value([self.OUTFLOW_ROW], topic="outflow")
        assert label_col == "ClientName"

    def test_masters_shows_revenue(self):
        row = {"MasterName": "Мастер А", "TotalVisits": 50, "Revenue": 120000}
        _, value_col = _pick_label_value([row], topic="masters")
        assert value_col == "Revenue"

    def test_leaving_shows_total_spent(self):
        row = {"ClientName": "Клиент", "DaysOverdue": 15, "TotalSpent": 8000}
        _, value_col = _pick_label_value([row], topic="leaving")
        assert value_col == "TotalSpent"

    def test_no_topic_skips_days_columns(self):
        """Без темы: DaysSinceLastVisit пропускается."""
        row = {"ClientName": "X", "DaysSinceLastVisit": 100, "TotalVisits": 5}
        _, value_col = _pick_label_value([row], topic="")
        assert value_col == "TotalVisits"


# ── Рендеринг с реальными данными ────────────────────────────

@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestChartRenderingWithRealData:
    """Рендерим графики из данных максимально приближённых к реальным."""

    def test_outflow_chart_is_png(self):
        rows = [
            {"ClientName": "Козлова Р.", "TotalSpent": 8112.6, "DaysSinceLastVisit": 275},
            {"ClientName": "Семенова П.", "TotalSpent": 5430.0, "DaysSinceLastVisit": 285},
            {"ClientName": "Белова Т.", "TotalSpent": 57054.0, "DaysSinceLastVisit": 283},
        ]
        result = render_chart("outflow", rows, {"topic": "outflow"})
        assert result is not None
        assert result[:4] == b"\x89PNG"

    def test_statistics_single_row_chart(self):
        row = {
            "TotalVisits": 219, "UniqueClients": 137,
            "TotalRevenue": 422028.0, "AvgCheck": 1954.0,
            "ActiveMasters": 14, "SalonName": "Dream",
        }
        result = render_chart("statistics", [row], {"topic": "statistics"})
        assert result is not None
        assert result[:4] == b"\x89PNG"

    def test_trend_line_chart(self):
        rows = [
            {"WeekEnd": "2026-01-05", "Visits": 45, "Revenue": 77424, "UniqueClients": 30},
            {"WeekEnd": "2026-01-12", "Visits": 50, "Revenue": 85000, "UniqueClients": 35},
            {"WeekEnd": "2026-01-19", "Visits": 38, "Revenue": 67258, "UniqueClients": 28},
        ]
        result = render_chart("trend", rows, {"topic": "trend"})
        assert result is not None
        assert result[:4] == b"\x89PNG"

    def test_masters_hbar_chart(self):
        rows = [
            {"MasterName": "Мастер А", "TotalRevenue": 120000, "Rating": 4.8},
            {"MasterName": "Мастер Б", "TotalRevenue": 95000, "Rating": 4.5},
        ]
        result = render_chart("masters", rows, {"topic": "masters"})
        assert result is not None

    def test_birthday_renders_table(self):
        """birthday = table_only, теперь рендерит PNG-таблицу."""
        rows = [
            {"ClientName": "Иванов И.", "Phone": "79001234567", "Birthday": "2026-04-15"},
        ]
        result = render_chart("birthday", rows, {"topic": "birthday"})
        assert result is not None
        assert result[:4] == b"\x89PNG"

    def test_empty_rows_returns_none(self):
        result = render_chart("outflow", [], {})
        assert result is None


# ── Пограничные случаи рендеринга ────────────────────────────

@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestChartEdgeCases:
    def test_single_row_hbar(self):
        """Один клиент в оттоке — не должен ломаться."""
        rows = [{"ClientName": "Один", "TotalSpent": 5000}]
        result = render_chart("outflow", rows, {"topic": "outflow"})
        assert result is not None

    def test_all_zero_values(self):
        rows = [{"ClientName": "Ноль", "TotalSpent": 0, "TotalVisits": 0}]
        result = render_chart("outflow", rows, {"topic": "outflow"})
        assert result is not None

    def test_very_long_names(self):
        rows = [{"ClientName": "А" * 50, "TotalSpent": 1000}]
        result = render_chart("outflow", rows, {"topic": "outflow"})
        assert result is not None

    def test_none_values_in_data(self):
        rows = [{"ClientName": "Test", "Category": None, "TotalSpent": 500}]
        result = render_chart("outflow", rows, {"topic": "outflow"})
        assert result is not None
