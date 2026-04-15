#!/usr/bin/env python3
"""T017: Analyse mapping YAML produced by map_pbix_to_sql.py and generate a gap report.

Usage:
    python scripts/bootstrap/gap_analysis.py <pbix_to_sql_mapping_yaml> <output_gaps_md>

Reads mapping[].measures[].classification = sql_covered | python_postprocess | not_covered
and writes a Markdown gap report to <output_gaps_md> (default: catalogs/bootstrap/gaps.md).

Priority classification for not_covered measures:
  P1 (critical)        — revenue / выручк / amount keywords
  P2 (important)       — client / клиент / master / мастер keywords
  P3 (nice-to-have)    — everything else
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Priority keyword rules (applied to measure name + expression preview)
# ---------------------------------------------------------------------------

_P1_PATTERN = re.compile(
    r"\b(revenue|выручк|amount|сумм|выруч)\b",
    re.IGNORECASE | re.UNICODE,
)

_P2_PATTERN = re.compile(
    r"\b(client|клиент|master|мастер|customer|покупател)\b",
    re.IGNORECASE | re.UNICODE,
)


def _priority(measure_name: str, expression_preview: str) -> str:
    """Return P1 / P2 / P3 based on measure name and expression preview."""
    text = f"{measure_name} {expression_preview or ''}"
    if _P1_PATTERN.search(text):
        return "P1"
    if _P2_PATTERN.search(text):
        return "P2"
    return "P3"


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
# Markdown rendering
# ---------------------------------------------------------------------------

_PRIORITY_LABELS: dict[str, str] = {
    "P1": "P1 — critical (revenue / выручка / amount)",
    "P2": "P2 — important (client / клиент / master / мастер)",
    "P3": "P3 — nice-to-have",
}


def _render_markdown(
    not_covered: list[dict],
    stats: dict[str, int],
    source_path: Path,
) -> str:
    """Build the full Markdown gap report string."""
    lines: list[str] = []

    lines.append("# DAX Gap Report — Not-Covered Measures")
    lines.append("")
    lines.append(f"**Source mapping:** `{source_path}`")
    lines.append("")

    # Summary
    total = stats["total_measures"]
    nc = stats["not_covered"]
    pp = stats["python_postprocess"]
    sc = stats["sql_covered"]
    lines.append("## Summary")
    lines.append("")
    lines.append("| Classification       | Count | Share |")
    lines.append("|----------------------|------:|------:|")
    share = lambda n: f"{n / total * 100:.1f}%" if total else "—"  # noqa: E731
    lines.append(f"| sql_covered          | {sc:5} | {share(sc):>6} |")
    lines.append(f"| python_postprocess   | {pp:5} | {share(pp):>6} |")
    lines.append(f"| **not_covered**      | **{nc}** | **{share(nc)}** |")
    lines.append(f"| Total measures       | {total:5} |       |")
    lines.append("")

    if not not_covered:
        lines.append("_No gaps found — all measures are covered._")
        return "\n".join(lines)

    # Priority breakdown in summary
    p_counts: dict[str, int] = {"P1": 0, "P2": 0, "P3": 0}
    for item in not_covered:
        p_counts[item["priority"]] += 1

    lines.append("### Priority breakdown (not_covered only)")
    lines.append("")
    for key in ("P1", "P2", "P3"):
        lines.append(f"- **{key}**: {p_counts[key]} measure(s)")
    lines.append("")

    # Per-table groups
    lines.append("## Gaps by Source PBIX Table")
    lines.append("")

    # Group by table
    tables_seen: dict[str, list[dict]] = {}
    for item in not_covered:
        tables_seen.setdefault(item["pbix_table"], []).append(item)

    for table_name, measures in sorted(tables_seen.items()):
        lines.append(f"### {table_name}")
        lines.append("")
        lines.append("| Priority | Measure Name | Expression Preview |")
        lines.append("|----------|:-------------|:-------------------|")
        for m in sorted(measures, key=lambda x: x["priority"]):
            priority = m["priority"]
            name = m["name"].replace("|", "\\|")
            preview = (
                (m.get("expression_preview") or "")
                .replace("\n", " ")
                .replace("|", "\\|")
            )
            preview = preview[:100] + "…" if len(preview) > 100 else preview
            lines.append(f"| `{priority}` | {name} | `{preview}` |")
        lines.append("")

    # Per-priority sections
    for priority_key in ("P1", "P2", "P3"):
        bucket = [m for m in not_covered if m["priority"] == priority_key]
        if not bucket:
            continue
        lines.append(f"## {_PRIORITY_LABELS[priority_key]}")
        lines.append("")
        for item in bucket:
            preview = (item.get("expression_preview") or "").strip().replace("\n", " ")
            lines.append(f"- **{item['name']}** _(table: {item['pbix_table']})_")
            if preview:
                lines.append("  ```")
                lines.append(f"  {preview[:200]}")
                lines.append("  ```")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(
            "Usage: python scripts/bootstrap/gap_analysis.py "
            "<pbix_to_sql_mapping_yaml> [<output_gaps_md>]",
            file=sys.stderr,
        )
        sys.exit(1)

    mapping_path = Path(sys.argv[1])
    output_path = (
        Path(sys.argv[2]) if len(sys.argv) == 3 else Path("catalogs/bootstrap/gaps.md")
    )

    print(f"Loading mapping: {mapping_path}")
    data = _load_yaml(mapping_path)

    mapping: list[dict] = data.get("mapping", [])
    if not mapping:
        print(
            "WARNING: 'mapping' key is empty or missing in the input YAML.",
            file=sys.stderr,
        )

    # Collect stats and not_covered items
    stats: dict[str, int] = {
        "total_measures": 0,
        "sql_covered": 0,
        "python_postprocess": 0,
        "not_covered": 0,
    }
    not_covered: list[dict] = []

    for table_entry in mapping:
        pbix_table: str = table_entry.get("pbix_table", "<unknown>")
        for measure in table_entry.get("measures", []):
            classification: str = measure.get("classification", "not_covered")
            stats["total_measures"] += 1
            if classification in stats:
                stats[classification] += 1
            else:
                # Treat unknown classifications as not_covered
                stats["not_covered"] += 1

            if classification == "not_covered":
                name: str = measure.get("name", "")
                preview: str = measure.get("expression_preview") or ""
                not_covered.append(
                    {
                        "pbix_table": pbix_table,
                        "name": name,
                        "expression_preview": preview,
                        "priority": _priority(name, preview),
                    }
                )

    print(
        f"Measures — total: {stats['total_measures']}, "
        f"sql_covered: {stats['sql_covered']}, "
        f"python_postprocess: {stats['python_postprocess']}, "
        f"not_covered: {stats['not_covered']}"
    )

    p_counts = {"P1": 0, "P2": 0, "P3": 0}
    for item in not_covered:
        p_counts[item["priority"]] += 1
    print(
        f"Not-covered priorities — P1: {p_counts['P1']}, P2: {p_counts['P2']}, P3: {p_counts['P3']}"
    )

    markdown = _render_markdown(not_covered, stats, mapping_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Gap report written to: {output_path}")


if __name__ == "__main__":
    main()
