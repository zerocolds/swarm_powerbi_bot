#!/usr/bin/env python3
"""T018: Validate SQL aggregates against their catalog definitions.

Usage:
    python scripts/bootstrap/validate_aggregates.py <aggregate_catalog_yaml> <sql_connection_string> [options]
    python scripts/bootstrap/validate_aggregates.py <aggregate_catalog_yaml> dry-run [options]

Options:
    --test-object-id INT   ObjectId used for live execution tests (default: 506770)
    --dax-baseline YAML    Optional YAML with DAX baseline values for numeric tolerance checks
    --fail-fast            Stop on first failure

For each aggregate in the catalog:
  1. Check that the stored procedure exists (INFORMATION_SCHEMA probe).
  2. Execute with test parameters and verify expected columns are returned.
  3. Verify row_count > 0 for the test ObjectId.
  4. If --dax-baseline provided, compare numeric columns with ≤1% tolerance.

If <sql_connection_string> is the literal string "dry-run", only the catalog
structure is validated (no database connection is made).
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# ---------------------------------------------------------------------------
# Catalog structure validation (dry-run / always performed first)
# ---------------------------------------------------------------------------

_REQUIRED_AGGREGATE_KEYS = ("id", "name", "parameters", "returns")


def _validate_catalog_structure(aggregates: list[dict]) -> list[str]:
    """Validate catalog YAML structure. Returns list of error strings."""
    errors: list[str] = []

    if not isinstance(aggregates, list):
        errors.append("'aggregates' must be a list")
        return errors

    seen_ids: set[str] = set()
    for idx, agg in enumerate(aggregates):
        prefix = f"[{idx}] id={agg.get('id', '<missing>')}"

        for key in _REQUIRED_AGGREGATE_KEYS:
            if key not in agg:
                errors.append(f"{prefix}: missing required key '{key}'")

        agg_id = agg.get("id")
        if agg_id:
            if agg_id in seen_ids:
                errors.append(f"{prefix}: duplicate id '{agg_id}'")
            seen_ids.add(agg_id)

        # Validate parameters list
        for pidx, param in enumerate(agg.get("parameters", [])):
            p_prefix = f"{prefix} param[{pidx}]"
            if "name" not in param:
                errors.append(f"{p_prefix}: missing 'name'")
            if "type" not in param:
                errors.append(f"{p_prefix}: missing 'type'")

        # Validate returns list
        returns = agg.get("returns", [])
        if not isinstance(returns, list) or len(returns) == 0:
            errors.append(f"{prefix}: 'returns' must be a non-empty list")

    return errors


# ---------------------------------------------------------------------------
# Live SQL validation helpers
# ---------------------------------------------------------------------------

def _build_test_params(aggregate: dict, object_id: int) -> dict[str, Any]:
    """Build a minimal set of test parameters for executing the procedure."""
    today = date.today()
    month_ago = today - timedelta(days=30)

    params: dict[str, Any] = {}
    for param in aggregate.get("parameters", []):
        name: str = param["name"]
        ptype: str = param.get("type", "str").lower()
        required: bool = param.get("required", True)
        default = param.get("default")

        if not required and default is not None:
            params[name] = default
            continue

        name_lower = name.lower()
        if "object_id" in name_lower or "salon" in name_lower:
            params[name] = object_id
        elif "date_from" in name_lower or name_lower == "datefrom":
            params[name] = month_ago.isoformat()
        elif "date_to" in name_lower or name_lower == "dateto":
            params[name] = today.isoformat()
        elif ptype in ("int", "integer"):
            params[name] = param.get("default", param.get("min", 1))
        elif ptype in ("date",):
            params[name] = today.isoformat()
        elif ptype in ("bool", "boolean", "bit"):
            params[name] = False
        else:
            params[name] = ""

    return params


def _expected_columns(aggregate: dict) -> list[str]:
    """Extract expected column names from the 'returns' field."""
    columns: list[str] = []
    for item in aggregate.get("returns", []):
        if isinstance(item, dict):
            columns.extend(item.keys())
        elif isinstance(item, str):
            columns.append(item)
    return columns


def _check_procedure_exists(cursor: Any, proc_name: str) -> bool:
    """Query INFORMATION_SCHEMA to check if a stored procedure exists."""
    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.ROUTINES "
        "WHERE ROUTINE_TYPE = 'PROCEDURE' AND ROUTINE_NAME = ?",
        (proc_name,),
    )
    row = cursor.fetchone()
    return bool(row and row[0] > 0)


def _derive_proc_name(aggregate: dict) -> str:
    """Derive a stored procedure name from the aggregate id."""
    agg_id: str = aggregate.get("id", "")
    # Convention: usp_<id> or sp_<id> — prefer explicit field if set
    return aggregate.get("proc_name", f"usp_{agg_id}")


def _percent_diff(a: float, b: float) -> float:
    """Relative difference, guard against division by zero."""
    if a == 0 and b == 0:
        return 0.0
    denom = max(abs(a), abs(b))
    return abs(a - b) / denom


def _load_baseline(path: Path) -> dict[str, dict[str, float]]:
    """Load DAX baseline YAML. Expected format: {<agg_id>: {<column>: value}}."""
    data = _load_yaml(path)
    return data if isinstance(data, dict) else {}


# ---------------------------------------------------------------------------
# Result helpers
# ---------------------------------------------------------------------------

class AggResult:
    def __init__(self, agg_id: str, name: str) -> None:
        self.agg_id = agg_id
        self.name = name
        self.passed = True
        self.issues: list[str] = []

    def fail(self, msg: str) -> None:
        self.passed = False
        self.issues.append(msg)

    def warn(self, msg: str) -> None:
        self.issues.append(f"WARN: {msg}")

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"  [{status}] {self.agg_id} — {self.name}"]
        for issue in self.issues:
            lines.append(f"         {issue}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dry-run validator
# ---------------------------------------------------------------------------

def _run_dry(aggregates: list[dict]) -> list[AggResult]:
    """Validate catalog structure only, no DB connection."""
    results: list[AggResult] = []
    struct_errors = _validate_catalog_structure(aggregates)
    if struct_errors:
        # Surface as a single synthetic result
        r = AggResult("<catalog>", "Catalog structure")
        for err in struct_errors:
            r.fail(err)
        results.append(r)
        return results

    for agg in aggregates:
        r = AggResult(agg.get("id", "?"), agg.get("name", ""))
        # Check expected columns parseable
        cols = _expected_columns(agg)
        if not cols:
            r.fail("'returns' resolved to zero columns")
        else:
            r.issues.append(f"columns: {', '.join(cols)}")
        # Check test params buildable
        params = _build_test_params(agg, 506770)
        required_params = [p["name"] for p in agg.get("parameters", []) if p.get("required", True)]
        missing = [p for p in required_params if p not in params]
        if missing:
            r.fail(f"Could not derive test values for required params: {missing}")
        else:
            r.issues.append(f"test params: {params}")
        results.append(r)

    return results


# ---------------------------------------------------------------------------
# Live SQL validator
# ---------------------------------------------------------------------------

def _run_live(
    aggregates: list[dict],
    conn_string: str,
    object_id: int,
    baseline: dict[str, dict[str, float]],
    fail_fast: bool,
) -> list[AggResult]:
    """Execute each aggregate against a real SQL Server and validate results."""
    try:
        import pyodbc  # type: ignore[import]
    except ImportError:
        print("ERROR: pyodbc is not installed. Install it with: uv add pyodbc", file=sys.stderr)
        sys.exit(1)

    # First validate structure
    struct_errors = _validate_catalog_structure(aggregates)
    if struct_errors:
        r = AggResult("<catalog>", "Catalog structure")
        for err in struct_errors:
            r.fail(err)
        return [r]

    try:
        conn = pyodbc.connect(conn_string, timeout=15)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Cannot connect to SQL Server: {exc}", file=sys.stderr)
        sys.exit(1)

    results: list[AggResult] = []
    try:
        with conn:
            cursor = conn.cursor()
            for agg in aggregates:
                r = AggResult(agg.get("id", "?"), agg.get("name", ""))
                proc_name = _derive_proc_name(agg)

                # 1. Check procedure exists
                try:
                    exists = _check_procedure_exists(cursor, proc_name)
                except Exception as exc:  # noqa: BLE001
                    r.fail(f"INFORMATION_SCHEMA query failed: {exc}")
                    results.append(r)
                    if fail_fast and not r.passed:
                        break
                    continue

                if not exists:
                    r.fail(f"Stored procedure '{proc_name}' not found in INFORMATION_SCHEMA")
                    results.append(r)
                    if fail_fast and not r.passed:
                        break
                    continue

                # 2. Execute with test parameters
                test_params = _build_test_params(agg, object_id)
                param_placeholders = ", ".join(f"@{k}=?" for k in test_params)
                exec_sql = f"EXEC {proc_name} {param_placeholders}"
                param_values = list(test_params.values())

                try:
                    cursor.execute(exec_sql, param_values)
                    columns_returned = [desc[0] for desc in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                except Exception as exc:  # noqa: BLE001
                    r.fail(f"Execution failed: {exc}")
                    results.append(r)
                    if fail_fast and not r.passed:
                        break
                    continue

                # 3. Verify expected columns present
                expected_cols = _expected_columns(agg)
                returned_lower = {c.lower() for c in columns_returned}
                missing_cols = [c for c in expected_cols if c.lower() not in returned_lower]
                if missing_cols:
                    r.fail(f"Missing expected columns: {missing_cols}")
                else:
                    r.issues.append(f"columns OK ({len(columns_returned)} returned)")

                # 4. Verify row_count > 0
                row_count = len(rows)
                if row_count == 0:
                    r.fail(f"No rows returned for object_id={object_id}")
                else:
                    r.issues.append(f"row_count={row_count} OK")

                # 5. DAX baseline comparison (if provided)
                agg_id = agg.get("id", "")
                if baseline and agg_id in baseline and rows and columns_returned:
                    col_idx = {c.lower(): i for i, c in enumerate(columns_returned)}
                    agg_baseline = baseline[agg_id]
                    for col_name, expected_val in agg_baseline.items():
                        if col_name.lower() not in col_idx:
                            r.warn(f"Baseline column '{col_name}' not in result set")
                            continue
                        # Compare first row value
                        actual_val = rows[0][col_idx[col_name.lower()]]
                        try:
                            diff = _percent_diff(float(expected_val), float(actual_val))
                            if diff > 0.01:
                                r.fail(
                                    f"Baseline mismatch '{col_name}': "
                                    f"expected={expected_val}, actual={actual_val}, "
                                    f"diff={diff:.2%} > 1%"
                                )
                            else:
                                r.issues.append(
                                    f"baseline '{col_name}': diff={diff:.2%} OK"
                                )
                        except (TypeError, ValueError):
                            r.warn(f"Cannot compare non-numeric baseline value for '{col_name}'")

                results.append(r)
                if fail_fast and not r.passed:
                    break
    finally:
        conn.close()

    return results


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def _print_report(results: list[AggResult], dry_run: bool) -> int:
    """Print results to stdout, return exit code (0 = all pass, 1 = failures)."""
    mode_label = "DRY-RUN" if dry_run else "LIVE"
    print(f"\n=== Aggregate Validation Report [{mode_label}] ===\n")

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    for r in results:
        print(str(r))

    print(f"\nTotal: {len(results)}  Passed: {passed}  Failed: {failed}")
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "T018: Validate SQL aggregates against their catalog definitions. "
            "Pass 'dry-run' as the connection string to skip DB and validate structure only."
        )
    )
    parser.add_argument("catalog_yaml", help="Path to aggregate catalog YAML")
    parser.add_argument(
        "sql_connection_string",
        help="pyodbc connection string, or the literal 'dry-run'",
    )
    parser.add_argument(
        "--test-object-id",
        type=int,
        default=506770,
        metavar="INT",
        help="ObjectId used for live SQL execution tests (default: 506770)",
    )
    parser.add_argument(
        "--dax-baseline",
        metavar="YAML",
        help="Path to YAML with DAX baseline values for numeric tolerance checks (≤1%%)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop validation on the first failure",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    catalog_path = Path(args.catalog_yaml)
    print(f"Loading catalog: {catalog_path}")
    catalog_data = _load_yaml(catalog_path)
    aggregates: list[dict] = catalog_data.get("aggregates", [])

    if not aggregates:
        print("WARNING: No aggregates found in catalog ('aggregates' list is empty).", file=sys.stderr)

    dry_run = args.sql_connection_string.strip().lower() == "dry-run"

    baseline: dict[str, dict[str, float]] = {}
    if args.dax_baseline:
        baseline_path = Path(args.dax_baseline)
        print(f"Loading DAX baseline: {baseline_path}")
        baseline = _load_baseline(baseline_path)

    if dry_run:
        print(f"Mode: DRY-RUN (catalog structure validation only, {len(aggregates)} aggregate(s))")
        results = _run_dry(aggregates)
    else:
        print(
            f"Mode: LIVE SQL (object_id={args.test_object_id}, "
            f"{len(aggregates)} aggregate(s))"
        )
        results = _run_live(
            aggregates,
            args.sql_connection_string,
            args.test_object_id,
            baseline,
            args.fail_fast,
        )

    exit_code = _print_report(results, dry_run)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
