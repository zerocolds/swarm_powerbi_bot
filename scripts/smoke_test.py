#!/usr/bin/env python3
"""Smoke test для Semantic Aggregate Layer.

Проверяет все компоненты: MSSQL, процедуры, каталог, агрегаты, LLM, E2E.
Выход: JSON-отчёт в stdout.
Exit codes: 0=PASS, 1=FAIL, 2=CONFIG_ERROR.

Запуск: uv run python scripts/smoke_test.py
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# src/ в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("smoke_test")
logger.setLevel(logging.INFO)

# ── Константы ────────────────────────────────────────────────────────────────

TEST_OBJECT_ID = 506770
DATE_FROM = "2026-03-01"
DATE_TO = "2026-03-31"
PROCEDURES = ["spKDO_Aggregate", "spKDO_ClientList", "spKDO_CommAgg"]
EXPECTED_MIN_AGGREGATES = 25  # каталог >=25, ожидаем 27
ZERO_ROWS_OK = {"clients_birthday", "clients_forecast", "comm_waitlist_by_manager"}

# ── Типы ─────────────────────────────────────────────────────────────────────

StepResult = dict  # {"name", "status", "duration_ms", "detail"}


def _step(name: str, status: str, duration_ms: int, detail: str = "") -> StepResult:
    return {"name": name, "status": status, "duration_ms": duration_ms, "detail": detail}


# ── Step 1: MSSQL Connectivity ───────────────────────────────────────────────

def step_mssql_connectivity(conn_str: str) -> StepResult:
    t0 = time.monotonic()
    try:
        import pyodbc
    except ImportError:
        return _step("mssql_connectivity", "FAIL", 0, "pyodbc not installed")

    if not conn_str:
        return _step("mssql_connectivity", "FAIL", 0, "empty connection string (check MSSQL_* env vars)")

    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        conn.close()
        ms = int((time.monotonic() - t0) * 1000)
        if row and row[0] == 1:
            return _step("mssql_connectivity", "PASS", ms, "SELECT 1 = 1")
        return _step("mssql_connectivity", "FAIL", ms, f"unexpected result: {row}")
    except Exception as exc:
        ms = int((time.monotonic() - t0) * 1000)
        return _step("mssql_connectivity", "FAIL", ms, str(exc)[:300])


# ── Step 2: Procedures Exist ─────────────────────────────────────────────────

def step_procedures_exist(conn_str: str) -> StepResult:
    t0 = time.monotonic()
    if not conn_str:
        return _step("procedures_exist", "SKIP", 0, "no connection string")

    try:
        import pyodbc

        conn = pyodbc.connect(conn_str, timeout=15)
        cursor = conn.cursor()
        found = []
        missing = []
        for proc in PROCEDURES:
            cursor.execute(f"SELECT OBJECT_ID('dbo.{proc}')")  # noqa: S608
            row = cursor.fetchone()
            if row and row[0] is not None:
                found.append(proc)
            else:
                missing.append(proc)
        conn.close()
        ms = int((time.monotonic() - t0) * 1000)
        if missing:
            return _step("procedures_exist", "FAIL", ms, f"missing: {missing}")
        return _step("procedures_exist", "PASS", ms, f"found: {len(found)}/{len(PROCEDURES)}")
    except Exception as exc:
        ms = int((time.monotonic() - t0) * 1000)
        return _step("procedures_exist", "FAIL", ms, str(exc)[:300])


# ── Step 3: Catalog Validation ───────────────────────────────────────────────

def step_catalog_validation(catalog_path: str) -> tuple[StepResult, list[dict] | None]:
    """Возвращает (step_result, list_of_aggregates | None)."""
    t0 = time.monotonic()
    try:
        from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry

        registry = AggregateRegistry(catalog_path)
        aggregates = registry.list_aggregates()
        ms = int((time.monotonic() - t0) * 1000)

        procs_found = {a.get("procedure") for a in aggregates}
        bad_procs = procs_found - set(PROCEDURES)

        if len(aggregates) < EXPECTED_MIN_AGGREGATES:
            return _step(
                "catalog_validation", "FAIL", ms,
                f"only {len(aggregates)} aggregates (expected >= {EXPECTED_MIN_AGGREGATES})",
            ), None

        if bad_procs:
            return _step(
                "catalog_validation", "FAIL", ms,
                f"unknown procedures in catalog: {bad_procs}",
            ), None

        return _step(
            "catalog_validation", "PASS", ms,
            f"{len(aggregates)} aggregates, procedures: {sorted(procs_found)}",
        ), aggregates
    except Exception as exc:
        ms = int((time.monotonic() - t0) * 1000)
        return _step("catalog_validation", "FAIL", ms, str(exc)[:300]), None


# ── Step 4: Execute All Aggregates ───────────────────────────────────────────

def _build_params(entry: dict) -> dict:
    """Строит params для тестового вызова агрегата из каталога."""
    params: dict = {}
    for p in entry.get("parameters", []):
        name = p.get("name", "")
        ptype = p.get("type", "")

        if name == "object_id":
            params["object_id"] = TEST_OBJECT_ID
        elif name == "date_from":
            params["date_from"] = DATE_FROM
        elif name == "date_to":
            params["date_to"] = DATE_TO
        elif name in ("master_id",):
            continue  # опциональный, не задаём
        elif name == "top":
            params["top"] = p.get("default", 20)
        elif name == "group_by":
            default = p.get("default", "")
            allowed = entry.get("allowed_group_by", [])
            params["group_by"] = default if default else (allowed[0] if allowed else "")
        elif name in ("filter", "reason"):
            params[name] = p.get("default", "all")
        elif ptype == "int" and "default" in p:
            params[name] = p["default"]
        elif ptype == "string" and "default" in p:
            val = p["default"]
            if val not in ("today", "today+7d"):
                params[name] = val

    return params


async def step_execute_aggregates(
    conn_str: str, catalog_path: str, aggregates: list[dict],
) -> tuple[StepResult, list[dict]]:
    t0 = time.monotonic()
    agg_results: list[dict] = []

    if not conn_str:
        return _step("execute_aggregates", "SKIP", 0, "no connection string"), agg_results

    try:
        from swarm_powerbi_bot.config import Settings
        from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry
        from swarm_powerbi_bot.services.sql_client import SQLClient

        settings = Settings.from_env()
        sql_client = SQLClient(settings)
        registry = AggregateRegistry(catalog_path)

        errors = 0
        for entry in aggregates:
            agg_id = entry["id"]
            params = _build_params(entry)
            at0 = time.monotonic()
            try:
                result = await sql_client.execute_aggregate(agg_id, params, registry)
                ams = int((time.monotonic() - at0) * 1000)
                agg_results.append({
                    "aggregate_id": agg_id,
                    "status": result.status,
                    "row_count": result.row_count,
                    "duration_ms": ams,
                    "error": result.error or "",
                })
                if result.status != "ok":
                    if agg_id not in ZERO_ROWS_OK:
                        errors += 1
            except Exception as exc:
                ams = int((time.monotonic() - at0) * 1000)
                agg_results.append({
                    "aggregate_id": agg_id,
                    "status": "error",
                    "row_count": 0,
                    "duration_ms": ams,
                    "error": str(exc)[:200],
                })
                errors += 1

        ms = int((time.monotonic() - t0) * 1000)
        ok_count = len(aggregates) - errors
        if errors > 0:
            return _step(
                "execute_aggregates", "FAIL", ms,
                f"{ok_count}/{len(aggregates)} ok, {errors} errors",
            ), agg_results
        return _step(
            "execute_aggregates", "PASS", ms,
            f"{ok_count}/{len(aggregates)} ok",
        ), agg_results
    except Exception as exc:
        ms = int((time.monotonic() - t0) * 1000)
        return _step("execute_aggregates", "FAIL", ms, str(exc)[:300]), agg_results


# ── Step 5: Ollama LLM Health ────────────────────────────────────────────────

def step_ollama_health(base_url: str, model: str) -> StepResult:
    t0 = time.monotonic()
    if not base_url:
        return _step("ollama_health", "SKIP", 0, "OLLAMA_BASE_URL not set")

    try:
        import urllib.request

        url = base_url.rstrip("/") + "/api/chat"
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": "Ответь одним словом: тест."}],
            "stream": False,
            "think": False,
            "options": {"num_predict": 32},
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=15)  # noqa: S310
        body = json.loads(resp.read())
        content = body.get("message", {}).get("content", "")
        ms = int((time.monotonic() - t0) * 1000)
        if content.strip():
            return _step("ollama_health", "PASS", ms, f"response: {content[:80]}")
        return _step("ollama_health", "FAIL", ms, "empty response from LLM")
    except Exception as exc:
        ms = int((time.monotonic() - t0) * 1000)
        return _step("ollama_health", "FAIL", ms, str(exc)[:300])


# ── Step 6: LLM Planning ────────────────────────────────────────────────────

async def step_llm_planning(settings) -> StepResult:
    t0 = time.monotonic()
    try:
        from swarm_powerbi_bot.models import UserQuestion
        from swarm_powerbi_bot.services import LLMClient
        from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry
        from swarm_powerbi_bot.agents import PlannerAgent

        llm_client = LLMClient(settings)
        registry = AggregateRegistry(settings.aggregate_catalog_path)
        planner = PlannerAgent(
            llm_client=llm_client,
            aggregate_registry=registry,
            semantic_catalog_path=settings.semantic_catalog_path,
        )
        question = UserQuestion(
            user_id="smoke-test",
            text="Какой отток за месяц?",
            object_id=TEST_OBJECT_ID,
        )
        plan = await planner.run_multi(question)
        ms = int((time.monotonic() - t0) * 1000)
        if plan.intent and plan.queries:
            return _step(
                "llm_planning", "PASS", ms,
                f"intent={plan.intent}, queries={len(plan.queries)}, topic={plan.topic}",
            )
        return _step(
            "llm_planning", "FAIL", ms,
            f"empty plan: intent={plan.intent!r}, queries={len(plan.queries)}",
        )
    except Exception as exc:
        ms = int((time.monotonic() - t0) * 1000)
        return _step("llm_planning", "FAIL", ms, str(exc)[:300])


# ── Step 7: Full E2E ────────────────────────────────────────────────────────

async def step_e2e(settings) -> StepResult:
    t0 = time.monotonic()
    try:
        from swarm_powerbi_bot.main import build_orchestrator
        from swarm_powerbi_bot.models import UserQuestion

        orchestrator = build_orchestrator(settings)
        question = UserQuestion(
            user_id="smoke-test",
            text="Покажи выручку за март",
            object_id=TEST_OBJECT_ID,
        )
        response = await orchestrator.handle_question(question)
        ms = int((time.monotonic() - t0) * 1000)

        checks = []
        if not response.answer:
            checks.append("empty answer")
        if response.topic == "unknown":
            checks.append("topic=unknown")
        if response.confidence not in ("low", "medium", "high"):
            checks.append(f"bad confidence={response.confidence!r}")

        if checks:
            return _step("e2e_cycle", "FAIL", ms, "; ".join(checks))
        return _step(
            "e2e_cycle", "PASS", ms,
            f"topic={response.topic}, confidence={response.confidence}, "
            f"answer_len={len(response.answer)}, has_image={response.image is not None}",
        )
    except Exception as exc:
        ms = int((time.monotonic() - t0) * 1000)
        return _step("e2e_cycle", "FAIL", ms, str(exc)[:300])


# ── Main ─────────────────────────────────────────────────────────────────────

async def run_smoke() -> dict:
    # Загружаем конфиг
    try:
        from swarm_powerbi_bot.config import Settings

        settings = Settings.from_env()
    except Exception as exc:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall": "CONFIG_ERROR",
            "error": str(exc),
            "steps": [],
            "aggregates": [],
            "summary": {},
        }

    conn_str = settings.sql_connection_string()
    catalog_path = settings.aggregate_catalog_path

    steps: list[StepResult] = []
    agg_results: list[dict] = []

    # Step 1: MSSQL connectivity
    logger.info("Step 1/7: MSSQL connectivity...")
    s1 = step_mssql_connectivity(conn_str)
    steps.append(s1)
    logger.info("  %s (%dms) %s", s1["status"], s1["duration_ms"], s1["detail"])

    mssql_ok = s1["status"] == "PASS"

    # Step 2: Procedures exist
    logger.info("Step 2/7: Procedures exist...")
    if mssql_ok:
        s2 = step_procedures_exist(conn_str)
    else:
        s2 = _step("procedures_exist", "SKIP", 0, "MSSQL not available")
    steps.append(s2)
    logger.info("  %s (%dms) %s", s2["status"], s2["duration_ms"], s2["detail"])

    # Step 3: Catalog validation
    logger.info("Step 3/7: Catalog validation...")
    s3, aggregates = step_catalog_validation(catalog_path)
    steps.append(s3)
    logger.info("  %s (%dms) %s", s3["status"], s3["duration_ms"], s3["detail"])

    # Step 4: Execute all aggregates
    logger.info("Step 4/7: Execute aggregates...")
    if mssql_ok and aggregates:
        s4, agg_results = await step_execute_aggregates(conn_str, catalog_path, aggregates)
    else:
        reason = "MSSQL not available" if not mssql_ok else "catalog not loaded"
        s4 = _step("execute_aggregates", "SKIP", 0, reason)
    steps.append(s4)
    logger.info("  %s (%dms) %s", s4["status"], s4["duration_ms"], s4["detail"])

    # Step 5: Ollama LLM health
    logger.info("Step 5/7: Ollama health...")
    s5 = step_ollama_health(settings.ollama_base_url, settings.ollama_model)
    steps.append(s5)
    logger.info("  %s (%dms) %s", s5["status"], s5["duration_ms"], s5["detail"])

    llm_ok = s5["status"] == "PASS"

    # Step 6: LLM planning
    logger.info("Step 6/7: LLM planning...")
    if llm_ok and mssql_ok:
        s6 = await step_llm_planning(settings)
    else:
        reason = []
        if not llm_ok:
            reason.append("LLM not available")
        if not mssql_ok:
            reason.append("MSSQL not available")
        s6 = _step("llm_planning", "SKIP", 0, "; ".join(reason))
    steps.append(s6)
    logger.info("  %s (%dms) %s", s6["status"], s6["duration_ms"], s6["detail"])

    # Step 7: Full E2E
    logger.info("Step 7/7: E2E cycle...")
    if llm_ok and mssql_ok:
        s7 = await step_e2e(settings)
    else:
        reason = []
        if not llm_ok:
            reason.append("LLM not available")
        if not mssql_ok:
            reason.append("MSSQL not available")
        s7 = _step("e2e_cycle", "SKIP", 0, "; ".join(reason))
    steps.append(s7)
    logger.info("  %s (%dms) %s", s7["status"], s7["duration_ms"], s7["detail"])

    # Summary
    passed = sum(1 for s in steps if s["status"] == "PASS")
    failed = sum(1 for s in steps if s["status"] == "FAIL")
    skipped = sum(1 for s in steps if s["status"] == "SKIP")
    agg_ok = sum(1 for a in agg_results if a["status"] == "ok")
    agg_err = sum(1 for a in agg_results if a["status"] != "ok")

    overall = "PASS" if failed == 0 else "FAIL"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "steps": steps,
        "aggregates": agg_results,
        "summary": {
            "total_steps": len(steps),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "aggregates_ok": agg_ok,
            "aggregates_error": agg_err,
        },
    }


def main() -> None:
    report = asyncio.run(run_smoke())
    print(json.dumps(report, ensure_ascii=False, indent=2))

    overall = report.get("overall", "FAIL")
    logger.info("Overall: %s", overall)

    if overall == "CONFIG_ERROR":
        sys.exit(2)
    elif overall == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
