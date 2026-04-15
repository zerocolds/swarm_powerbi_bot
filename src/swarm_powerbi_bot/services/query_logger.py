from __future__ import annotations

import json
import logging
import logging.handlers
import sys
from datetime import datetime, timezone
from pathlib import Path


_SENSITIVE_KEYS = frozenset(
    {"password", "token", "secret", "connection_string", "conn_str", "dsn", "pwd"}
)


def _sanitize(params: dict) -> dict:
    return {k: "***" if k.lower() in _SENSITIVE_KEYS else v for k, v in params.items()}


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return record.getMessage()


class QueryLogger:
    def __init__(self, log_path: str = "logs/aggregate_queries.log") -> None:
        self._logger = logging.getLogger(f"query_logger.{log_path}")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        if not self._logger.handlers:
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            formatter = _JsonFormatter()

            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)

            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setFormatter(formatter)

            self._logger.addHandler(file_handler)
            self._logger.addHandler(stdout_handler)

    def log(
        self,
        user_id: str,
        aggregate_id: str,
        params: dict,
        duration_ms: int,
        row_count: int,
        status: str,
        error: str | None = None,
    ) -> None:
        entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "aggregate_id": aggregate_id,
            "params": _sanitize(params),
            "duration_ms": duration_ms,
            "row_count": row_count,
            "status": status,
        }
        if error is not None:
            entry["error"] = error
        self._logger.info(json.dumps(entry, ensure_ascii=False))
