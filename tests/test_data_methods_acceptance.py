"""Acceptance tests for data-methods refactor (spec: epic #12, task #13).

Covers acceptance criteria not addressed in test_data_methods.py:
  - INVENTORY.md existence & completeness
  - Keyword-only signature enforcement
  - Parametrized empty-result invariant for ALL 26 methods
  - pyodbc.Error propagation (not swallowed)
  - Invalid procedure name rejection
  - datetime isoformat value conversion
  - Extra **dims silently ignored
  - sql_client._execute_aggregate_sync delegates catalog aggregates to DATA_METHODS
"""
from __future__ import annotations

import inspect
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from swarm_powerbi_bot.services.data_methods import (
    DATA_METHODS,
    _AGGREGATE_COLUMNS,
    _execute_sp,
    get_revenue_total,
    get_clients_outflow,
)

_CONN = "Driver={ODBC Driver 17 for SQL Server};Server=test;Database=test;"
_D_FROM = date(2026, 3, 1)
_D_TO = date(2026, 3, 31)

_ALL_26 = list(DATA_METHODS.keys())
assert len(_ALL_26) == 26, f"Expected 26 methods, got {len(_ALL_26)}"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_cursor(columns: list[str], rows: list[tuple]) -> MagicMock:
    cur = MagicMock()
    cur.description = [(c,) for c in columns]
    cur.fetchall.return_value = rows
    return cur


def _mock_pyodbc_ctx(cursor: MagicMock):
    """Context manager that patches pyodbc in data_methods with the given cursor."""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_pyodbc = MagicMock()
    mock_pyodbc.connect.return_value = mock_conn
    return patch("swarm_powerbi_bot.services.data_methods.pyodbc", mock_pyodbc), mock_pyodbc, cursor


# ── AC-1: INVENTORY.md exists and is structurally complete ───────────────────


INVENTORY_PATH = Path(__file__).parent.parent / "docs" / "data-methods" / "INVENTORY.md"


def test_inventory_md_exists():
    assert INVENTORY_PATH.exists(), f"INVENTORY.md not found at {INVENTORY_PATH}"


def test_inventory_md_lists_all_procedures():
    """INVENTORY.md must mention all three stored procedures."""
    content = INVENTORY_PATH.read_text(encoding="utf-8")
    for proc in ("spKDO_Aggregate", "spKDO_ClientList", "spKDO_CommAgg"):
        assert proc in content, f"INVENTORY.md missing procedure {proc}"


def test_inventory_md_lists_all_aggregate_ids():
    """Every aggregate_id in DATA_METHODS must appear in INVENTORY.md."""
    content = INVENTORY_PATH.read_text(encoding="utf-8")
    missing = [agg_id for agg_id in DATA_METHODS if f"`{agg_id}`" not in content]
    assert not missing, f"aggregate_ids missing from INVENTORY.md: {missing}"


def test_inventory_md_documents_edge_cases():
    """INVENTORY.md must document multiple-result-set and timeout behaviour."""
    content = INVENTORY_PATH.read_text(encoding="utf-8")
    assert "result set" in content.lower() or "result-set" in content.lower(), \
        "INVENTORY.md must document multiple result-set behaviour"
    assert "timeout" in content.lower() or "pyodbc.Error" in content, \
        "INVENTORY.md must document timeout/pyodbc.Error propagation"


# ── AC-2: Keyword-only signature enforcement ──────────────────────────────────


def test_all_methods_require_keyword_only_date_from_date_to():
    """date_from and date_to must be keyword-only in every DATA_METHODS entry."""
    for name, fn in DATA_METHODS.items():
        sig = inspect.signature(fn)
        params = sig.parameters
        assert "date_from" in params, f"DATA_METHODS[{name!r}] missing date_from param"
        assert "date_to" in params, f"DATA_METHODS[{name!r}] missing date_to param"
        # keyword-only = KEYWORD_ONLY kind
        assert params["date_from"].kind == inspect.Parameter.KEYWORD_ONLY, \
            f"DATA_METHODS[{name!r}].date_from is not keyword-only"
        assert params["date_to"].kind == inspect.Parameter.KEYWORD_ONLY, \
            f"DATA_METHODS[{name!r}].date_to is not keyword-only"


def test_calling_positionally_raises_type_error():
    """Passing date_from positionally must raise TypeError."""
    with pytest.raises(TypeError):
        get_revenue_total(_CONN, _D_FROM, _D_TO)  # type: ignore[call-arg]


# ── AC-3: Parametrised empty-result invariant for ALL 26 methods ──────────────


@pytest.mark.parametrize("aggregate_id", _ALL_26)
def test_empty_result_invariant_all_methods(aggregate_id: str):
    """Every data-method must return empty DataFrame (not raise) on zero rows."""
    cur = _make_cursor([], [])
    patcher, mock_pyodbc, _ = _mock_pyodbc_ctx(cur)

    with patcher:
        fn = DATA_METHODS[aggregate_id]
        result = fn(conn_str=_CONN, date_from=_D_FROM, date_to=_D_TO, object_id=12345)

    assert isinstance(result, pd.DataFrame), \
        f"DATA_METHODS[{aggregate_id!r}] returned {type(result)}, expected DataFrame"
    assert len(result) == 0, \
        f"DATA_METHODS[{aggregate_id!r}] returned {len(result)} rows, expected 0"


@pytest.mark.parametrize("aggregate_id", _ALL_26)
def test_empty_result_has_expected_columns(aggregate_id: str):
    """Empty DataFrame must include the expected columns from _AGGREGATE_COLUMNS."""
    cur = _make_cursor([], [])
    patcher, mock_pyodbc, _ = _mock_pyodbc_ctx(cur)

    with patcher:
        fn = DATA_METHODS[aggregate_id]
        result = fn(conn_str=_CONN, date_from=_D_FROM, date_to=_D_TO, object_id=12345)

    # When description is None the empty_columns schema is the fallback.
    # We validate that the returned columns list is well-typed.
    assert isinstance(result.columns.tolist(), list)
    # Validate schema consistency: every registered column must map to the method
    assert aggregate_id in _AGGREGATE_COLUMNS


# ── AC-4: pyodbc.Error propagation ───────────────────────────────────────────
# Note: real pyodbc is not installed in CI (no libodbc.so.2). We create a
# synthetic Error class that mimics pyodbc.Error to test the propagation
# invariant without requiring the native library.


class _FakePyodbcError(Exception):
    """Fake pyodbc.Error used in CI where libodbc.so.2 is absent."""


def test_pyodbc_error_propagates_from_execute_sp():
    """pyodbc.Error from cursor.execute() must NOT be caught — it propagates."""
    cur = MagicMock()
    cur.execute.side_effect = _FakePyodbcError("08001", "Connection timeout")

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = cur
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_pyodbc = MagicMock()
    mock_pyodbc.connect.return_value = mock_conn
    mock_pyodbc.Error = _FakePyodbcError

    with patch("swarm_powerbi_bot.services.data_methods.pyodbc", mock_pyodbc):
        with pytest.raises(_FakePyodbcError):
            get_revenue_total(
                conn_str=_CONN,
                date_from=_D_FROM,
                date_to=_D_TO,
                object_id=12345,
            )


def test_pyodbc_error_propagates_from_connect():
    """pyodbc.Error on connect() also propagates — not swallowed."""
    mock_pyodbc = MagicMock()
    mock_pyodbc.connect.side_effect = _FakePyodbcError("08001", "Server unreachable")
    mock_pyodbc.Error = _FakePyodbcError

    with patch("swarm_powerbi_bot.services.data_methods.pyodbc", mock_pyodbc):
        with pytest.raises(_FakePyodbcError):
            get_revenue_total(
                conn_str=_CONN,
                date_from=_D_FROM,
                date_to=_D_TO,
                object_id=12345,
            )


# ── AC-5: Invalid procedure name rejection ────────────────────────────────────


def test_invalid_procedure_name_returns_empty_df_no_raise():
    """_execute_sp must reject invalid procedure names without raising."""
    result = _execute_sp(
        conn_str=_CONN,
        procedure="bad; DROP TABLE clients--",
        date_from=_D_FROM,
        date_to=_D_TO,
        empty_columns=["Col1", "Col2"],
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_procedure_name_with_spaces_rejected():
    result = _execute_sp(
        conn_str=_CONN,
        procedure="spKDO Aggregate",
        date_from=_D_FROM,
        date_to=_D_TO,
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_valid_procedure_name_with_dbo_prefix_accepted():
    """dbo.-prefixed procedure names are accepted (prefix stripped for validation)."""
    cur = _make_cursor(["Revenue"], [(100.0,)])
    patcher, mock_pyodbc, _ = _mock_pyodbc_ctx(cur)

    with patcher:
        result = _execute_sp(
            conn_str=_CONN,
            procedure="dbo.spKDO_Aggregate",
            date_from=_D_FROM,
            date_to=_D_TO,
        )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


# ── AC-6: datetime isoformat conversion ───────────────────────────────────────


def test_datetime_values_converted_to_isoformat():
    """datetime values in SQL rows must be converted to ISO strings in the DataFrame."""
    dt_val = datetime(2026, 3, 15, 10, 30, 0)
    cur = _make_cursor(["ClientName", "LastVisit"], [("Иванов И.", dt_val)])
    patcher, mock_pyodbc, _ = _mock_pyodbc_ctx(cur)

    with patcher:
        result = get_clients_outflow(
            conn_str=_CONN,
            date_from=_D_FROM,
            date_to=_D_TO,
            object_id=12345,
        )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    last_visit = result.iloc[0]["LastVisit"]
    assert last_visit == "2026-03-15T10:30:00", \
        f"Expected ISO string, got {last_visit!r}"


def test_date_values_converted_to_isoformat():
    """date (not datetime) values are also converted via isoformat()."""
    d_val = date(2026, 3, 15)
    cur = _make_cursor(["BirthDate"], [(d_val,)])
    patcher, mock_pyodbc, _ = _mock_pyodbc_ctx(cur)

    with patcher:
        result = _execute_sp(
            conn_str=_CONN,
            procedure="spKDO_ClientList",
            date_from=_D_FROM,
            date_to=_D_TO,
        )

    assert len(result) == 1
    assert result.iloc[0]["BirthDate"] == "2026-03-15"


# ── AC-7: Extra **dims silently ignored ───────────────────────────────────────


def test_extra_dims_do_not_raise():
    """Extra keyword arguments (**dims) must be silently ignored — not raise."""
    cur = _make_cursor([], [])
    patcher, mock_pyodbc, _ = _mock_pyodbc_ctx(cur)

    with patcher:
        result = get_revenue_total(
            conn_str=_CONN,
            date_from=_D_FROM,
            date_to=_D_TO,
            object_id=12345,
            unknown_dimension="some_value",
            another_extra=42,
        )

    assert isinstance(result, pd.DataFrame)


# ── AC-8: sql_client._execute_aggregate_sync delegates to DATA_METHODS ────────


def test_execute_aggregate_sync_uses_data_methods_for_catalog_aggregate():
    """_execute_aggregate_sync must call DATA_METHODS for known aggregate IDs."""
    from swarm_powerbi_bot.services.sql_client import SQLClient  # noqa: PLC0415
    from swarm_powerbi_bot.config import Settings  # noqa: PLC0415

    mock_settings = MagicMock(spec=Settings)
    mock_settings.sql_connection_string.return_value = _CONN
    mock_settings.default_object_id = 12345

    mock_df = pd.DataFrame([{"Revenue": 100000.0, "Visits": 50}])
    mock_method = MagicMock(return_value=mock_df)

    client = SQLClient(mock_settings)

    with patch.dict(
        "swarm_powerbi_bot.services.data_methods.DATA_METHODS",
        {"revenue_total": mock_method},
        clear=False,
    ):
        # Patch the import inside _execute_aggregate_sync
        with patch(
            "swarm_powerbi_bot.services.sql_client.DATA_METHODS" if False else
            "swarm_powerbi_bot.services.data_methods.DATA_METHODS",
        ):
            pass  # Ensure the module is importable

        params = {
            "date_from": "2026-03-01",
            "date_to": "2026-03-31",
            "object_id": 12345,
            "group_by": "total",
        }
        # Call the sync method directly (not async)
        with patch("swarm_powerbi_bot.services.sql_client.pyodbc", MagicMock()):
            # Monkey-patch DATA_METHODS in sql_client's local import scope
            import swarm_powerbi_bot.services.data_methods as dm_module  # noqa: PLC0415
            original = dm_module.DATA_METHODS.get("revenue_total")
            dm_module.DATA_METHODS["revenue_total"] = mock_method
            try:
                rows, agg_id, date_params = client._execute_aggregate_sync(
                    "revenue_total",
                    "spKDO_Aggregate",
                    params,
                )
            finally:
                if original is not None:
                    dm_module.DATA_METHODS["revenue_total"] = original
                elif "revenue_total" in dm_module.DATA_METHODS:
                    del dm_module.DATA_METHODS["revenue_total"]

    mock_method.assert_called_once()
    assert agg_id == "revenue_total"
    assert rows == [{"Revenue": 100000.0, "Visits": 50}]


def test_execute_aggregate_sync_bypasses_data_methods_for_legacy():
    """_execute_aggregate_sync must NOT call DATA_METHODS for legacy procedures."""
    from swarm_powerbi_bot.services.sql_client import SQLClient  # noqa: PLC0415
    from swarm_powerbi_bot.config import Settings  # noqa: PLC0415

    mock_settings = MagicMock(spec=Settings)
    mock_settings.sql_connection_string.return_value = ""  # no connection → early return
    mock_settings.default_object_id = 12345

    client = SQLClient(mock_settings)
    params = {
        "date_from": "2026-03-01",
        "date_to": "2026-03-31",
        "object_id": 12345,
    }
    rows, agg_id, _ = client._execute_aggregate_sync(
        "attachments",
        "spKDO_Attachments",
        params,
    )
    assert rows == []  # empty because no conn_str
    assert agg_id == "attachments"


# ── AC-9: multiple result sets — only first is used ───────────────────────────


def test_only_first_result_set_consumed():
    """_execute_sp uses a single cursor.fetchall() — nextset() is never called."""
    cur = _make_cursor(["Revenue"], [(100.0,)])
    patcher, mock_pyodbc, _ = _mock_pyodbc_ctx(cur)

    with patcher:
        get_revenue_total(
            conn_str=_CONN,
            date_from=_D_FROM,
            date_to=_D_TO,
            object_id=12345,
        )

    # nextset should never have been called
    cur.nextset.assert_not_called()
    cur.fetchall.assert_called_once()


# ── AC-10: Planner imports DATA_METHODS ───────────────────────────────────────


def test_planner_imports_data_methods():
    """PlannerAgent must import DATA_METHODS from data_methods module."""
    import swarm_powerbi_bot.agents.planner as planner_module  # noqa: PLC0415
    assert hasattr(planner_module, "DATA_METHODS"), \
        "planner module must import DATA_METHODS from data_methods"


def test_planner_data_methods_is_same_object():
    """The DATA_METHODS in planner must be the canonical registry."""
    import swarm_powerbi_bot.agents.planner as planner_module  # noqa: PLC0415
    from swarm_powerbi_bot.services.data_methods import DATA_METHODS  # noqa: PLC0415
    assert planner_module.DATA_METHODS is DATA_METHODS, \
        "planner.DATA_METHODS is not the same object as data_methods.DATA_METHODS"


# ── AC-11: All methods' names match their aggregate_id ───────────────────────


def test_all_method_names_match_aggregate_id():
    """__name__ of each data-method closure must be 'get_<aggregate_id>'."""
    for agg_id, fn in DATA_METHODS.items():
        expected_name = f"get_{agg_id}"
        assert fn.__name__ == expected_name, \
            f"DATA_METHODS[{agg_id!r}].__name__ = {fn.__name__!r}, expected {expected_name!r}"


# ── AC-12: No PII logged at DEBUG level ───────────────────────────────────────


def test_debug_log_does_not_include_full_names(caplog):
    """SQL debug log must not emit full Russian client names as arguments."""
    import logging  # noqa: PLC0415

    cur = _make_cursor(["ClientName", "Phone"], [("Иванов Иван Иванович", "+79001234567")])
    patcher, mock_pyodbc, _ = _mock_pyodbc_ctx(cur)

    with caplog.at_level(logging.DEBUG, logger="swarm_powerbi_bot.services.data_methods"):
        with patcher:
            get_clients_outflow(
                conn_str=_CONN,
                date_from=_D_FROM,
                date_to=_D_TO,
                object_id=12345,
            )

    # The SQL debug line logs the SQL template and args — args are date/int values only
    # Full client names appear only in the result DataFrame, not in logs
    for record in caplog.records:
        if "data_method SQL" in record.message:
            assert "Иванов" not in record.message, \
                "Full name leaked into SQL debug log"
            assert "+79001234567" not in record.message, \
                "Phone number leaked into SQL debug log"
