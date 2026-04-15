import asyncio

import httpx
import pytest

from swarm_powerbi_bot.config import Settings
from swarm_powerbi_bot.services.stt_client import STTClient


def _make_settings(**overrides) -> Settings:
    defaults = {
        "ollama_api_key": "test-key",
        "whisper_base_url": "https://ollama.com/api",
        "whisper_model": "whisper-large:cloud",
    }
    defaults.update(overrides)
    return Settings(**defaults)


def test_available_with_key_and_url():
    client = STTClient(_make_settings())
    assert client.available is True


def test_not_available_without_key():
    client = STTClient(_make_settings(ollama_api_key=""))
    assert client.available is False


def test_not_available_without_url():
    client = STTClient(_make_settings(whisper_base_url=""))
    assert client.available is False


def test_transcribe_returns_empty_when_unavailable():
    client = STTClient(_make_settings(ollama_api_key=""))
    result = asyncio.run(client.transcribe(b"fake-audio"))
    assert result == ""


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
async def test_transcribe_sends_correct_request(monkeypatch):
    transport = MockTransport(
        response_body={"text": "Покажи выручку за неделю"}
    )

    settings = _make_settings()
    client = STTClient(settings)

    original_init = httpx.AsyncClient.__init__

    def patched_init(self_client, **kwargs):
        kwargs["transport"] = transport
        kwargs.pop("timeout", None)
        original_init(self_client, timeout=120.0, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)

    result = await client.transcribe(b"fake-ogg-audio", filename="voice.ogg")

    assert result == "Покажи выручку за неделю"
    assert transport.last_request is not None
    assert "/v1/audio/transcriptions" in str(transport.last_request.url)


@pytest.mark.asyncio
async def test_transcribe_returns_empty_on_error(monkeypatch):
    transport = MockTransport(response_body={}, status_code=500)

    settings = _make_settings()
    client = STTClient(settings)

    original_init = httpx.AsyncClient.__init__

    def patched_init(self_client, **kwargs):
        kwargs["transport"] = transport
        kwargs.pop("timeout", None)
        original_init(self_client, timeout=120.0, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)

    result = await client.transcribe(b"audio", filename="voice.ogg")
    assert result == ""
