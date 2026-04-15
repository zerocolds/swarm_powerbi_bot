#!/usr/bin/env python3
"""T014: Generate runtime semantic catalog from a PBIX semantic model YAML.

Usage:
    python scripts/bootstrap/generate_semantic_catalog.py <semantic_model_yaml> <output_yaml>

The output contains business entities, rules, and relationships described
in Russian, suitable for LLM planning context.
No SQL code, table names, or connection strings are included.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# Mapping from common English Power BI data types to Russian business labels
_TYPE_LABELS: dict[str, str] = {
    "int64": "целое число",
    "double": "число с плавающей точкой",
    "decimal": "денежная сумма",
    "string": "текст",
    "boolean": "да/нет",
    "dateTime": "дата и время",
    "date": "дата",
    "binary": "бинарные данные",
}


def _ru_type(dtype: str) -> str:
    return _TYPE_LABELS.get(dtype, dtype)


def _is_id_column(name: str) -> bool:
    """Heuristic: column is likely a surrogate/foreign key."""
    lower = name.lower()
    return lower.endswith("id") or lower.endswith("_id") or lower == "id"


def _infer_business_name(name: str) -> str:
    """Convert PascalCase/snake_case column names to readable Russian hints.

    This is a best-effort helper; the catalog is meant to be reviewed
    and enriched manually after generation.
    """
    # Split on CamelCase boundaries and underscores
    tokens = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    tokens = tokens.replace("_", " ").lower().strip()
    return tokens


def _build_entity(table: dict) -> dict:
    """Build a business entity description from a model table."""
    tname: str = table.get("name", "")
    columns: list[dict] = table.get("columns", [])
    measures: list[dict] = table.get("measures", [])

    attributes = []
    for col in columns:
        if col.get("hidden"):
            continue
        col_name: str = col.get("name", "")
        col_type: str = col.get("type", col.get("dataType", "string"))
        attr: dict = {
            "attribute": col_name,
            "type": _ru_type(col_type),
        }
        if _is_id_column(col_name):
            attr["role"] = "identifier"
        attributes.append(attr)

    kpis = []
    for m in measures:
        if m.get("hidden"):
            continue
        kpis.append(
            {
                "name": m.get("name", ""),
                "description": f"Вычисляемый показатель: {_infer_business_name(m.get('name', ''))}",
            }
        )

    entity: dict = {
        "entity": tname,
        "description": f"Бизнес-сущность: {_infer_business_name(tname)}",
        "attributes": attributes,
    }
    if kpis:
        entity["kpis"] = kpis
    return entity


def _build_relationships(raw_rels: list[dict]) -> list[dict]:
    """Convert raw relationship dicts to human-readable business rules."""
    rules = []
    for rel in raw_rels:
        if not rel.get("active", True):
            continue
        rule = {
            "from": rel.get("from_table", ""),
            "to": rel.get("to_table", ""),
            "via": f"{rel.get('from_column', '')} → {rel.get('to_column', '')}",
            "cardinality": rel.get("cardinality", "oneToMany"),
            "business_rule": (
                f"Каждая запись «{rel.get('from_table', '')}» связана с "
                f"«{rel.get('to_table', '')}» через поле «{rel.get('from_column', '')}»."
            ),
        }
        rules.append(rule)
    return rules


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: python scripts/bootstrap/generate_semantic_catalog.py "
            "<semantic_model_yaml> <output_yaml>",
            file=sys.stderr,
        )
        sys.exit(1)

    model_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    print(f"Loading semantic model: {model_path}")
    model = _load_yaml(model_path)

    tables: list[dict] = model.get("tables", [])
    relationships: list[dict] = model.get("relationships", [])

    print(f"Processing {len(tables)} tables, {len(relationships)} relationships...")

    entities = [_build_entity(t) for t in tables]
    business_rules = _build_relationships(relationships)

    # Collect all unique measure names as domain concepts
    all_kpis: list[str] = []
    for t in tables:
        for m in t.get("measures", []):
            if not m.get("hidden") and m.get("name"):
                all_kpis.append(m["name"])

    output: dict = {
        "version": "1.0",
        "description": (
            "Семантический каталог бизнес-сущностей и правил, "
            "автоматически сгенерированный из модели данных Power BI."
        ),
        "entities": entities,
        "business_rules": business_rules,
        "domain_concepts": {
            "kpis": all_kpis,
            "note": (
                "Показатели вычисляются на стороне аналитического слоя. "
                "Для получения данных используйте семантические агрегаты."
            ),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        yaml.dump(output, fh, allow_unicode=True, sort_keys=False, default_flow_style=False)

    print(
        f"Done. Entities: {len(entities)}, "
        f"business rules: {len(business_rules)}, "
        f"KPIs: {len(all_kpis)}"
    )
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
