"""Интеграционные E2E тесты через реальный MSSQL + Ollama.

Запуск: uv run pytest tests/integration/test_real_e2e.py -m integration -v
"""
from __future__ import annotations

import asyncio

import pytest

from swarm_powerbi_bot.models import SwarmResponse, UserQuestion
from swarm_powerbi_bot.orchestrator import SwarmOrchestrator

pytestmark = pytest.mark.integration


def _question(text: str, **kwargs) -> UserQuestion:
    defaults = {"user_id": "e2e-test", "object_id": 506770}
    defaults.update(kwargs)
    return UserQuestion(text=text, **defaults)


# ── 1. Revenue question ─────────────────────────────────────────────────────

async def test_e2e_revenue_question(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(_question("Покажи выручку за март"))
    assert resp.answer, "empty answer"
    assert resp.topic != "unknown", f"topic should not be unknown, got {resp.topic}"


# ── 2. Outflow question ─────────────────────────────────────────────────────

async def test_e2e_outflow_question(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Какой отток за месяц?"),
    )
    assert resp.answer


# ── 3. Comparison с chart ────────────────────────────────────────────────────

async def test_e2e_comparison(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Сравни выручку марта и февраля"),
    )
    assert resp.answer
    # comparison должен генерировать chart
    if resp.image is not None:
        assert resp.mime_type == "image/png"


# ── 4. Top masters ──────────────────────────────────────────────────────────

async def test_e2e_top_masters(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Топ-5 мастеров по выручке за март"),
    )
    assert resp.answer


# ── 5. Decomposition ────────────────────────────────────────────────────────

async def test_e2e_decomposition(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Почему упала выручка?"),
    )
    assert resp.answer


# ── 6. Unknown question ─────────────────────────────────────────────────────

async def test_e2e_unknown_question(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Как сварить борщ?"),
    )
    assert isinstance(resp, SwarmResponse)
    # Должен вежливо отказать или дать общий ответ


# ── 7. Follow-up ────────────────────────────────────────────────────────────

async def test_e2e_follow_up(real_orchestrator: SwarmOrchestrator):
    resp1 = await real_orchestrator.handle_question(
        _question("выручка за март"),
    )
    assert resp1.answer
    topic = resp1.topic

    resp2 = await real_orchestrator.handle_question(
        _question("а за февраль?", last_topic=topic),
    )
    assert resp2.answer


# ── 8. Chart generation ─────────────────────────────────────────────────────

async def test_e2e_chart_generation(real_orchestrator: SwarmOrchestrator):
    resp = await real_orchestrator.handle_question(
        _question("Покажи график выручки по неделям за квартал"),
    )
    assert resp.answer
    # Если chart сгенерирован, проверяем формат
    if resp.image is not None:
        assert resp.mime_type == "image/png"
        assert len(resp.image) > 100  # не пустой PNG


# ── 9. Telegram mock ────────────────────────────────────────────────────────

async def test_e2e_telegram_mock(real_orchestrator: SwarmOrchestrator):
    """Проверяем что orchestrator возвращает корректный SwarmResponse."""
    resp = await real_orchestrator.handle_question(
        _question("статистика за март"),
    )
    assert isinstance(resp, SwarmResponse)
    assert resp.confidence in ("low", "medium", "high")
    assert isinstance(resp.follow_ups, list)
    assert isinstance(resp.diagnostics, dict)


# ── 10. Concurrent users ────────────────────────────────────────────────────

async def test_e2e_concurrent_users(real_orchestrator: SwarmOrchestrator):
    questions = [
        _question("выручка за март", user_id="user-1"),
        _question("отток клиентов", user_id="user-2"),
        _question("коммуникации за март", user_id="user-3"),
    ]
    results = await asyncio.gather(
        *[real_orchestrator.handle_question(q) for q in questions],
    )
    for i, resp in enumerate(results):
        assert isinstance(resp, SwarmResponse), f"user-{i+1} got non-SwarmResponse"
        assert resp.answer, f"user-{i+1} got empty answer"
