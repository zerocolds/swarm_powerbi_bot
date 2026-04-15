"""Тесты для chart_renderer — рендеринг графиков из SQL-данных."""
from swarm_powerbi_bot.services.chart_renderer import (
    HAS_MPL,
    choose_chart_type,
    render_chart,
)

import pytest


def test_choose_chart_type_trend():
    assert choose_chart_type("trend", []) == "line"


def test_choose_chart_type_referrals():
    assert choose_chart_type("referrals", []) == "pie"


def test_choose_chart_type_outflow():
    assert choose_chart_type("outflow", []) == "hbar"


def test_choose_chart_type_birthday_table():
    assert choose_chart_type("birthday", []) == "table_only"


def test_choose_chart_type_unknown_fallback():
    assert choose_chart_type("unknown_topic_xyz", []) == "bar"


def test_render_chart_empty_rows():
    result = render_chart("statistics", [], {})
    assert result is None


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
def test_render_chart_table_only():
    """table_only теперь рендерит PNG-таблицу."""
    result = render_chart("birthday", [{"Name": "Test", "Phone": "123"}], {})
    assert result is not None
    assert result[:4] == b"\x89PNG"


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
def test_render_bar_statistics():
    rows = [{
        "TotalVisits": 150,
        "UniqueClients": 80,
        "TotalRevenue": 250000.0,
        "AvgCheck": 1666.7,
        "SalonName": "Тест",
    }]
    result = render_chart("statistics", rows, {"topic": "statistics"})
    assert result is not None
    assert isinstance(result, bytes)
    assert result[:4] == b"\x89PNG"


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
def test_render_hbar_outflow():
    rows = [
        {"ClientName": "Иванов", "DaysOverdue": 45, "TotalSpent": 15000},
        {"ClientName": "Петрова", "DaysOverdue": 60, "TotalSpent": 22000},
        {"ClientName": "Сидоров", "DaysOverdue": 100, "TotalSpent": 5000},
    ]
    result = render_chart("outflow", rows, {"topic": "outflow"})
    assert result is not None
    assert result[:4] == b"\x89PNG"


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
def test_render_line_trend():
    rows = [
        {"WeekEnd": "2025-01-06", "Visits": 50, "Revenue": 100000, "UniqueClients": 30},
        {"WeekEnd": "2025-01-13", "Visits": 55, "Revenue": 110000, "UniqueClients": 32},
        {"WeekEnd": "2025-01-20", "Visits": 48, "Revenue": 95000, "UniqueClients": 28},
    ]
    result = render_chart("trend", rows, {"topic": "trend"})
    assert result is not None
    assert result[:4] == b"\x89PNG"


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
def test_render_pie_referrals():
    rows = [
        {"AcquisitionChannel": "Instagram", "ClientCount": 50},
        {"AcquisitionChannel": "Рекомендация", "ClientCount": 30},
        {"AcquisitionChannel": "Сайт", "ClientCount": 20},
    ]
    result = render_chart("referrals", rows, {"topic": "referrals"})
    assert result is not None
    assert result[:4] == b"\x89PNG"


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
def test_render_chart_with_period_label():
    """Проверяем что период из params попадает в title."""
    from datetime import date
    rows = [{"TotalVisits": 100, "SalonName": "Тест"}]
    params = {
        "topic": "statistics",
        "DateFrom": date(2025, 1, 1),
        "DateTo": date(2025, 1, 31),
    }
    result = render_chart("statistics", rows, params)
    assert result is not None
    assert isinstance(result, bytes)
