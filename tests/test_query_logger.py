"""Tests for swarm_powerbi_bot.services.query_logger."""
from __future__ import annotations

import json

import pytest

from swarm_powerbi_bot.services.query_logger import QueryLogger


# ── helpers ───────────────────────────────────────────────────────────────────

def _last_log_entry(log_path: str) -> dict:
    """Read the last non-empty line from a log file and parse it as JSON."""
    with open(log_path, encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    assert lines, "Log file is empty"
    return json.loads(lines[-1])


# ── tests ─────────────────────────────────────────────────────────────────────

class TestQueryLogger:
    @pytest.fixture()
    def log_file(self, tmp_path):
        return str(tmp_path / "test_queries.log")

    @pytest.fixture()
    def logger(self, log_file):
        ql = QueryLogger(log_path=log_file)
        yield ql
        # Remove file handler to avoid leaking across tests
        for h in ql._logger.handlers[:]:
            h.close()
            ql._logger.removeHandler(h)

    def _log_success(self, logger: QueryLogger, params: dict | None = None) -> None:
        logger.log(
            user_id="u123",
            aggregate_id="revenue_by_master",
            params=params or {"date_from": "2024-01-01"},
            duration_ms=42,
            row_count=10,
            status="ok",
        )

    def test_log_file_is_created(self, logger, log_file):
        self._log_success(logger)
        import os
        assert os.path.exists(log_file)

    def test_log_entry_is_valid_json(self, logger, log_file):
        self._log_success(logger)
        entry = _last_log_entry(log_file)
        assert isinstance(entry, dict)

    def test_required_fields_present(self, logger, log_file):
        self._log_success(logger)
        entry = _last_log_entry(log_file)
        required = {"timestamp", "user_id", "aggregate_id", "params", "duration_ms", "row_count", "status"}
        assert required.issubset(entry.keys())

    def test_timestamp_is_iso_format(self, logger, log_file):
        from datetime import datetime
        self._log_success(logger)
        entry = _last_log_entry(log_file)
        # Should not raise
        dt = datetime.fromisoformat(entry["timestamp"])
        assert dt.tzinfo is not None  # timezone-aware

    def test_user_id_recorded(self, logger, log_file):
        self._log_success(logger)
        entry = _last_log_entry(log_file)
        assert entry["user_id"] == "u123"

    def test_aggregate_id_recorded(self, logger, log_file):
        self._log_success(logger)
        entry = _last_log_entry(log_file)
        assert entry["aggregate_id"] == "revenue_by_master"

    def test_duration_ms_recorded(self, logger, log_file):
        self._log_success(logger)
        entry = _last_log_entry(log_file)
        assert entry["duration_ms"] == 42

    def test_row_count_recorded(self, logger, log_file):
        self._log_success(logger)
        entry = _last_log_entry(log_file)
        assert entry["row_count"] == 10

    def test_status_ok_recorded(self, logger, log_file):
        self._log_success(logger)
        entry = _last_log_entry(log_file)
        assert entry["status"] == "ok"

    def test_password_is_masked(self, logger, log_file):
        self._log_success(logger, params={"date_from": "2024-01-01", "password": "s3cr3t"})
        entry = _last_log_entry(log_file)
        assert entry["params"]["password"] == "***"

    def test_token_is_masked(self, logger, log_file):
        self._log_success(logger, params={"token": "abc123", "date_from": "2024-01-01"})
        entry = _last_log_entry(log_file)
        assert entry["params"]["token"] == "***"

    def test_non_sensitive_params_not_masked(self, logger, log_file):
        self._log_success(logger, params={"date_from": "2024-01-01", "top_n": 5})
        entry = _last_log_entry(log_file)
        assert entry["params"]["date_from"] == "2024-01-01"
        assert entry["params"]["top_n"] == 5

    def test_error_field_included_on_error_status(self, logger, log_file):
        logger.log(
            user_id="u999",
            aggregate_id="revenue_by_master",
            params={},
            duration_ms=1,
            row_count=0,
            status="error",
            error="Connection timeout",
        )
        entry = _last_log_entry(log_file)
        assert entry["status"] == "error"
        assert "error" in entry
        assert entry["error"] == "Connection timeout"

    def test_error_field_absent_on_success(self, logger, log_file):
        self._log_success(logger)
        entry = _last_log_entry(log_file)
        assert "error" not in entry

    def test_multiple_sensitive_keys_all_masked(self, logger, log_file):
        self._log_success(logger, params={
            "password": "pw",
            "token": "tok",
            "secret": "sec",
            "date_from": "2024-01-01",
        })
        entry = _last_log_entry(log_file)
        for key in ("password", "token", "secret"):
            assert entry["params"][key] == "***", f"{key} was not masked"

    def test_conn_str_masked(self, logger, log_file):
        self._log_success(logger, params={"connection_string": "Server=x;Pwd=y"})
        entry = _last_log_entry(log_file)
        assert entry["params"]["connection_string"] == "***"
