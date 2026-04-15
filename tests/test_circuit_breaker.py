"""C5: Тесты circuit breaker в LLMClient.plan_aggregates."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from swarm_powerbi_bot.config import Settings
from swarm_powerbi_bot.services.llm_client import LLMClient


@pytest.fixture()
def settings():
    return Settings(
        ollama_api_key="test-key",
        ollama_base_url="http://localhost:11434/api",
        ollama_model="test-model",
        llm_plan_timeout=1,
        llm_circuit_breaker_threshold=3,
        llm_circuit_breaker_cooldown=60,
    )


@pytest.fixture()
def client(settings):
    return LLMClient(settings)


def _mock_response(content: str) -> MagicMock:
    """Создаёт mock httpx.Response с указанным content."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"message": {"content": content}}
    resp.raise_for_status = MagicMock()
    return resp


class TestCircuitBreaker:
    async def test_breaker_trips_after_threshold_failures(self, client, settings):
        """3 consecutive failures → circuit breaker opens."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = TimeoutError("timeout")

            for _ in range(settings.llm_circuit_breaker_threshold):
                result = await client.plan_aggregates("вопрос", "каталог", "семантика")
                assert result is None

            assert client._cb_failures >= settings.llm_circuit_breaker_threshold
            assert client._cb_open_until > time.monotonic()

    async def test_breaker_returns_none_while_open(self, client, settings):
        """While breaker is open, plan_aggregates returns None without HTTP call."""
        client._cb_failures = settings.llm_circuit_breaker_threshold
        client._cb_open_until = time.monotonic() + 60

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            result = await client.plan_aggregates("вопрос", "каталог", "семантика")
            assert result is None
            mock_post.assert_not_called()

    async def test_breaker_resets_on_success(self, client):
        """Successful plan_aggregates resets failure counter."""
        client._cb_failures = 2
        resp = _mock_response('{"intent": "single", "queries": ["test"]}')

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=resp):
            result = await client.plan_aggregates("вопрос", "каталог", "семантика")
            assert result is not None
            assert client._cb_failures == 0

    async def test_breaker_expires_after_cooldown(self, client, settings):
        """After cooldown, breaker allows new requests."""
        client._cb_failures = settings.llm_circuit_breaker_threshold
        client._cb_open_until = time.monotonic() - 1

        resp = _mock_response('{"intent": "single", "queries": ["x"]}')

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=resp):
            result = await client.plan_aggregates("вопрос", "каталог", "семантика")
            assert result is not None
            assert client._cb_failures == 0

    async def test_empty_content_increments_failures(self, client):
        """Empty LLM response increments failure counter."""
        resp = _mock_response("")

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=resp):
            result = await client.plan_aggregates("вопрос", "каталог", "семантика")
            assert result is None
            assert client._cb_failures == 1
