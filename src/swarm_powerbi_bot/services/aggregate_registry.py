from __future__ import annotations

import datetime
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyYAML is required for aggregate_registry. Install it: uv add pyyaml"
    ) from exc

try:
    import jsonschema
    from jsonschema import ValidationError
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "jsonschema is required for aggregate_registry. Install it: uv add jsonschema"
    ) from exc

logger = logging.getLogger(__name__)

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_FILTER_VALUES = frozenset(
    {"all", "outflow", "leaving", "forecast", "noshow", "quality", "birthday"}
)

_REASON_VALUES = frozenset(
    {"all", "outflow", "leaving", "forecast", "noshow", "quality", "birthday", "waitlist", "opz"}
)

_DEFAULT_CATALOG = Path(__file__).parents[3] / "catalogs" / "aggregate-catalog.yaml"
_DEFAULT_SCHEMA = Path(__file__).parents[3] / "catalogs" / "schemas" / "aggregate-catalog.schema.json"


@dataclass(frozen=True)
class AggregateEntry:
    name: str
    data_method: str
    metric_type: Literal["monetary", "count", "ratio", "duration"]
    description: str
    dimensions: list[str]
    example_questions: list[str]
    unit: str | None
    aggregation: str


def _is_date(value: object) -> bool:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _load_schema(schema_path: Path | None = None) -> dict | None:
    if schema_path is None:
        schema_path = _DEFAULT_SCHEMA
    if schema_path.exists():
        try:
            return json.loads(schema_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Could not load schema %s: %s", schema_path, exc)
    return None


def _validate_against_schema(raw: dict, path: Path) -> None:
    schema = _load_schema()
    if schema is None:
        return
    try:
        jsonschema.validate(instance=raw, schema=schema)
    except ValidationError as exc:
        raise ValidationError(
            f"Catalog {path} failed schema validation: {exc.message}",
            validator=exc.validator,
            path=exc.absolute_path,
            cause=exc.cause,
            context=exc.context,
            validator_value=exc.validator_value,
            instance=exc.instance,
            schema=exc.schema,
            schema_path=exc.absolute_schema_path,
        ) from exc


def _parse_entries(raw: dict, path: Path) -> tuple[dict[str, dict], list[AggregateEntry]]:
    entries = raw.get("aggregates", [])
    catalog: dict[str, dict] = {}
    aggregate_entries: list[AggregateEntry] = []
    seen_ids: dict[str, int] = {}

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict) or "id" not in entry:
            raise ValueError(
                f"Catalog {path}: entry #{idx} missing required 'id' field: {entry!r}"
            )
        entry_id = entry["id"]
        if entry_id in seen_ids:
            raise ValueError(
                f"Catalog {path}: duplicate id {entry_id!r} at entries "
                f"#{seen_ids[entry_id]} and #{idx}"
            )
        seen_ids[entry_id] = idx
        catalog[entry_id] = entry

        if "data_method" in entry:
            aggregate_entries.append(
                AggregateEntry(
                    name=entry_id,
                    data_method=entry["data_method"],
                    metric_type=entry.get("metric_type", "count"),
                    description=entry.get("description", ""),
                    dimensions=list(entry.get("dimensions", [])),
                    example_questions=list(entry.get("example_questions", [])),
                    unit=entry.get("unit"),
                    aggregation=entry.get("aggregation", "COUNT"),
                )
            )

    return catalog, aggregate_entries


def _load_raw(path: Path) -> dict:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.error("Catalog file not found: %s", path)
        raise
    except yaml.YAMLError as exc:
        logger.error("Invalid YAML in catalog %s: %s", path, exc)
        raise
    if not isinstance(raw, dict):
        logger.warning("Catalog %s has unexpected format, returning empty", path)
        return {"aggregates": []}
    return raw


# ── module-level state ────────────────────────────────────────────────────────

_catalog: dict[str, dict] = {}
_entries: list[AggregateEntry] = []


def _validate_data_method_refs(
    entries: list[AggregateEntry],
    known_methods: frozenset[str] | set[str],
    path: Path,
) -> None:
    errors = [
        f"  {e.name!r}: data_method={e.data_method!r} not in known_methods"
        for e in entries
        if e.data_method not in known_methods
    ]
    if errors:
        raise ValueError(
            f"Catalog {path}: data_method cross-validation failed:\n"
            + "\n".join(errors)
        )


def load_catalog(
    path: str | Path | None = None,
    *,
    validate_schema: bool | None = None,
    known_methods: frozenset[str] | set[str] | None = None,
) -> list[AggregateEntry]:
    """Load aggregate catalog from YAML.

    validate_schema defaults to True when loading the default catalog path,
    False when an explicit path is provided. Pass validate_schema=True to
    force schema validation on any path.

    When loading the default catalog (path=None), cross-validation against
    DATA_METHODS is always performed automatically. For custom paths, pass
    known_methods explicitly to opt in.

    Raises:
        FileNotFoundError: file not found
        yaml.YAMLError: invalid YAML
        jsonschema.ValidationError: schema validation failed
        ValueError: duplicate id, missing required field, or invalid data_method ref
    """
    global _catalog, _entries
    resolved = Path(path) if path is not None else _DEFAULT_CATALOG
    should_validate = (path is None) if validate_schema is None else validate_schema
    raw = _load_raw(resolved)
    if should_validate:
        _validate_against_schema(raw, resolved)
    _catalog, _entries = _parse_entries(raw, resolved)
    if path is None:
        from swarm_powerbi_bot.services.data_methods import DATA_METHODS  # noqa: PLC0415
        _validate_data_method_refs(_entries, frozenset(DATA_METHODS), resolved)
    elif known_methods is not None:
        _validate_data_method_refs(_entries, known_methods, resolved)
    return list(_entries)


# ── public functions (backward-compatible) ────────────────────────────────────


def validate_aggregate_id(aggregate_id: str) -> bool:
    return aggregate_id in _catalog


def validate_params(aggregate_id: str, params: dict) -> tuple[bool, str]:
    entry = _catalog.get(aggregate_id)
    if entry is None:
        return False, f"unknown aggregate_id: {aggregate_id!r}"
    return _validate_entry_params(aggregate_id, entry, params)


def _validate_entry_params(
    aggregate_id: str,
    entry: dict,
    params: dict,
) -> tuple[bool, str]:
    allowed_group_by: list[str] = entry.get("allowed_group_by", [])
    catalog_params: list[dict] = entry.get("parameters", [])
    for catalog_param in catalog_params:
        if catalog_param.get("required", False):
            param_name = catalog_param.get("name", "")
            if param_name and param_name not in params:
                return False, (
                    f"required param {param_name!r} missing for aggregate {aggregate_id!r}"
                )

    for key, value in params.items():
        if key in ("date_from", "date_to"):
            if not _is_date(value):
                return False, f"{key} must be YYYY-MM-DD, got {value!r}"
        elif key == "object_id":
            if not isinstance(value, int):
                return False, f"object_id must be int, got {type(value).__name__}"
        elif key == "master_id":
            if value is not None and not isinstance(value, int):
                return False, f"master_id must be int or None, got {type(value).__name__}"
        elif key == "group_by":
            if value not in allowed_group_by:
                return False, (
                    f"group_by {value!r} not allowed for {aggregate_id!r}; "
                    f"allowed: {allowed_group_by}"
                )
        elif key == "filter":
            if value not in _FILTER_VALUES:
                return False, f"filter {value!r} not in allowed set {sorted(_FILTER_VALUES)}"
        elif key == "reason":
            if value not in _REASON_VALUES:
                return False, f"reason {value!r} not in allowed set {sorted(_REASON_VALUES)}"
        elif key in ("top_n", "top"):
            if not isinstance(value, int) or not (1 <= value <= 50):
                return False, f"{key} must be int in [1, 50], got {value!r}"

    return True, ""


# ── Registry class ────────────────────────────────────────────────────────────


class AggregateRegistry:
    def __init__(self, catalog_path: str, *, validate_schema: bool = False) -> None:
        p = Path(catalog_path)
        raw = _load_raw(p)
        if validate_schema:
            _validate_against_schema(raw, p)
        self._catalog, self._entries = _parse_entries(raw, p)
        if validate_schema:
            from swarm_powerbi_bot.services.data_methods import DATA_METHODS  # noqa: PLC0415
            _validate_data_method_refs(self._entries, frozenset(DATA_METHODS), p)

    def get_aggregate(self, aggregate_id: str) -> dict | None:
        return self._catalog.get(aggregate_id)

    def validate(self, aggregate_id: str, params: dict) -> tuple[bool, str]:
        entry = self._catalog.get(aggregate_id)
        if entry is None:
            return False, f"unknown aggregate_id: {aggregate_id!r}"
        return _validate_entry_params(aggregate_id, entry, params)

    def list_aggregates(self) -> list[dict]:
        return list(self._catalog.values())

    def list_entries(self) -> list[AggregateEntry]:
        return list(self._entries)
