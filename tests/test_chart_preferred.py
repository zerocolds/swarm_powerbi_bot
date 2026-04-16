"""Тесты для _PREFERRED_VALUE и _pick_label_value() в chart_renderer.

T013 [US3] _PREFERRED_VALUE["services"] == "ServiceCount"
T014 [US3] _PREFERRED_VALUE["masters"] == "TotalRevenue"
T015 [US3] boolean-поле (IsPrimary) пропускается при выборе value axis
"""

from swarm_powerbi_bot.services.chart_renderer import _PREFERRED_VALUE, _pick_label_value


def test_T013_preferred_value_services():
    """_PREFERRED_VALUE["services"] должен быть ServiceCount, не Revenue."""
    assert _PREFERRED_VALUE["services"] == "ServiceCount"


def test_T014_preferred_value_masters():
    """_PREFERRED_VALUE["masters"] должен быть TotalRevenue, не Revenue."""
    assert _PREFERRED_VALUE["masters"] == "TotalRevenue"


def test_T015_boolean_field_skipped():
    """IsPrimary (bool) не должен выбираться как value axis даже если первый числовой."""
    rows = [
        {"MasterName": "Иван", "IsPrimary": True, "ServiceCount": 10}
    ]
    label_col, value_col = _pick_label_value(rows, topic="")
    # boolean-поле IsPrimary должно быть пропущено, value_col = ServiceCount
    assert value_col == "ServiceCount", (
        f"Ожидался ServiceCount, получен '{value_col}'"
    )
    assert label_col == "MasterName"
