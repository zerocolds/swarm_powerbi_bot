from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any, Callable

try:
    import pandas as pd  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError("pandas is required for data_methods. Install it: uv add pandas") from exc

try:
    import pyodbc  # type: ignore
except Exception:  # pragma: no cover
    pyodbc = None
    logging.getLogger(__name__).warning("pyodbc not available — data_methods SQL disabled")

logger = logging.getLogger(__name__)

# ── Expected column schemas per aggregate_id ─────────────────────────────────

_AGGREGATE_COLUMNS: dict[str, list[str]] = {
    "revenue_total": ["Visits", "UniqueClients", "ActiveMasters", "Revenue", "AvgCheck", "TotalHours", "ReturningClients", "SalonName"],
    "revenue_by_week": ["Period", "Visits", "UniqueClients", "Revenue", "AvgCheck", "ActiveMasters"],
    "revenue_by_month": ["Period", "Visits", "UniqueClients", "Revenue", "AvgCheck", "ActiveMasters"],
    "revenue_by_master": ["MasterName", "Rating", "Visits", "UniqueClients", "Revenue", "AvgCheck", "TotalHours", "RevenuePerHour", "SalonName"],
    "revenue_by_service": ["ServiceName", "ServiceCategory", "ServiceCount", "UniqueClients", "Revenue", "AvgCheck", "SalonName"],
    "revenue_by_salon": ["SalonName", "Visits", "UniqueClients", "ActiveMasters", "Revenue", "AvgCheck"],
    "revenue_by_channel": ["Channel", "ClientCount", "Visits", "Revenue", "AvgCheck", "SalonName"],
    "clients_outflow": ["ClientName", "Phone", "Category", "ClientStatus", "LastVisit", "FirstVisit", "ExpectedNextVisit", "DaysSinceLastVisit", "DaysOverdue", "ServicePeriodDays", "TotalVisits", "TotalSpent", "LastCommResult", "SalonName"],
    "clients_leaving": ["ClientName", "Phone", "Category", "ClientStatus", "LastVisit", "ExpectedNextVisit", "DaysSinceLastVisit", "DaysOverdue", "ServicePeriodDays", "TotalVisits", "TotalSpent", "LastCommResult", "SalonName"],
    "clients_forecast": ["ClientName", "Phone", "Category", "ClientStatus", "LastVisit", "ExpectedNextVisit", "DaysUntilExpected", "ServicePeriodDays", "TotalVisits", "TotalSpent", "LastCommResult", "SalonName"],
    "clients_noshow": ["ClientName", "Phone", "Category", "ClientStatus", "LastCancelledVisit", "LastSuccessVisit", "FirstVisit", "LastCommResult", "LastCommDate", "SalonName"],
    "clients_quality": ["ClientName", "Phone", "Category", "ClientStatus", "LastVisit", "FirstVisit", "ExpectedNextVisit", "TotalVisits", "TotalSpent", "LastCommResult", "SalonName"],
    "clients_birthday": ["ClientName", "Phone", "BirthDate", "Age", "Category", "SalonName", "Congratulated"],
    "clients_all": ["ClientName", "Phone", "Category", "ClientStatus", "LastVisit", "FirstVisit", "ExpectedNextVisit", "DaysSinceLastVisit", "DaysOverdue", "ServicePeriodDays", "TotalVisits", "TotalSpent", "LastCommResult", "SalonName"],
    "comm_all_by_reason": ["Reason", "TotalCount", "UniqueClients", "BookedCount", "RefusedCount", "SalonName"],
    "comm_all_by_result": ["Result", "TotalCount", "UniqueClients", "SalonName"],
    "comm_all_by_manager": ["Manager", "TotalCount", "UniqueClients", "BookedCount", "SalonName"],
    "comm_all_list": ["CommDate", "Reason", "CommType", "Result", "Manager", "ClientPhone", "ClientCategory", "Comment", "SalonName"],
    "comm_outflow_by_reason": ["Reason", "TotalCount", "UniqueClients", "BookedCount", "RefusedCount", "SalonName"],
    "comm_leaving_by_result": ["Result", "TotalCount", "UniqueClients", "SalonName"],
    "comm_forecast_by_result": ["Result", "TotalCount", "UniqueClients", "SalonName"],
    "comm_noshow_by_manager": ["Manager", "TotalCount", "UniqueClients", "BookedCount", "SalonName"],
    "comm_quality_by_result": ["Result", "TotalCount", "UniqueClients", "SalonName"],
    "comm_birthday_by_result": ["Result", "TotalCount", "UniqueClients", "SalonName"],
    "comm_waitlist_by_manager": ["Manager", "TotalCount", "UniqueClients", "BookedCount", "SalonName"],
    "comm_opz_by_result": ["Result", "TotalCount", "UniqueClients", "SalonName"],
}


# ── Core SQL execution helper ─────────────────────────────────────────────────

def _execute_sp(
    conn_str: str,
    procedure: str,
    date_from: date,
    date_to: date,
    *,
    object_id: int | None = None,
    master_id: int | None = None,
    group_by: str = "",
    filter_val: str = "",
    reason: str = "",
    top: int = 20,
    empty_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Execute a stored procedure and return results as a DataFrame.

    Returns an empty DataFrame with correct columns on zero-row results.
    Propagates pyodbc.Error — caller is responsible for handling timeouts.
    """
    empty_cols = empty_columns or []

    if pyodbc is None or not conn_str:
        return pd.DataFrame(columns=empty_cols)

    bare = procedure.replace("dbo.", "", 1) if procedure.startswith("dbo.") else procedure
    if not re.fullmatch(r"[a-zA-Z0-9_.]+", bare):
        logger.error("Invalid procedure name rejected: %r", procedure)
        return pd.DataFrame(columns=empty_cols)
    if not procedure.startswith("dbo."):
        procedure = f"dbo.{procedure}"

    sql_parts = [f"EXEC {procedure} @DateFrom=?, @DateTo=?"]
    sql_args: list[Any] = [date_from, date_to]

    if object_id is not None:
        sql_parts.append("@ObjectId=?")
        sql_args.append(object_id)

    if master_id is not None:
        sql_parts.append("@MasterId=?")
        sql_args.append(master_id)

    if group_by:
        sql_parts.append("@GroupBy=?")
        sql_args.append(group_by)

    if filter_val:
        sql_parts.append("@Filter=?")
        sql_args.append(filter_val)

    if reason:
        sql_parts.append("@Reason=?")
        sql_args.append(reason)

    sql_parts.append("@Top=?")
    sql_args.append(top)

    sql = ", ".join(sql_parts) + ";"
    logger.debug("data_method SQL: %s | args=%s", sql, sql_args)

    with pyodbc.connect(conn_str, timeout=10) as conn:
        cur = conn.cursor()
        cur.execute(sql, sql_args)
        cols = [desc[0] for desc in (cur.description or [])]
        rows: list[dict[str, Any]] = []
        for row in cur.fetchall():
            item: dict[str, Any] = {}
            for i, col in enumerate(cols):
                val = row[i]
                item[col] = val.isoformat() if hasattr(val, "isoformat") else val
            rows.append(item)

    if not rows:
        return pd.DataFrame(columns=empty_cols or cols or [])
    return pd.DataFrame(rows)


# ── Factory for atomic data methods ──────────────────────────────────────────

def _make_method(
    aggregate_id: str,
    procedure: str,
    *,
    group_by: str = "",
    filter_val: str = "",
    reason: str = "",
) -> Callable[..., "pd.DataFrame"]:
    """Create a typed data-method closure for a specific aggregate_id."""
    empty_cols = _AGGREGATE_COLUMNS.get(aggregate_id, [])

    def method(
        *,
        conn_str: str,
        date_from: date,
        date_to: date,
        object_id: int | None = None,
        master_id: int | None = None,
        top: int = 20,
        **_extra: Any,
    ) -> pd.DataFrame:
        return _execute_sp(
            conn_str,
            procedure,
            date_from,
            date_to,
            object_id=object_id,
            master_id=master_id,
            group_by=group_by,
            filter_val=filter_val,
            reason=reason,
            top=top,
            empty_columns=empty_cols,
        )

    method.__name__ = f"get_{aggregate_id}"
    method.__qualname__ = f"get_{aggregate_id}"
    method.__doc__ = aggregate_id
    return method


# ── spKDO_Aggregate methods ───────────────────────────────────────────────────

get_revenue_total = _make_method("revenue_total", "spKDO_Aggregate", group_by="total")
get_revenue_by_week = _make_method("revenue_by_week", "spKDO_Aggregate", group_by="week")
get_revenue_by_month = _make_method("revenue_by_month", "spKDO_Aggregate", group_by="month")
get_revenue_by_master = _make_method("revenue_by_master", "spKDO_Aggregate", group_by="master")
get_revenue_by_service = _make_method("revenue_by_service", "spKDO_Aggregate", group_by="service")
get_revenue_by_salon = _make_method("revenue_by_salon", "spKDO_Aggregate", group_by="salon")
get_revenue_by_channel = _make_method("revenue_by_channel", "spKDO_Aggregate", group_by="channel")

# ── spKDO_ClientList methods ──────────────────────────────────────────────────

get_clients_outflow = _make_method("clients_outflow", "spKDO_ClientList", filter_val="outflow")
get_clients_leaving = _make_method("clients_leaving", "spKDO_ClientList", filter_val="leaving")
get_clients_forecast = _make_method("clients_forecast", "spKDO_ClientList", filter_val="forecast")
get_clients_noshow = _make_method("clients_noshow", "spKDO_ClientList", filter_val="noshow")
get_clients_quality = _make_method("clients_quality", "spKDO_ClientList", filter_val="quality")
get_clients_birthday = _make_method("clients_birthday", "spKDO_ClientList", filter_val="birthday")
get_clients_all = _make_method("clients_all", "spKDO_ClientList", filter_val="all")

# ── spKDO_CommAgg methods ─────────────────────────────────────────────────────

get_comm_all_by_reason = _make_method("comm_all_by_reason", "spKDO_CommAgg", group_by="reason")
get_comm_all_by_result = _make_method("comm_all_by_result", "spKDO_CommAgg", group_by="result")
get_comm_all_by_manager = _make_method("comm_all_by_manager", "spKDO_CommAgg", group_by="manager")
get_comm_all_list = _make_method("comm_all_list", "spKDO_CommAgg", group_by="list")
get_comm_outflow_by_reason = _make_method("comm_outflow_by_reason", "spKDO_CommAgg", reason="outflow", group_by="reason")
get_comm_leaving_by_result = _make_method("comm_leaving_by_result", "spKDO_CommAgg", reason="leaving", group_by="result")
get_comm_forecast_by_result = _make_method("comm_forecast_by_result", "spKDO_CommAgg", reason="forecast", group_by="result")
get_comm_noshow_by_manager = _make_method("comm_noshow_by_manager", "spKDO_CommAgg", reason="noshow", group_by="manager")
get_comm_quality_by_result = _make_method("comm_quality_by_result", "spKDO_CommAgg", reason="quality", group_by="result")
get_comm_birthday_by_result = _make_method("comm_birthday_by_result", "spKDO_CommAgg", reason="birthday", group_by="result")
get_comm_waitlist_by_manager = _make_method("comm_waitlist_by_manager", "spKDO_CommAgg", reason="waitlist", group_by="manager")
get_comm_opz_by_result = _make_method("comm_opz_by_result", "spKDO_CommAgg", reason="opz", group_by="result")

# ── Registry ──────────────────────────────────────────────────────────────────

DATA_METHODS: dict[str, Callable[..., "pd.DataFrame"]] = {
    "revenue_total": get_revenue_total,
    "revenue_by_week": get_revenue_by_week,
    "revenue_by_month": get_revenue_by_month,
    "revenue_by_master": get_revenue_by_master,
    "revenue_by_service": get_revenue_by_service,
    "revenue_by_salon": get_revenue_by_salon,
    "revenue_by_channel": get_revenue_by_channel,
    "clients_outflow": get_clients_outflow,
    "clients_leaving": get_clients_leaving,
    "clients_forecast": get_clients_forecast,
    "clients_noshow": get_clients_noshow,
    "clients_quality": get_clients_quality,
    "clients_birthday": get_clients_birthday,
    "clients_all": get_clients_all,
    "comm_all_by_reason": get_comm_all_by_reason,
    "comm_all_by_result": get_comm_all_by_result,
    "comm_all_by_manager": get_comm_all_by_manager,
    "comm_all_list": get_comm_all_list,
    "comm_outflow_by_reason": get_comm_outflow_by_reason,
    "comm_leaving_by_result": get_comm_leaving_by_result,
    "comm_forecast_by_result": get_comm_forecast_by_result,
    "comm_noshow_by_manager": get_comm_noshow_by_manager,
    "comm_quality_by_result": get_comm_quality_by_result,
    "comm_birthday_by_result": get_comm_birthday_by_result,
    "comm_waitlist_by_manager": get_comm_waitlist_by_manager,
    "comm_opz_by_result": get_comm_opz_by_result,
}
