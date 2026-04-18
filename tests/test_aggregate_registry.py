"""Tests for swarm_powerbi_bot.services.aggregate_registry."""
from __future__ import annotations

import textwrap

import pytest

from swarm_powerbi_bot.services.aggregate_registry import (
    AggregateRegistry,
    load_catalog,
    validate_aggregate_id,
    validate_params,
)


# ── fixtures ──────────────────────────────────────────────────────────────────

CATALOG_YAML = textwrap.dedent("""\
    aggregates:
      - id: revenue_by_master
        name: Выручка по мастерам
        data_method: revenue_by_master
        metric_type: monetary
        description: "Выручка в разрезе мастеров"
        dimensions: [date, master_id]
        example_questions:
          - "топ мастеров по выручке"
          - "кто из мастеров заработал больше"
        unit: RUB
        aggregation: SUM
        allowed_group_by:
          - master
          - day
      - id: visits_by_object
        name: Визиты по объектам
        data_method: visits_by_object
        metric_type: count
        description: "Визиты по объектам"
        dimensions: [date]
        example_questions:
          - "визиты по объектам"
          - "сколько визитов в каждом объекте"
        unit: null
        aggregation: COUNT
        allowed_group_by:
          - object
          - week
""")


@pytest.fixture()
def catalog_path(tmp_path):
    path = tmp_path / "catalog.yaml"
    path.write_text(CATALOG_YAML, encoding="utf-8")
    return str(path)


@pytest.fixture()
def registry(catalog_path):
    return AggregateRegistry(catalog_path)


@pytest.fixture(autouse=True)
def _load_module_catalog(catalog_path):
    """Load module-level catalog for module-level function tests."""
    load_catalog(catalog_path)


# ── load_catalog / list_aggregates ────────────────────────────────────────────

class TestLoadCatalog:
    def test_loads_valid_yaml(self, registry):
        aggregates = registry.list_aggregates()
        assert len(aggregates) == 2

    def test_aggregate_ids_present(self, registry):
        ids = {a["id"] for a in registry.list_aggregates()}
        assert ids == {"revenue_by_master", "visits_by_object"}

    def test_list_aggregates_returns_all(self, registry):
        result = registry.list_aggregates()
        assert isinstance(result, list)
        assert all(isinstance(a, dict) for a in result)


# ── get_aggregate ─────────────────────────────────────────────────────────────

class TestGetAggregate:
    def test_known_id_returns_dict(self, registry):
        agg = registry.get_aggregate("revenue_by_master")
        assert isinstance(agg, dict)
        assert agg["id"] == "revenue_by_master"

    def test_unknown_id_returns_none(self, registry):
        assert registry.get_aggregate("nonexistent") is None


# ── validate_aggregate_id (module-level) ──────────────────────────────────────

class TestValidateAggregateId:
    def test_known_id_returns_true(self):
        assert validate_aggregate_id("revenue_by_master") is True

    def test_unknown_id_returns_false(self):
        assert validate_aggregate_id("ghost_aggregate") is False


# ── validate_params (module-level) ────────────────────────────────────────────

class TestValidateParams:
    def test_valid_date_from(self):
        ok, msg = validate_params("revenue_by_master", {"date_from": "2024-01-01"})
        assert ok is True
        assert msg == ""

    def test_valid_date_to(self):
        ok, msg = validate_params("revenue_by_master", {"date_to": "2024-12-31"})
        assert ok is True

    def test_invalid_date_format(self):
        ok, msg = validate_params("revenue_by_master", {"date_from": "01-01-2024"})
        assert ok is False
        assert "YYYY-MM-DD" in msg

    def test_invalid_date_non_string(self):
        ok, msg = validate_params("revenue_by_master", {"date_from": 20240101})
        assert ok is False

    # group_by is per-aggregate
    def test_group_by_allowed_for_aggregate(self):
        ok, msg = validate_params("revenue_by_master", {"group_by": "master"})
        assert ok is True

    def test_group_by_not_allowed_for_aggregate(self):
        # "object" is allowed for visits_by_object, NOT for revenue_by_master
        ok, msg = validate_params("revenue_by_master", {"group_by": "object"})
        assert ok is False
        assert "not allowed" in msg

    def test_group_by_allowed_for_other_aggregate(self):
        ok, msg = validate_params("visits_by_object", {"group_by": "object"})
        assert ok is True

    def test_group_by_checked_against_per_aggregate_list(self):
        # "day" is only in revenue_by_master, not in visits_by_object
        ok_r, _ = validate_params("revenue_by_master", {"group_by": "day"})
        ok_v, _ = validate_params("visits_by_object", {"group_by": "day"})
        assert ok_r is True
        assert ok_v is False

    def test_top_n_lower_bound(self):
        ok, _ = validate_params("revenue_by_master", {"top_n": 1})
        assert ok is True

    def test_top_n_upper_bound(self):
        ok, _ = validate_params("revenue_by_master", {"top_n": 50})
        assert ok is True

    def test_top_n_below_range(self):
        ok, msg = validate_params("revenue_by_master", {"top_n": 0})
        assert ok is False
        assert "top_n" in msg

    def test_top_n_above_range(self):
        ok, msg = validate_params("revenue_by_master", {"top_n": 51})
        assert ok is False
        assert "top_n" in msg

    def test_top_n_non_int(self):
        ok, msg = validate_params("revenue_by_master", {"top_n": "10"})
        assert ok is False

    def test_invalid_aggregate_id_rejected(self):
        ok, msg = validate_params("ghost_aggregate", {"date_from": "2024-01-01"})
        assert ok is False
        assert "unknown aggregate_id" in msg

    def test_empty_params_valid(self):
        ok, msg = validate_params("revenue_by_master", {})
        assert ok is True

    def test_master_id_none_accepted(self):
        ok, _ = validate_params("revenue_by_master", {"master_id": None})
        assert ok is True

    def test_master_id_int_accepted(self):
        ok, _ = validate_params("revenue_by_master", {"master_id": 42})
        assert ok is True

    def test_master_id_non_int_rejected(self):
        ok, msg = validate_params("revenue_by_master", {"master_id": "42"})
        assert ok is False
        assert "master_id" in msg


# ── AggregateRegistry.validate (class-level mirror) ──────────────────────────

class TestRegistryValidate:
    def test_valid_params(self, registry):
        ok, msg = registry.validate("revenue_by_master", {"date_from": "2024-06-01", "top_n": 10})
        assert ok is True

    def test_invalid_aggregate_id(self, registry):
        ok, msg = registry.validate("no_such", {})
        assert ok is False
        assert "unknown aggregate_id" in msg

    def test_group_by_per_aggregate(self, registry):
        ok_yes, _ = registry.validate("visits_by_object", {"group_by": "week"})
        ok_no, _ = registry.validate("visits_by_object", {"group_by": "master"})
        assert ok_yes is True
        assert ok_no is False
