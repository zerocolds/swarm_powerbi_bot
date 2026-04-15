"""Fixtures для интеграционных тестов с реальным MSSQL и Ollama.

Все тесты помечены @pytest.mark.integration и пропускаются
если окружение недоступно (нет MSSQL_SERVER, нет Ollama).

Запуск: uv run pytest tests/integration/ -m integration -v
"""
from __future__ import annotations

import os
import urllib.request

import pytest

from swarm_powerbi_bot.config import Settings
from swarm_powerbi_bot.main import build_orchestrator
from swarm_powerbi_bot.services import LLMClient, SQLClient
from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry

TEST_OBJECT_ID = 506770
TEST_DATE_FROM = "2026-03-01"
TEST_DATE_TO = "2026-03-31"


def _mssql_available(settings: Settings) -> bool:
    conn_str = settings.sql_connection_string()
    if not conn_str:
        return False
    try:
        import pyodbc

        conn = pyodbc.connect(conn_str, timeout=5)
        conn.close()
        return True
    except Exception:
        return False


def _ollama_available(settings: Settings) -> bool:
    if not settings.ollama_base_url:
        return False
    try:
        url = settings.ollama_base_url.rstrip("/") + "/api/tags"
        req = urllib.request.Request(url)
        urllib.request.urlopen(req, timeout=5)  # noqa: S310
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def real_settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def mssql_ok(real_settings: Settings) -> bool:
    return _mssql_available(real_settings)


@pytest.fixture(scope="session")
def ollama_ok(real_settings: Settings) -> bool:
    return _ollama_available(real_settings)


@pytest.fixture(scope="session")
def real_sql_client(real_settings: Settings, mssql_ok: bool) -> SQLClient:
    if not mssql_ok:
        pytest.skip("MSSQL not available")
    return SQLClient(real_settings)


@pytest.fixture(scope="session")
def real_llm_client(real_settings: Settings, ollama_ok: bool) -> LLMClient:
    if not ollama_ok:
        pytest.skip("Ollama not available")
    return LLMClient(real_settings)


@pytest.fixture(scope="session")
def real_registry(real_settings: Settings) -> AggregateRegistry:
    path = real_settings.aggregate_catalog_path
    if not os.path.exists(path):
        pytest.skip(f"Catalog not found: {path}")
    return AggregateRegistry(path)


@pytest.fixture(scope="session")
def real_orchestrator(real_settings: Settings, mssql_ok: bool, ollama_ok: bool):
    if not mssql_ok:
        pytest.skip("MSSQL not available")
    if not ollama_ok:
        pytest.skip("Ollama not available")
    return build_orchestrator(real_settings)


@pytest.fixture
def test_object_id() -> int:
    return TEST_OBJECT_ID


@pytest.fixture
def test_date_range() -> tuple[str, str]:
    return TEST_DATE_FROM, TEST_DATE_TO
