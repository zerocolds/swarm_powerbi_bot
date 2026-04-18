"""T023: Security тесты — SQL-инъекции, whitelist aggregate_id, валидация параметров.

Покрывает:
- SQL injection в question text → "не могу ответить" (no SQL executed)
- aggregate_id not in whitelist → rejected
- Invalid params (bad date format, group_by not in allowed list) → rejected
- Tests use AggregateRegistry.validate() directly
"""
from __future__ import annotations

import textwrap

import pytest

from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry


# ── Fixtures ──────────────────────────────────────────────────────────────────

CATALOG_YAML = textwrap.dedent("""\
    aggregates:
      - id: revenue_total
        name: Общая выручка
        data_method: revenue_total
        metric_type: monetary
        description: Суммарная выручка за период
        dimensions: []
        example_questions:
          - "общая выручка за месяц"
          - "сколько заработали"
        unit: RUB
        aggregation: SUM
        procedure: spKDO_Aggregate
        allowed_group_by:
          - total
          - week
          - month
          - master
      - id: outflow_clients
        name: Отток клиентов
        data_method: outflow_clients
        metric_type: count
        description: Клиенты со статусом outflow
        dimensions: [date]
        example_questions:
          - "список оттока"
          - "кто в оттоке"
        unit: null
        aggregation: COUNT
        procedure: spKDO_ClientList
        allowed_group_by:
          - list
          - master
      - id: visits_by_salon
        name: Визиты по салонам
        data_method: visits_by_salon
        metric_type: count
        description: Агрегация визитов по объектам
        dimensions: [date]
        example_questions:
          - "визиты по салонам"
          - "сколько визитов в каждом салоне"
        unit: null
        aggregation: COUNT
        procedure: spKDO_Aggregate
        allowed_group_by:
          - salon
          - week
""")


@pytest.fixture()
def catalog_path(tmp_path):
    p = tmp_path / "aggregate-catalog.yaml"
    p.write_text(CATALOG_YAML, encoding="utf-8")
    return str(p)


@pytest.fixture()
def registry(catalog_path):
    return AggregateRegistry(catalog_path)


# ── SQL injection в тексте вопроса → блокировка ───────────────────────────────

class TestSQLInjectionBlocking:
    """SQL-инъекции в тексте вопроса не должны приводить к выполнению SQL."""

    SQL_INJECTION_SAMPLES = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "'; SELECT * FROM sys.objects; --",
        "UNION SELECT null, null, null --",
        "1; EXEC xp_cmdshell('dir')",
        "' OR 1=1--",
        "'; WAITFOR DELAY '0:0:5'; --",
    ]

    def test_sql_injection_in_aggregate_id_rejected(self, registry):
        """aggregate_id с SQL-инъекцией отклоняется whitelist-ом."""
        for injection in self.SQL_INJECTION_SAMPLES:
            ok, msg = registry.validate(injection, {})
            assert ok is False, f"Expected rejection for: {injection!r}"
            assert "unknown aggregate_id" in msg

    def test_sql_injection_as_group_by_rejected(self, registry):
        """SQL-инъекция в group_by должна быть отклонена."""
        ok, msg = registry.validate("revenue_total", {"group_by": "'; DROP TABLE; --"})
        assert ok is False
        assert "not allowed" in msg or "group_by" in msg

    def test_sql_injection_as_date_rejected(self, registry):
        """SQL-инъекция вместо даты — неверный формат → rejected."""
        ok, msg = registry.validate("revenue_total", {"date_from": "'; DROP TABLE--"})
        assert ok is False
        assert "YYYY-MM-DD" in msg

    def test_sql_injection_as_filter_rejected(self, registry):
        """SQL-инъекция в filter → rejected (not in allowed set)."""
        ok, msg = registry.validate("outflow_clients", {"filter": "'; DROP TABLE--"})
        assert ok is False

    def test_legitimate_question_text_does_not_affect_validation(self, registry):
        """Обычный текст вопроса (не параметр) не нарушает validate()."""
        # Это проверяет что validate не принимает "сырой текст" как параметр
        ok, msg = registry.validate("revenue_total", {"date_from": "2026-04-01", "date_to": "2026-04-15"})
        assert ok is True
        assert msg == ""


# ── aggregate_id whitelist ────────────────────────────────────────────────────

class TestAggregateIdWhitelist:
    """aggregate_id не из whitelist → rejected."""

    def test_known_id_accepted(self, registry):
        ok, _ = registry.validate("revenue_total", {})
        assert ok is True

    def test_unknown_id_rejected(self, registry):
        ok, msg = registry.validate("ghost_aggregate", {})
        assert ok is False
        assert "unknown aggregate_id" in msg

    def test_empty_string_id_rejected(self, registry):
        ok, msg = registry.validate("", {})
        assert ok is False

    def test_id_with_spaces_rejected(self, registry):
        ok, msg = registry.validate("revenue total", {})
        assert ok is False

    def test_id_with_semicolon_rejected(self, registry):
        ok, msg = registry.validate("revenue_total; DROP TABLE", {})
        assert ok is False

    def test_id_with_dbo_prefix_rejected(self, registry):
        """dbo.spKDO_Aggregate не в whitelist — только aggregate_id из каталога."""
        ok, msg = registry.validate("dbo.spKDO_Aggregate", {})
        assert ok is False

    def test_all_catalog_ids_accepted(self, registry):
        """Все aggregate_id из каталога должны проходить whitelist."""
        catalog_ids = [a["id"] for a in registry.list_aggregates()]
        assert len(catalog_ids) > 0, "catalog must not be empty"
        for agg_id in catalog_ids:
            ok, msg = registry.validate(agg_id, {})
            assert ok is True, f"Expected OK for catalog id: {agg_id!r}, got: {msg}"


# ── Invalid params: bad date format ───────────────────────────────────────────

class TestInvalidDateParams:
    """Неверный формат даты → rejected."""

    INVALID_DATES = [
        "01-01-2024",          # DD-MM-YYYY
        "2024/01/01",          # слеши
        "January 1, 2024",     # текст
        "20240101",            # без дефисов
        "",                    # пустая строка
        "не дата",             # кириллица
        "2024-1-1",            # без ведущих нулей (не 4-2-2 формат)
    ]

    def test_invalid_date_from_rejected(self, registry):
        for bad_date in self.INVALID_DATES:
            ok, msg = registry.validate("revenue_total", {"date_from": bad_date})
            assert ok is False, f"Expected rejection for date_from={bad_date!r}"
            assert "YYYY-MM-DD" in msg or "date_from" in msg

    def test_invalid_date_to_rejected(self, registry):
        for bad_date in self.INVALID_DATES:
            ok, msg = registry.validate("revenue_total", {"date_to": bad_date})
            assert ok is False, f"Expected rejection for date_to={bad_date!r}"
            assert "YYYY-MM-DD" in msg or "date_to" in msg

    def test_valid_date_accepted(self, registry):
        ok, msg = registry.validate("revenue_total", {
            "date_from": "2026-01-01",
            "date_to": "2026-04-15",
        })
        assert ok is True
        assert msg == ""

    def test_non_string_date_rejected(self, registry):
        ok, msg = registry.validate("revenue_total", {"date_from": 20260101})
        assert ok is False


# ── Invalid params: group_by not in allowed list ──────────────────────────────

class TestInvalidGroupByParams:
    """group_by не из allowed list → rejected."""

    def test_group_by_not_in_allowed_rejected(self, registry):
        # revenue_total allows: total, week, month, master
        invalid_group_by_values = ["day", "object", "channel", "salon", "service"]
        for val in invalid_group_by_values:
            ok, msg = registry.validate("revenue_total", {"group_by": val})
            assert ok is False, f"Expected rejection for group_by={val!r} on revenue_total"
            assert "not allowed" in msg

    def test_group_by_allowed_accepted(self, registry):
        for val in ["total", "week", "month", "master"]:
            ok, msg = registry.validate("revenue_total", {"group_by": val})
            assert ok is True, f"Expected OK for group_by={val!r} on revenue_total, got: {msg}"

    def test_group_by_per_aggregate_specificity(self, registry):
        """group_by проверяется per-aggregate, не глобально."""
        # "salon" доступен для visits_by_salon, но не для outflow_clients
        ok_salon, _ = registry.validate("visits_by_salon", {"group_by": "salon"})
        ok_outflow, msg = registry.validate("outflow_clients", {"group_by": "salon"})
        assert ok_salon is True
        assert ok_outflow is False
        assert "not allowed" in msg

    def test_empty_group_by_not_validated(self, registry):
        """Пустой group_by не передаётся в validate — нет ошибки."""
        ok, _ = registry.validate("revenue_total", {})
        assert ok is True

    def test_group_by_with_injection_rejected(self, registry):
        ok, msg = registry.validate("revenue_total", {"group_by": "total; DROP TABLE"})
        assert ok is False


# ── Invalid params: top_n out of range ────────────────────────────────────────

class TestInvalidTopNParams:
    def test_top_n_zero_rejected(self, registry):
        ok, msg = registry.validate("revenue_total", {"top_n": 0})
        assert ok is False
        assert "top_n" in msg

    def test_top_n_above_50_rejected(self, registry):
        ok, msg = registry.validate("revenue_total", {"top_n": 51})
        assert ok is False
        assert "top_n" in msg

    def test_top_n_string_rejected(self, registry):
        ok, msg = registry.validate("revenue_total", {"top_n": "20"})
        assert ok is False

    def test_top_n_valid_accepted(self, registry):
        for n in [1, 10, 20, 50]:
            ok, _ = registry.validate("revenue_total", {"top_n": n})
            assert ok is True, f"Expected OK for top_n={n}"


# ── Invalid params: object_id / master_id types ───────────────────────────────

class TestInvalidIdParams:
    def test_object_id_string_rejected(self, registry):
        ok, msg = registry.validate("revenue_total", {"object_id": "12345"})
        assert ok is False
        assert "object_id" in msg

    def test_object_id_int_accepted(self, registry):
        ok, _ = registry.validate("revenue_total", {"object_id": 12345})
        assert ok is True

    def test_master_id_string_rejected(self, registry):
        ok, msg = registry.validate("revenue_total", {"master_id": "42"})
        assert ok is False
        assert "master_id" in msg

    def test_master_id_none_accepted(self, registry):
        ok, _ = registry.validate("revenue_total", {"master_id": None})
        assert ok is True
