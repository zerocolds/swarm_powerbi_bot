from __future__ import annotations

import logging
import re
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyYAML is required for aggregate_registry. Install it: uv add pyyaml"
    ) from exc

logger = logging.getLogger(__name__)

# ── constants ──────────────────────────────────────────────────────────────────

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_FILTER_VALUES = frozenset(
    {"all", "outflow", "leaving", "forecast", "noshow", "quality", "birthday"}
)


# ── helpers ────────────────────────────────────────────────────────────────────


def _is_date(value: object) -> bool:
    return isinstance(value, str) and bool(_DATE_RE.match(value))


def _load_catalog(path: str) -> dict[str, dict]:
    """Загружает YAML-каталог, возвращает {aggregate_id: entry}.

    Raises:
        FileNotFoundError: файл не найден
        yaml.YAMLError: невалидный YAML
        ValueError: запись без обязательного поля 'id'
    """
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.error("Catalog file not found: %s", path)
        raise
    except yaml.YAMLError as exc:
        logger.error("Invalid YAML in catalog %s: %s", path, exc)
        raise

    if not isinstance(raw, dict):
        logger.warning("Catalog %s has unexpected format, returning empty", path)
        return {}

    entries = raw.get("aggregates", [])
    result: dict[str, dict] = {}
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict) or "id" not in entry:
            raise ValueError(
                f"Catalog {path}: entry #{idx} missing required 'id' field: {entry!r}"
            )
        result[entry["id"]] = entry
    return result


def _validate_entry_params(
    aggregate_id: str,
    entry: dict,
    params: dict,
) -> tuple[bool, str]:
    """Общая валидация параметров для записи каталога."""
    allowed_group_by: list[str] = entry.get("allowed_group_by", [])

    for key, value in params.items():
        if key in ("date_from", "date_to"):
            if not _is_date(value):
                return False, f"{key} must be YYYY-MM-DD, got {value!r}"

        elif key == "object_id":
            if not isinstance(value, int):
                return False, f"object_id must be int, got {type(value).__name__}"

        elif key == "master_id":
            if value is not None and not isinstance(value, int):
                return (
                    False,
                    f"master_id must be int or None, got {type(value).__name__}",
                )

        elif key == "group_by":
            if value not in allowed_group_by:
                return False, (
                    f"group_by {value!r} not allowed for {aggregate_id!r}; "
                    f"allowed: {allowed_group_by}"
                )

        elif key == "filter":
            if value not in _FILTER_VALUES:
                return False, (
                    f"filter {value!r} not in allowed set {sorted(_FILTER_VALUES)}"
                )

        elif key == "top_n":
            if not isinstance(value, int) or not (1 <= value <= 50):
                return False, f"top_n must be int in [1, 50], got {value!r}"

    return True, ""


# ── module-level state (populated by load_catalog()) ──────────────────────────

_catalog: dict[str, dict] = {}


def load_catalog(path: str) -> None:
    """Загружает каталог агрегатов из YAML-файла. Вызывается при старте."""
    global _catalog
    _catalog = _load_catalog(path)


# ── public functions ───────────────────────────────────────────────────────────


def validate_aggregate_id(aggregate_id: str) -> bool:
    """True, если aggregate_id есть в загруженном каталоге."""
    return aggregate_id in _catalog


def validate_params(aggregate_id: str, params: dict) -> tuple[bool, str]:
    """Валидирует params для указанного агрегата.

    Возвращает (True, "") при успехе или (False, <причина>) при ошибке.
    """
    entry = _catalog.get(aggregate_id)
    if entry is None:
        return False, f"unknown aggregate_id: {aggregate_id!r}"
    return _validate_entry_params(aggregate_id, entry, params)


# ── Registry class ─────────────────────────────────────────────────────────────


class AggregateRegistry:
    def __init__(self, catalog_path: str) -> None:
        self._catalog: dict[str, dict] = _load_catalog(catalog_path)

    def get_aggregate(self, aggregate_id: str) -> dict | None:
        return self._catalog.get(aggregate_id)

    def validate(self, aggregate_id: str, params: dict) -> tuple[bool, str]:
        """Комбинирует проверку whitelist и параметров."""
        entry = self._catalog.get(aggregate_id)
        if entry is None:
            return False, f"unknown aggregate_id: {aggregate_id!r}"
        return _validate_entry_params(aggregate_id, entry, params)

    def list_aggregates(self) -> list[dict]:
        """Возвращает все агрегаты — используется при формировании LLM-промпта."""
        return list(self._catalog.values())
