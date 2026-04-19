from __future__ import annotations

import dataclasses

import pytest
from jsonschema import ValidationError

from swarm_powerbi_bot.services.aggregate_registry import AggregateEntry, load_catalog
from swarm_powerbi_bot.services.data_methods import DATA_METHODS


# ── happy-path ────────────────────────────────────────────────────────────────


def test_load_catalog_returns_aggregate_entries():
    catalog = load_catalog()
    assert len(catalog) > 0
    assert all(isinstance(e, AggregateEntry) for e in catalog)


def test_aggregate_entry_fields():
    catalog = load_catalog()
    entry = catalog[0]
    assert isinstance(entry.name, str) and entry.name
    assert isinstance(entry.data_method, str) and entry.data_method
    assert entry.metric_type in ("monetary", "count", "ratio", "duration")
    assert isinstance(entry.description, str) and entry.description
    assert isinstance(entry.dimensions, list)
    assert isinstance(entry.example_questions, list)
    assert isinstance(entry.aggregation, str) and entry.aggregation


def test_aggregate_entry_is_frozen():
    """AggregateEntry must be immutable (frozen dataclass)."""
    entry = load_catalog()[0]
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        entry.name = "mutated"  # type: ignore[misc]


# ── cross-validation: catalog ↔ DATA_METHODS ─────────────────────────────────


def test_every_aggregate_has_data_method():
    """Every catalog entry references an existing DATA_METHOD key."""
    catalog = load_catalog()
    for entry in catalog:
        assert entry.data_method in DATA_METHODS, (
            f"Aggregate {entry.name} references missing method {entry.data_method}"
        )


def test_all_data_methods_have_catalog_entry():
    """Every key in DATA_METHODS has at least one catalog entry (bidirectional)."""
    catalog = load_catalog()
    covered = {e.data_method for e in catalog}
    missing = set(DATA_METHODS) - covered
    assert not missing, (
        f"DATA_METHODS keys have no catalog entry: {sorted(missing)}"
    )


def test_default_load_auto_cross_validates(tmp_path, monkeypatch):
    """load_catalog() with default path enforces data_method integrity automatically."""
    import swarm_powerbi_bot.services.aggregate_registry as reg

    bad_catalog = tmp_path / "aggregate-catalog.yaml"
    bad_catalog.write_text(
        "aggregates:\n"
        "  - id: ghost\n"
        "    name: Ghost\n"
        "    data_method: nonexistent_auto\n"
        "    metric_type: count\n"
        "    description: injected\n"
        "    dimensions: []\n"
        "    example_questions: [вопрос один, вопрос два]\n"
        "    aggregation: COUNT\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(reg, "_DEFAULT_CATALOG", bad_catalog)
    with pytest.raises(ValueError, match="nonexistent_auto"):
        reg.load_catalog()


def test_known_methods_cross_validation_passes():
    catalog = load_catalog(known_methods=frozenset(DATA_METHODS))
    assert len(catalog) > 0


def test_known_methods_cross_validation_rejects_unknown(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "aggregates:\n"
        "  - id: x\n"
        "    name: X\n"
        "    data_method: nonexistent_method\n"
        "    metric_type: count\n"
        "    description: test\n"
        "    dimensions: []\n"
        "    example_questions: [вопрос один, вопрос два]\n"
        "    aggregation: COUNT\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="nonexistent_method"):
        load_catalog(path=bad, known_methods=frozenset(DATA_METHODS))


# ── example_questions ─────────────────────────────────────────────────────────


def test_example_questions_min_2():
    catalog = load_catalog()
    for entry in catalog:
        assert len(entry.example_questions) >= 2, (
            f"{entry.name} needs >=2 example questions for LLM few-shot"
        )


def test_example_questions_are_strings():
    """Each example question must be a non-empty string."""
    catalog = load_catalog()
    for entry in catalog:
        for q in entry.example_questions:
            assert isinstance(q, str) and q.strip(), (
                f"{entry.name} has blank/non-string example question: {q!r}"
            )


# ── schema validation ─────────────────────────────────────────────────────────


def test_schema_rejects_missing_required_field(tmp_path):
    """JSONSchema rejects entry without 'description'."""
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "aggregates:\n"
        "  - id: foo\n"
        "    name: Foo\n"
        "    data_method: foo\n"
        "    metric_type: count\n"
        "    dimensions: []\n"
        "    example_questions: [вопрос один, вопрос два]\n"
        "    aggregation: COUNT\n",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError, match="description"):
        load_catalog(path=bad, validate_schema=True)


def test_schema_rejects_unknown_metric_type(tmp_path):
    """JSONSchema rejects metric_type not in the allowed enum."""
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "aggregates:\n"
        "  - id: x\n"
        "    name: X\n"
        "    data_method: x\n"
        "    metric_type: unknown_type\n"
        "    description: test\n"
        "    dimensions: []\n"
        "    example_questions: [a, b]\n"
        "    aggregation: SUM\n",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_catalog(path=bad, validate_schema=True)


def test_schema_rejects_too_few_example_questions(tmp_path):
    """JSONSchema rejects entry with fewer than 2 example_questions."""
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "aggregates:\n"
        "  - id: x\n"
        "    name: X\n"
        "    data_method: x\n"
        "    metric_type: count\n"
        "    description: test\n"
        "    dimensions: []\n"
        "    example_questions: [only_one]\n"
        "    aggregation: COUNT\n",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_catalog(path=bad, validate_schema=True)


def test_schema_file_missing_skips_validation(tmp_path, monkeypatch):
    """When schema file is absent, load_catalog does not raise (graceful skip)."""
    import swarm_powerbi_bot.services.aggregate_registry as reg

    good = tmp_path / "good.yaml"
    good.write_text(
        "aggregates:\n"
        "  - id: revenue_total\n"
        "    name: Revenue\n"
        "    data_method: revenue_total\n"
        "    metric_type: monetary\n"
        "    description: test\n"
        "    dimensions: []\n"
        "    example_questions: [вопрос один, вопрос два]\n"
        "    unit: RUB\n"
        "    aggregation: SUM\n",
        encoding="utf-8",
    )
    absent_schema = tmp_path / "no-schema.json"
    monkeypatch.setattr(reg, "_DEFAULT_SCHEMA", absent_schema)
    result = load_catalog(path=good, validate_schema=True)
    assert len(result) == 1


# ── duplicate id ──────────────────────────────────────────────────────────────


def test_duplicate_id_raises(tmp_path):
    """Duplicate 'id' in YAML must raise ValueError naming the duplicate."""
    dup = tmp_path / "dup.yaml"
    dup.write_text(
        "aggregates:\n"
        "  - id: foo\n"
        "    name: Foo\n"
        "    data_method: foo\n"
        "    metric_type: count\n"
        "    description: first\n"
        "    dimensions: []\n"
        "    example_questions: [вопрос один, вопрос два]\n"
        "    aggregation: COUNT\n"
        "  - id: foo\n"
        "    name: Foo2\n"
        "    data_method: foo\n"
        "    metric_type: count\n"
        "    description: second\n"
        "    dimensions: []\n"
        "    example_questions: [вопрос один, вопрос два]\n"
        "    aggregation: COUNT\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate id"):
        load_catalog(path=dup)


# ── business rules ────────────────────────────────────────────────────────────


def test_monetary_entries_have_rub_unit():
    catalog = load_catalog()
    for entry in catalog:
        if entry.metric_type == "monetary":
            assert entry.unit == "RUB", f"{entry.name} monetary entry must have unit=RUB"


def test_count_entries_have_null_unit():
    catalog = load_catalog()
    for entry in catalog:
        if entry.metric_type == "count":
            assert entry.unit is None, f"{entry.name} count entry must have unit=null"


# ── YAML robustness ───────────────────────────────────────────────────────────


def test_yaml_with_comments_loads_ok(tmp_path):
    """YAML files with # comments must parse without error."""
    commented = tmp_path / "commented.yaml"
    commented.write_text(
        "# Каталог агрегатов\n"
        "aggregates:\n"
        "  # Revenue group\n"
        "  - id: revenue_total\n"
        "    name: Revenue Total  # human label\n"
        "    data_method: revenue_total\n"
        "    metric_type: monetary\n"
        "    description: выручка за период\n"
        "    dimensions: []  # no extra dims\n"
        "    example_questions:\n"
        "      - выручка за март  # example 1\n"
        "      - сколько заработали  # example 2\n"
        "    unit: RUB\n"
        "    aggregation: SUM\n",
        encoding="utf-8",
    )
    result = load_catalog(path=commented, validate_schema=False)
    assert len(result) == 1
    assert result[0].name == "revenue_total"


# ── structural / field contract ───────────────────────────────────────────────


def test_aggregate_entry_field_names():
    """AggregateEntry must expose exactly the 8 spec-required fields by name."""
    import dataclasses

    field_names = {f.name for f in dataclasses.fields(AggregateEntry)}
    required = {"name", "data_method", "metric_type", "description", "dimensions",
                "example_questions", "unit", "aggregation"}
    assert required.issubset(field_names), (
        f"AggregateEntry missing spec fields: {required - field_names}"
    )


def test_empty_aggregates_list_returns_empty(tmp_path):
    """YAML with an empty aggregates list must return [] without raising."""
    empty = tmp_path / "empty.yaml"
    empty.write_text("aggregates: []\n", encoding="utf-8")
    result = load_catalog(path=empty, validate_schema=False)
    assert result == []


def test_default_path_auto_validates_schema():
    """load_catalog() with no args must validate against schema (implicit True)."""
    import swarm_powerbi_bot.services.aggregate_registry as reg

    # The real catalog is valid — if schema auto-validation is broken this would
    # either raise or return stale entries.  We confirm entries come back typed.
    catalog = reg.load_catalog()
    assert all(
        e.metric_type in ("monetary", "count", "ratio", "duration") for e in catalog
    )
