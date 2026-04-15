import asyncio
import json

import httpx
import pytest

from swarm_powerbi_bot.config import Settings
from swarm_powerbi_bot.services.llm_client import LLMClient


def _make_settings(**overrides) -> Settings:
    defaults = {
        "ollama_api_key": "test-key",
        "ollama_model": "glm-5:cloud",
        "ollama_base_url": "https://ollama.com/api",
    }
    defaults.update(overrides)
    return Settings(**defaults)


def test_returns_fallback_when_no_api_key():
    settings = _make_settings(ollama_api_key="")
    client = LLMClient(settings)
    result = asyncio.run(client.synthesize("sys", "user", "fallback"))
    assert result == "fallback"


def test_extract_content_valid():
    data = {"message": {"role": "assistant", "content": "Ответ аналитика"}}
    assert LLMClient._extract_content(data) == "Ответ аналитика"


def test_extract_content_missing():
    assert LLMClient._extract_content({}) == ""
    assert LLMClient._extract_content({"message": {}}) == ""
    assert LLMClient._extract_content({"message": {"content": ""}}) == ""


class MockTransport(httpx.AsyncBaseTransport):
    def __init__(self, response_body: dict, status_code: int = 200):
        self.response_body = response_body
        self.status_code = status_code
        self.last_request = None

    async def handle_async_request(self, request):
        self.last_request = request
        return httpx.Response(
            status_code=self.status_code,
            json=self.response_body,
        )


@pytest.mark.asyncio
async def test_synthesize_sends_correct_payload(monkeypatch):
    transport = MockTransport(
        response_body={
            "model": "glm-5:cloud",
            "message": {"role": "assistant", "content": "Выручка выросла на 15%"},
            "done": True,
        }
    )

    settings = _make_settings()
    client = LLMClient(settings)

    # Подменяем httpx.AsyncClient на клиент с нашим транспортом
    original_init = httpx.AsyncClient.__init__

    def patched_init(self_client, **kwargs):
        kwargs["transport"] = transport
        kwargs.pop("timeout", None)
        original_init(self_client, timeout=60.0, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)

    result = await client.synthesize("system prompt", "user prompt", "fallback")

    assert result == "Выручка выросла на 15%"

    # Проверяем формат запроса
    body = json.loads(transport.last_request.content)
    assert body["model"] == "glm-5:cloud"
    assert body["stream"] is False
    assert body["messages"][0]["role"] == "system"
    assert body["messages"][0]["content"] == "system prompt"
    assert body["messages"][1]["role"] == "user"
    assert body["messages"][1]["content"] == "user prompt"
    assert body["options"]["temperature"] == 0.3


@pytest.mark.asyncio
async def test_synthesize_returns_fallback_on_error(monkeypatch):
    transport = MockTransport(response_body={}, status_code=500)

    settings = _make_settings()
    client = LLMClient(settings)

    original_init = httpx.AsyncClient.__init__

    def patched_init(self_client, **kwargs):
        kwargs["transport"] = transport
        kwargs.pop("timeout", None)
        original_init(self_client, timeout=60.0, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)

    result = await client.synthesize("sys", "user", "fallback text")
    assert result == "fallback text"
