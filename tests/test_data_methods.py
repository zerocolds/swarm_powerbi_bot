from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from swarm_powerbi_bot.services.data_methods import (
    DATA_METHODS,
    _AGGREGATE_COLUMNS,
    get_clients_outflow,
    get_comm_all_by_reason,
    get_comm_noshow_by_manager,
    get_revenue_by_master,
    get_revenue_by_salon,
    get_revenue_total,
)

_EXPECTED_KEYS = {
    "revenue_total",
    "revenue_by_week",
    "revenue_by_month",
    "revenue_by_master",
    "revenue_by_service",
    "revenue_by_salon",
    "revenue_by_channel",
    "clients_outflow",
    "clients_leaving",
    "clients_forecast",
    "clients_noshow",
    "clients_quality",
    "clients_birthday",
    "clients_all",
    "comm_all_by_reason",
    "comm_all_by_result",
    "comm_all_by_manager",
    "comm_all_list",
    "comm_outflow_by_reason",
    "comm_leaving_by_result",
    "comm_forecast_by_result",
    "comm_noshow_by_manager",
    "comm_quality_by_result",
    "comm_birthday_by_result",
    "comm_waitlist_by_manager",
    "comm_opz_by_result",
}

_CONN = "Driver={ODBC Driver 17 for SQL Server};Server=test;Database=test;"
_D_FROM = date(2026, 3, 1)
_D_TO = date(2026, 3, 31)


# ── Fixture ───────────────────────────────────────────────────────────────────


@pytest.fixture()
def mock_pyodbc_cursor():
    """Yields (mock_pyodbc, mock_cursor) with pyodbc patched in data_methods module."""
    mock_cursor = MagicMock()
    mock_cursor.description = None
    mock_cursor.fetchall.return_value = []

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_pyodbc = MagicMock()
    mock_pyodbc.connect.return_value = mock_conn

    with patch("swarm_powerbi_bot.services.data_methods.pyodbc", mock_pyodbc):
        yield mock_pyodbc, mock_cursor


# ── Registry ─────────────────────────────────────────────────────────────────


def test_data_method_registry_complete():
    assert set(DATA_METHODS.keys()) == _EXPECTED_KEYS


def test_all_aggregate_columns_defined():
    assert set(_AGGREGATE_COLUMNS.keys()) == _EXPECTED_KEYS


def test_data_methods_are_callable():
    for name, fn in DATA_METHODS.items():
        assert callable(fn), f"DATA_METHODS[{name!r}] is not callable"


# ── Empty-result invariant ────────────────────────────────────────────────────


def test_empty_result_returns_empty_dataframe(mock_pyodbc_cursor):
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = None
    mock_cursor.fetchall.return_value = []

    result = get_revenue_total(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_empty_result_has_correct_columns(mock_pyodbc_cursor):
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("Revenue",), ("Visits",)]
    mock_cursor.fetchall.return_value = []

    result = get_revenue_total(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
    assert isinstance(result.columns.tolist(), list)


# ── SQL shape tests ───────────────────────────────────────────────────────────


def test_get_revenue_total_sql_shape(mock_pyodbc_cursor):
    """get_revenue_total must call spKDO_Aggregate with @GroupBy=? = 'total'."""
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("Revenue",), ("Visits",)]
    mock_cursor.fetchall.return_value = [(100000.0, 50)]

    result = get_revenue_total(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1

    call_args = mock_cursor.execute.call_args
    sql: str = call_args[0][0]
    args: list = list(call_args[0][1])

    assert "spKDO_Aggregate" in sql
    assert "@DateFrom=?" in sql
    assert "@DateTo=?" in sql
    assert "@ObjectId=?" in sql
    assert "@GroupBy=?" in sql
    assert "@Top=?" in sql
    assert _D_FROM in args
    assert _D_TO in args
    assert 12345 in args
    assert "total" in args


def test_get_revenue_by_master_uses_group_by_master(mock_pyodbc_cursor):
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("MasterName",), ("Revenue",)]
    mock_cursor.fetchall.return_value = [("Иванова А.", 50000.0)]

    get_revenue_by_master(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=99,
    )

    sql = mock_cursor.execute.call_args[0][0]
    args = list(mock_cursor.execute.call_args[0][1])
    assert "spKDO_Aggregate" in sql
    assert "master" in args


def test_get_clients_outflow_uses_filter(mock_pyodbc_cursor):
    """get_clients_outflow must call spKDO_ClientList with @Filter=? = 'outflow'."""
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("ClientName",), ("DaysOverdue",)]
    mock_cursor.fetchall.return_value = [("Иванов И.", 45)]

    get_clients_outflow(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
    )

    sql = mock_cursor.execute.call_args[0][0]
    args = list(mock_cursor.execute.call_args[0][1])
    assert "spKDO_ClientList" in sql
    assert "@Filter=?" in sql
    assert "outflow" in args


def test_get_comm_all_by_reason_uses_reason_group_by(mock_pyodbc_cursor):
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("Reason",), ("TotalCount",)]
    mock_cursor.fetchall.return_value = [("outflow", 15)]

    get_comm_all_by_reason(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
    )

    sql = mock_cursor.execute.call_args[0][0]
    args = list(mock_cursor.execute.call_args[0][1])
    assert "spKDO_CommAgg" in sql
    assert "@GroupBy=?" in sql
    assert "reason" in args


def test_get_comm_noshow_by_manager_passes_reason(mock_pyodbc_cursor):
    """Comm-noshow method must pass both @Reason=noshow and @GroupBy=manager."""
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("Manager",), ("TotalCount",)]
    mock_cursor.fetchall.return_value = []

    get_comm_noshow_by_manager(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
    )

    sql = mock_cursor.execute.call_args[0][0]
    args = list(mock_cursor.execute.call_args[0][1])
    assert "@Reason=?" in sql
    assert "noshow" in args
    assert "@GroupBy=?" in sql
    assert "manager" in args


def test_revenue_by_salon_no_object_id(mock_pyodbc_cursor):
    """revenue_by_salon should work without object_id (cross-salon query)."""
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("SalonName",), ("Revenue",)]
    mock_cursor.fetchall.return_value = [("Салон А", 200000.0)]

    result = get_revenue_by_salon(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
    )

    sql = mock_cursor.execute.call_args[0][0]
    assert "@ObjectId=?" not in sql
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


def test_master_id_param_forwarded(mock_pyodbc_cursor):
    """master_id is forwarded to SQL as @MasterId=?."""
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("Revenue",)]
    mock_cursor.fetchall.return_value = [(55000.0,)]

    get_revenue_total(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
        master_id=777,
    )

    sql = mock_cursor.execute.call_args[0][0]
    args = list(mock_cursor.execute.call_args[0][1])
    assert "@MasterId=?" in sql
    assert 777 in args


def test_top_param_forwarded(mock_pyodbc_cursor):
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("Revenue",)]
    mock_cursor.fetchall.return_value = []

    get_revenue_total(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
        top=5,
    )

    args = list(mock_cursor.execute.call_args[0][1])
    assert 5 in args


# ── No-connection guard ───────────────────────────────────────────────────────


def test_empty_conn_str_returns_empty_df():
    """Empty conn_str must return empty DataFrame without raising."""
    result = get_revenue_total(
        conn_str="",
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_no_pyodbc_returns_empty_df(monkeypatch):
    """When pyodbc is None (unavailable), return empty DataFrame without raising."""
    monkeypatch.setattr("swarm_powerbi_bot.services.data_methods.pyodbc", None)
    result = get_revenue_total(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


# ── DataFrame content test ────────────────────────────────────────────────────


def test_rows_converted_to_dataframe(mock_pyodbc_cursor):
    """Multi-row result is returned as DataFrame with correct values."""
    mock_pyodbc, mock_cursor = mock_pyodbc_cursor
    mock_cursor.description = [("MasterName",), ("Revenue",), ("Visits",)]
    mock_cursor.fetchall.return_value = [
        ("Иванова А.", 80000.0, 30),
        ("Петрова Б.", 60000.0, 25),
    ]

    result = get_revenue_by_master(
        conn_str=_CONN,
        date_from=_D_FROM,
        date_to=_D_TO,
        object_id=12345,
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == ["MasterName", "Revenue", "Visits"]
    assert result.iloc[0]["MasterName"] == "Иванова А."
    assert result.iloc[0]["Revenue"] == 80000.0
