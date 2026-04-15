"""Интеграционные тесты SQL через реальный MSSQL.

Запуск: uv run pytest tests/integration/test_real_sql.py -m integration -v
"""
from __future__ import annotations

import asyncio

import pytest

from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry
from swarm_powerbi_bot.services.sql_client import SQLClient

pytestmark = pytest.mark.integration

PROCEDURES = ["spKDO_Aggregate", "spKDO_ClientList", "spKDO_CommAgg"]


# ── 1. Соединение ────────────────────────────────────────────────────────────

def test_connection(real_settings, mssql_ok):
    if not mssql_ok:
        pytest.skip("MSSQL not available")
    import pyodbc

    conn = pyodbc.connect(real_settings.sql_connection_string(), timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    assert cursor.fetchone()[0] == 1
    conn.close()


# ── 2. Процедуры существуют ──────────────────────────────────────────────────

def test_procedures_exist(real_settings, mssql_ok):
    if not mssql_ok:
        pytest.skip("MSSQL not available")
    import pyodbc

    conn = pyodbc.connect(real_settings.sql_connection_string(), timeout=10)
    cursor = conn.cursor()
    for proc in PROCEDURES:
        cursor.execute(f"SELECT OBJECT_ID('dbo.{proc}')")  # noqa: S608
        row = cursor.fetchone()
        assert row is not None and row[0] is not None, f"Procedure {proc} not found"
    conn.close()


# ── 3. revenue_total ─────────────────────────────────────────────────────────

async def test_aggregate_revenue_total(
    real_sql_client: SQLClient, real_registry: AggregateRegistry,
    test_object_id: int, test_date_range: tuple[str, str],
):
    date_from, date_to = test_date_range
    result = await real_sql_client.execute_aggregate(
        "revenue_total",
        {"object_id": test_object_id, "date_from": date_from, "date_to": date_to, "group_by": "total"},
        real_registry,
    )
    assert result.status == "ok", f"error: {result.error}"
    assert result.row_count > 0
    assert any("Revenue" in str(k) or "revenue" in str(k) for row in result.rows for k in row)


# ── 4. clients_outflow ───────────────────────────────────────────────────────

async def test_aggregate_clients_outflow(
    real_sql_client: SQLClient, real_registry: AggregateRegistry,
    test_object_id: int,
):
    result = await real_sql_client.execute_aggregate(
        "clients_outflow",
        {"object_id": test_object_id, "filter": "outflow", "group_by": "list"},
        real_registry,
    )
    assert result.status == "ok", f"error: {result.error}"


# ── 5. comm_all_by_reason ────────────────────────────────────────────────────

async def test_aggregate_comm_all(
    real_sql_client: SQLClient, real_registry: AggregateRegistry,
    test_object_id: int, test_date_range: tuple[str, str],
):
    date_from, date_to = test_date_range
    result = await real_sql_client.execute_aggregate(
        "comm_all_by_reason",
        {
            "object_id": test_object_id,
            "date_from": date_from,
            "date_to": date_to,
            "reason": "all",
            "group_by": "reason",
        },
        real_registry,
    )
    assert result.status == "ok", f"error: {result.error}"


# ── 6. Все 26 агрегатов без ошибок ──────────────────────────────────────────

async def test_all_aggregates_no_error(
    real_sql_client: SQLClient, real_registry: AggregateRegistry,
    test_object_id: int, test_date_range: tuple[str, str],
):
    date_from, date_to = test_date_range
    aggregates = real_registry.list_aggregates()
    errors = []
    for entry in aggregates:
        agg_id = entry["id"]
        params: dict = {"object_id": test_object_id}
        for p in entry.get("parameters", []):
            name = p.get("name", "")
            if name == "date_from":
                params["date_from"] = date_from
            elif name == "date_to":
                params["date_to"] = date_to
            elif name == "group_by":
                default = p.get("default", "")
                allowed = entry.get("allowed_group_by", [])
                params["group_by"] = default if default else (allowed[0] if allowed else "")
            elif name in ("filter", "reason"):
                params[name] = p.get("default", "all")
            elif name == "top":
                params["top"] = p.get("default", 20)
        result = await real_sql_client.execute_aggregate(agg_id, params, real_registry)
        if result.status != "ok":
            errors.append(f"{agg_id}: {result.error}")
    assert not errors, f"Aggregates with errors: {errors}"


# ── 7. Невалидный object_id ──────────────────────────────────────────────────

async def test_invalid_object_id(
    real_sql_client: SQLClient, real_registry: AggregateRegistry,
    test_date_range: tuple[str, str],
):
    date_from, date_to = test_date_range
    result = await real_sql_client.execute_aggregate(
        "revenue_total",
        {"object_id": 999999999, "date_from": date_from, "date_to": date_to, "group_by": "total"},
        real_registry,
    )
    assert result.status == "ok", "invalid object_id should return ok with 0 rows, not error"
    assert result.row_count == 0


# ── 8. Timeout при большом date range ────────────────────────────────────────

async def test_query_timeout(
    real_sql_client: SQLClient, real_registry: AggregateRegistry,
    test_object_id: int,
):
    result = await real_sql_client.execute_aggregate(
        "revenue_by_week",
        {"object_id": test_object_id, "date_from": "2016-01-01", "date_to": "2026-03-31", "group_by": "week"},
        real_registry,
    )
    # Должен завершиться (ok или timeout), но не зависнуть
    assert result.status in ("ok", "timeout")


# ── 9. SQL injection отклонён whitelist ──────────────────────────────────────

async def test_whitelist_rejects_injection(
    real_sql_client: SQLClient, real_registry: AggregateRegistry,
):
    result = await real_sql_client.execute_aggregate(
        "DROP TABLE users; --",
        {"object_id": 1},
        real_registry,
    )
    assert result.status == "error"
    assert "unknown aggregate_id" in (result.error or "").lower()


# ── 10. Конкурентные запросы ─────────────────────────────────────────────────

async def test_concurrent_aggregates(
    real_sql_client: SQLClient, real_registry: AggregateRegistry,
    test_object_id: int, test_date_range: tuple[str, str],
):
    date_from, date_to = test_date_range
    agg_ids = ["revenue_total", "revenue_by_week", "revenue_by_master",
               "clients_outflow", "comm_all_by_reason"]

    async def run_one(agg_id: str):
        params: dict = {"object_id": test_object_id, "date_from": date_from, "date_to": date_to}
        entry = real_registry.get_aggregate(agg_id)
        if entry:
            for p in entry.get("parameters", []):
                name = p.get("name", "")
                if name == "group_by":
                    default = p.get("default", "")
                    allowed = entry.get("allowed_group_by", [])
                    params["group_by"] = default if default else (allowed[0] if allowed else "")
                elif name in ("filter", "reason"):
                    params[name] = p.get("default", "all")
        return await real_sql_client.execute_aggregate(agg_id, params, real_registry)

    results = await asyncio.gather(*[run_one(a) for a in agg_ids])
    for r in results:
        assert r.status == "ok", f"{r.aggregate_id}: {r.error}"
