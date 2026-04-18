from __future__ import annotations

import pytest
from jsonschema import ValidationError

from swarm_powerbi_bot.services.aggregate_registry import AggregateEntry, load_catalog
from swarm_powerbi_bot.services.data_methods import DATA_METHODS


def test_every_aggregate_has_data_method():
    catalog = load_catalog()
    for entry in catalog:
        assert entry.data_method in DATA_METHODS, (
            f"Aggregate {entry.name} references missing method {entry.data_method}"
        )


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


def test_example_questions_min_2():
    catalog = load_catalog()
    for entry in catalog:
        assert len(entry.example_questions) >= 2, (
            f"{entry.name} needs >=2 example questions for LLM few-shot"
        )


def test_schema_rejects_missing_required_field(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("aggregates:\n  - name: foo\n", encoding="utf-8")
    with pytest.raises(ValidationError, match="description"):
        load_catalog(path=bad, validate_schema=True)


def test_schema_rejects_unknown_metric_type(tmp_path):
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


def test_duplicate_id_raises(tmp_path):
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


def test_data_method_equals_name():
    catalog = load_catalog()
    for entry in catalog:
        assert entry.data_method == entry.name, (
            f"{entry.name}: data_method should equal id"
        )
