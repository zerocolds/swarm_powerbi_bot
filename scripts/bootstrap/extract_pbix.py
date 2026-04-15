#!/usr/bin/env python3
"""T012: Extract DataModelSchema from a PBIX file and output as YAML.

Usage:
    python scripts/bootstrap/extract_pbix.py <pbix_path> <output_yaml_path>
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import yaml


# Candidate paths for DataModelSchema inside the ZIP archive.
_SCHEMA_CANDIDATES = [
    "DataModelSchema",
    "DataModel/DataModelSchema",
]


def _detect_encoding(data: bytes) -> str:
    """Detect UTF-16 LE BOM or fall back to UTF-8."""
    if data[:2] == b"\xff\xfe":
        return "utf-16-le"
    if data[:2] == b"\xfe\xff":
        return "utf-16-be"
    return "utf-8"


def _load_schema(pbix_path: Path) -> dict:
    """Open the PBIX ZIP and parse DataModelSchema JSON.

    Supports two PBIX formats:
    1. Newer PBIX with ``DataModelSchema`` entry (JSON) — parsed directly.
    2. Older PBIX with binary ``DataModel`` (ABF) — model reconstructed from
       ``Report/Layout`` visual configs (entities, measures, columns).
    """
    if not pbix_path.exists():
        print(f"ERROR: File not found: {pbix_path}", file=sys.stderr)
        sys.exit(1)

    try:
        zf = zipfile.ZipFile(pbix_path, "r")
    except zipfile.BadZipFile:
        print(f"ERROR: Not a valid PBIX/ZIP file: {pbix_path}", file=sys.stderr)
        sys.exit(1)

    with zf:
        names = zf.namelist()
        schema_name: str | None = None
        for candidate in _SCHEMA_CANDIDATES:
            if candidate in names:
                schema_name = candidate
                break

        if schema_name is not None:
            raw: bytes = zf.read(schema_name)
            encoding = _detect_encoding(raw)
            if encoding in ("utf-16-le", "utf-16-be"):
                raw = raw[2:]
            try:
                text = raw.decode(encoding)
            except UnicodeDecodeError as exc:
                print(f"ERROR: Failed to decode schema as {encoding}: {exc}", file=sys.stderr)
                sys.exit(1)
            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                print(f"ERROR: Invalid JSON in DataModelSchema: {exc}", file=sys.stderr)
                sys.exit(1)

        # Fallback: reconstruct model from Report/Layout visual configs
        if "Report/Layout" not in names:
            print(
                "ERROR: Neither DataModelSchema nor Report/Layout found in PBIX.",
                file=sys.stderr,
            )
            sys.exit(1)

        print("DataModelSchema not found — extracting model from Report/Layout...")
        layout_raw = zf.read("Report/Layout")
        # Report/Layout is typically UTF-16 LE (with or without BOM)
        for enc in ("utf-16-le", "utf-16", "utf-8"):
            try:
                layout_text = layout_raw.decode(enc)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            print("ERROR: Cannot decode Report/Layout", file=sys.stderr)
            sys.exit(1)
        return _reconstruct_from_layout(json.loads(layout_text))


def _reconstruct_from_layout(layout: dict) -> dict:
    """Reconstruct a pseudo-DataModelSchema from Report/Layout visual configs.

    Parses nested JSON in visual container configs/dataTransforms to extract
    Entity (table) references and Property (column/measure) references.
    """
    entities: dict[str, dict[str, set[str]]] = {}  # table -> {columns, measures}

    def _find_refs(obj: object) -> None:
        if isinstance(obj, str):
            try:
                _find_refs(json.loads(obj))
            except (json.JSONDecodeError, RecursionError):
                pass
        elif isinstance(obj, dict):
            # Direct Entity reference
            entity = obj.get("Entity")
            if isinstance(entity, str) and entity:
                entities.setdefault(entity, {"columns": set(), "measures": set()})

            # Column/Measure with Expression.SourceRef.Entity + Property
            prop = obj.get("Property")
            if isinstance(prop, str) and "Expression" in obj:
                expr = obj.get("Expression", {})
                src = expr.get("SourceRef", {})
                tbl = src.get("Entity", "")
                if tbl:
                    entities.setdefault(tbl, {"columns": set(), "measures": set()})
                    # Heuristic: if parent key is "Measure" → measure, else column
                    entities[tbl]["columns"].add(prop)

            # Measure expression at top level
            if "Measure" in obj and isinstance(obj["Measure"], dict):
                m = obj["Measure"]
                m_expr = m.get("Expression", {})
                m_src = m_expr.get("SourceRef", {})
                m_tbl = m_src.get("Entity", "")
                m_prop = m.get("Property", "")
                if m_tbl and m_prop:
                    entities.setdefault(m_tbl, {"columns": set(), "measures": set()})
                    entities[m_tbl]["measures"].add(m_prop)

            for v in obj.values():
                _find_refs(v)
        elif isinstance(obj, list):
            for item in obj:
                _find_refs(item)

    for section in layout.get("sections", []):
        for vc in section.get("visualContainers", []):
            for key in ("config", "dataTransforms", "filters", "query"):
                val = vc.get(key, "")
                if isinstance(val, str) and val:
                    _find_refs(val)

    # Build pseudo-schema
    tables = []
    for tbl_name, refs in sorted(entities.items()):
        cols = [{"name": c, "type": "string"} for c in sorted(refs["columns"])]
        measures = [{"name": m, "expression": "(extracted from visual config)"} for m in sorted(refs["measures"])]
        entry: dict = {"name": tbl_name, "columns": cols}
        if measures:
            entry["measures"] = measures
        tables.append(entry)

    return {"model": {"tables": tables, "relationships": []}}


def _extract_columns(table: dict) -> list[dict]:
    """Extract columns with name and data type."""
    columns = []
    for col in table.get("columns", []):
        name = col.get("name", "")
        # Skip hidden/internal columns (row number, etc.)
        if col.get("type") == "rowNumber":
            continue
        data_type = col.get("dataType", "string")
        entry: dict = {"name": name, "type": data_type}
        if col.get("isHidden"):
            entry["hidden"] = True
        if col.get("formatString"):
            entry["format"] = col["formatString"]
        columns.append(entry)
    return columns


def _extract_measures(table: dict) -> list[dict]:
    """Extract measures with name and DAX expression."""
    measures = []
    for m in table.get("measures", []):
        name = m.get("name", "")
        expression = m.get("expression", "").strip()
        entry: dict = {"name": name, "expression": expression}
        if m.get("formatString"):
            entry["format"] = m["formatString"]
        if m.get("isHidden"):
            entry["hidden"] = True
        measures.append(entry)
    return measures


def _extract_hierarchies(table: dict) -> list[dict]:
    """Extract hierarchies from a table."""
    hierarchies = []
    for h in table.get("hierarchies", []):
        levels = [
            {"name": lv.get("name", ""), "column": lv.get("column", "")}
            for lv in h.get("levels", [])
        ]
        hierarchies.append({"name": h.get("name", ""), "levels": levels})
    return hierarchies


def _build_output(schema: dict) -> dict:
    """Build the structured YAML output from the parsed schema."""
    model: dict = schema.get("model", schema)  # some PBIX wrap under "model"

    tables_out = []
    all_hierarchies = []

    for table in model.get("tables", []):
        tname = table.get("name", "")
        # Skip internal Power BI date tables
        if tname.startswith("DateTableTemplate") or tname.startswith("LocalDateTable"):
            continue

        columns = _extract_columns(table)
        measures = _extract_measures(table)
        hierarchies = _extract_hierarchies(table)

        entry: dict = {"name": tname, "columns": columns}
        if measures:
            entry["measures"] = measures
        if hierarchies:
            entry["hierarchies"] = hierarchies
            all_hierarchies.extend(
                [{"table": tname, **h} for h in hierarchies]
            )
        tables_out.append(entry)

    relationships_out = []
    for rel in model.get("relationships", []):
        relationships_out.append(
            {
                "from_table": rel.get("fromTable", ""),
                "from_column": rel.get("fromColumn", ""),
                "to_table": rel.get("toTable", ""),
                "to_column": rel.get("toColumn", ""),
                "cardinality": rel.get("crossFilteringBehavior", "oneToMany"),
                "active": rel.get("isActive", True),
            }
        )

    return {
        "tables": tables_out,
        "relationships": relationships_out,
        "hierarchies": all_hierarchies,
    }


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: python scripts/bootstrap/extract_pbix.py <pbix_path> <output_yaml_path>",
            file=sys.stderr,
        )
        sys.exit(1)

    pbix_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    print(f"Reading PBIX: {pbix_path}")
    schema = _load_schema(pbix_path)

    print("Extracting model...")
    output = _build_output(schema)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        yaml.dump(output, fh, allow_unicode=True, sort_keys=False, default_flow_style=False)

    tables_count = len(output["tables"])
    measures_count = sum(len(t.get("measures", [])) for t in output["tables"])
    rels_count = len(output["relationships"])
    print(
        f"Done. Tables: {tables_count}, measures: {measures_count}, relationships: {rels_count}"
    )
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
