#!/usr/bin/env python3
"""T013: Map PBIX semantic model to existing SQL procedures/views.

Usage:
    python scripts/bootstrap/map_pbix_to_sql.py <semantic_model_yaml> <sql_file> <output_yaml>

For each PBIX table, finds the matching SQL table/view/procedure.
For each DAX measure, classifies as:
  - sql_covered       — an SQL proc/view covers this metric directly
  - python_postprocess — data is available in SQL but needs Python aggregation
  - not_covered       — no SQL equivalent found
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


# Regex patterns for SQL object names
_PROC_PATTERN = re.compile(
    r"(?:CREATE|ALTER)\s+(?:OR\s+ALTER\s+)?(?:PROCEDURE|PROC|VIEW|FUNCTION)\s+"
    r"(?:\[?[\w]+\]?\.)?\[?([\w]+)\]?",
    re.IGNORECASE,
)

# Simple token extraction for table-like names
_TABLE_REF_PATTERN = re.compile(r"\b(?:FROM|JOIN|INTO)\s+(?:\[?[\w]+\]?\.)?\[?([\w]+)\]?", re.IGNORECASE)


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _load_sql(path: Path) -> str:
    if not path.exists():
        print(f"ERROR: SQL file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_sql_objects(sql_text: str) -> dict[str, list[str]]:
    """Return dict of object_name -> list of referenced table names."""
    # Split on GO boundaries or procedure/view definitions
    objects: dict[str, list[str]] = {}
    current_name: str | None = None
    current_refs: list[str] = []

    for line in sql_text.splitlines():
        proc_match = _PROC_PATTERN.search(line)
        if proc_match:
            if current_name:
                objects[current_name] = current_refs
            current_name = proc_match.group(1).lower()
            current_refs = []

        if current_name:
            for ref in _TABLE_REF_PATTERN.findall(line):
                current_refs.append(ref.lower())

    if current_name:
        objects[current_name] = current_refs

    # Also collect all procedure/view names as flat list (for matching even if body wasn't parsed)
    all_names = list(_PROC_PATTERN.findall(sql_text))
    for name in all_names:
        key = name.lower()
        if key not in objects:
            objects[key] = []

    return objects


def _normalize(name: str) -> str:
    """Lowercase, strip kdo/vw/fn prefixes and underscores for fuzzy match."""
    n = name.lower()
    n = re.sub(r"^(vw|fn|sp|usp|tb|kdo|_)+", "", n)
    n = n.replace("_", "").replace(" ", "")
    return n


def _find_sql_match(table_name: str, sql_objects: dict[str, list[str]]) -> str | None:
    """Find best matching SQL object name for a PBIX table name."""
    norm_table = _normalize(table_name)
    best: str | None = None
    best_score = 0

    for obj_name in sql_objects:
        norm_obj = _normalize(obj_name)
        # Substring match scoring
        if norm_table in norm_obj or norm_obj in norm_table:
            score = len(set(norm_table) & set(norm_obj))
            if score > best_score:
                best_score = score
                best = obj_name

    return best


def _dax_contains_aggregation(expression: str) -> bool:
    """Heuristic: DAX measure uses aggregation that SQL might not pre-compute."""
    agg_funcs = re.compile(
        r"\b(CALCULATE|FILTER|ALL|ALLEXCEPT|DIVIDE|SUMX|AVERAGEX|COUNTX|RANKX|TOPN"
        r"|EARLIER|RELATED|RELATEDTABLE|USERELATIONSHIP|KEEPFILTERS|REMOVEFILTERS"
        r"|DATEADD|DATESYTD|DATESMTD|DATESQTD|PREVIOUSMONTH|PREVIOUSYEAR"
        r"|SWITCH|IF|BLANK|ISBLANK|HASONEVALUE|SELECTEDVALUE)\s*\(",
        re.IGNORECASE,
    )
    return bool(agg_funcs.search(expression))


def _classify_measure(
    measure: dict,
    table_match: str | None,
    sql_objects: dict[str, list[str]],
) -> str:
    """Classify a DAX measure into sql_covered / python_postprocess / not_covered."""
    expression: str = measure.get("expression", "")

    if table_match is None:
        return "not_covered"

    # Check if the SQL object references the source table
    has_data = bool(sql_objects.get(table_match))

    if not has_data:
        return "not_covered"

    if _dax_contains_aggregation(expression):
        return "python_postprocess"

    return "sql_covered"


def main() -> None:
    if len(sys.argv) != 4:
        print(
            "Usage: python scripts/bootstrap/map_pbix_to_sql.py "
            "<semantic_model_yaml> <sql_file> <output_yaml>",
            file=sys.stderr,
        )
        sys.exit(1)

    model_path = Path(sys.argv[1])
    sql_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    print(f"Loading semantic model: {model_path}")
    model = _load_yaml(model_path)

    print(f"Loading SQL file: {sql_path}")
    sql_text = _load_sql(sql_path)
    sql_objects = _extract_sql_objects(sql_text)
    print(f"Found {len(sql_objects)} SQL objects: {', '.join(list(sql_objects.keys())[:10])}{'...' if len(sql_objects) > 10 else ''}")

    tables_out = []
    stats = {"sql_covered": 0, "python_postprocess": 0, "not_covered": 0}

    for table in model.get("tables", []):
        tname: str = table.get("name", "")
        sql_match = _find_sql_match(tname, sql_objects)

        measures_out = []
        for measure in table.get("measures", []):
            classification = _classify_measure(measure, sql_match, sql_objects)
            stats[classification] += 1
            measures_out.append(
                {
                    "name": measure.get("name", ""),
                    "classification": classification,
                    "expression_preview": (measure.get("expression", "")[:120].strip() or None),
                }
            )

        entry: dict = {
            "pbix_table": tname,
            "sql_match": sql_match,
        }
        if measures_out:
            entry["measures"] = measures_out
        tables_out.append(entry)

    output: dict = {
        "mapping": tables_out,
        "summary": {
            "total_tables": len(tables_out),
            "sql_objects_found": len(sql_objects),
            "measures": stats,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        yaml.dump(output, fh, allow_unicode=True, sort_keys=False, default_flow_style=False)

    print(
        f"Done. Mapped {len(tables_out)} tables. Measures — "
        f"sql_covered: {stats['sql_covered']}, "
        f"python_postprocess: {stats['python_postprocess']}, "
        f"not_covered: {stats['not_covered']}"
    )
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
