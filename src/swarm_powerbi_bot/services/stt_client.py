"""Speech-to-text клиент — Whisper Large через Ollama Cloud."""
from __future__ import annotations

import httpx

from ..config import Settings


class STTClient:
    """Отправляет аудио на Whisper-эндпоинт и возвращает текст."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def available(self) -> bool:
        return bool(self.settings.whisper_base_url and self.settings.ollama_api_key)

    async def transcribe(self, audio_bytes: bytes, filename: str = "voice.ogg") -> str:
        """Транскрибирует аудио → текст. Возвращает пустую строку при ошибке."""
        if not self.available:
            return ""

        base = self.settings.whisper_base_url.rstrip("/")
        url = f"{base}/v1/audio/transcriptions"

        headers = {
            "Authorization": f"Bearer {self.settings.ollama_api_key}",
        }

        # multipart/form-data — стандартный формат Whisper API
        files = {
            "file": (filename, audio_bytes, "audio/ogg"),
        }
        data = {
            "model": self.settings.whisper_model,
            "language": "ru",
            "response_format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, files=files, data=data)
                resp.raise_for_status()
                result = resp.json()
        except Exception:
            return ""

        # Стандартный ответ: {"text": "..."}
        text = result.get("text", "")
        if isinstance(text, str):
            return text.strip()
        return ""
