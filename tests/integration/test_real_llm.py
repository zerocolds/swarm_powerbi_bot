"""Интеграционные тесты LLM через реальный Ollama.

Запуск: uv run pytest tests/integration/test_real_llm.py -m integration -v
"""
from __future__ import annotations

import json
import urllib.request

import pytest

from swarm_powerbi_bot.agents import AnalystAgent, PlannerAgent
from swarm_powerbi_bot.models import AggregateResult, MultiPlan, UserQuestion
from swarm_powerbi_bot.services import LLMClient
from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry

pytestmark = pytest.mark.integration


# ── 1. Ollama health ─────────────────────────────────────────────────────────

def test_ollama_health(real_settings, ollama_ok):
    if not ollama_ok:
        pytest.skip("Ollama not available")
    url = real_settings.ollama_base_url.rstrip("/") + "/api/tags"
    resp = urllib.request.urlopen(url, timeout=10)  # noqa: S310
    data = json.loads(resp.read())
    assert "models" in data


# ── 2. Простое completion ────────────────────────────────────────────────────

def test_simple_completion(real_settings, ollama_ok):
    if not ollama_ok:
        pytest.skip("Ollama not available")
    url = real_settings.ollama_base_url.rstrip("/") + "/api/chat"
    payload = json.dumps({
        "model": real_settings.ollama_model,
        "messages": [{"role": "user", "content": "Скажи привет"}],
        "stream": False,
        "think": False,
        "options": {"num_predict": 64},
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=15)  # noqa: S310
    body = json.loads(resp.read())
    content = body.get("message", {}).get("content", "")
    assert content.strip(), "Empty LLM response"


# ── 3. Planner keyword fallback ──────────────────────────────────────────────

async def test_planner_keyword_fallback(real_settings):
    """PlannerAgent без registry → keyword fallback должен вернуть Plan."""
    llm_client = LLMClient(real_settings)
    # Без registry — keyword mode
    planner = PlannerAgent(llm_client=llm_client, aggregate_registry=None)
    question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
    plan = await planner.run(question)
    assert plan.topic


# ── 4. Planner LLM mode ─────────────────────────────────────────────────────

async def test_planner_llm_mode(
    real_settings, real_registry: AggregateRegistry, ollama_ok,
):
    if not ollama_ok:
        pytest.skip("Ollama not available")
    llm_client = LLMClient(real_settings)
    planner = PlannerAgent(
        llm_client=llm_client,
        aggregate_registry=real_registry,
        semantic_catalog_path=real_settings.semantic_catalog_path,
    )
    question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
    plan = await planner.run_multi(question)
    assert plan.queries, "Expected at least 1 query"
    assert plan.intent


# ── 5. Planner comparison ────────────────────────────────────────────────────

async def test_planner_comparison(
    real_settings, real_registry: AggregateRegistry, ollama_ok,
):
    if not ollama_ok:
        pytest.skip("Ollama not available")
    llm_client = LLMClient(real_settings)
    planner = PlannerAgent(
        llm_client=llm_client,
        aggregate_registry=real_registry,
        semantic_catalog_path=real_settings.semantic_catalog_path,
    )
    question = UserQuestion(
        user_id="test", text="сравни выручку за март и апрель", object_id=506770,
    )
    plan = await planner.run_multi(question)
    assert plan.intent == "comparison", f"expected comparison, got {plan.intent}"
    assert len(plan.queries) >= 2, f"expected >=2 queries, got {len(plan.queries)}"


# ── 6. Planner decomposition ────────────────────────────────────────────────

async def test_planner_decomposition(
    real_settings, real_registry: AggregateRegistry, ollama_ok,
):
    if not ollama_ok:
        pytest.skip("Ollama not available")
    llm_client = LLMClient(real_settings)
    planner = PlannerAgent(
        llm_client=llm_client,
        aggregate_registry=real_registry,
        semantic_catalog_path=real_settings.semantic_catalog_path,
    )
    question = UserQuestion(
        user_id="test", text="почему упала выручка?", object_id=506770,
    )
    plan = await planner.run_multi(question)
    assert plan.intent in ("decomposition", "single"), f"got {plan.intent}"
    assert len(plan.queries) >= 1


# ── 7. Unknown topic graceful ────────────────────────────────────────────────

async def test_planner_unknown_topic(
    real_settings, real_registry: AggregateRegistry, ollama_ok,
):
    if not ollama_ok:
        pytest.skip("Ollama not available")
    llm_client = LLMClient(real_settings)
    planner = PlannerAgent(
        llm_client=llm_client,
        aggregate_registry=real_registry,
        semantic_catalog_path=real_settings.semantic_catalog_path,
    )
    question = UserQuestion(user_id="test", text="рецепт борща", object_id=506770)
    plan = await planner.run_multi(question)
    # Не должен падать — либо пустой план, либо fallback
    assert isinstance(plan, MultiPlan)


# ── 8. Analyst summary ──────────────────────────────────────────────────────

async def test_analyst_summary(real_settings, ollama_ok):
    if not ollama_ok:
        pytest.skip("Ollama not available")
    llm_client = LLMClient(real_settings)
    analyst = AnalystAgent(llm_client)
    mock_results = [
        AggregateResult(
            aggregate_id="revenue_total",
            label="Выручка",
            rows=[{"Revenue": 1500000, "Visits": 320, "AvgCheck": 4687}],
            row_count=1,
            duration_ms=100,
            status="ok",
        ),
    ]
    question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
    result = await analyst.run(question=question, sql_results=mock_results)
    assert result.answer
    assert len(result.answer) <= 2000


# ── 9. Circuit breaker ──────────────────────────────────────────────────────

async def test_circuit_breaker(real_settings):
    """После N timeout-ов breaker открывается."""
    from swarm_powerbi_bot.config import Settings

    fast_settings = Settings(
        ollama_base_url=real_settings.ollama_base_url,
        ollama_model=real_settings.ollama_model,
        llm_plan_timeout=0,  # мгновенный timeout
        llm_circuit_breaker_threshold=2,
        llm_circuit_breaker_cooldown=60,
        aggregate_catalog_path=real_settings.aggregate_catalog_path,
    )
    llm_client = LLMClient(fast_settings)
    registry = AggregateRegistry(real_settings.aggregate_catalog_path)
    planner = PlannerAgent(
        llm_client=llm_client, aggregate_registry=registry,
        semantic_catalog_path=real_settings.semantic_catalog_path,
    )
    question = UserQuestion(user_id="test", text="выручка", object_id=506770)

    # Несколько попыток для активации breaker
    for _ in range(3):
        plan = await planner.run_multi(question)

    # После breaker — должен сработать fallback (keyword)
    plan = await planner.run_multi(question)
    assert isinstance(plan, MultiPlan)


# ── 10. LLM timeout не зависает ─────────────────────────────────────────────

async def test_llm_timeout(real_settings, ollama_ok):
    if not ollama_ok:
        pytest.skip("Ollama not available")
    from swarm_powerbi_bot.config import Settings

    # Крайне малый timeout
    fast_settings = Settings(
        ollama_base_url=real_settings.ollama_base_url,
        ollama_model=real_settings.ollama_model,
        llm_plan_timeout=0,
        aggregate_catalog_path=real_settings.aggregate_catalog_path,
    )
    llm_client = LLMClient(fast_settings)
    registry = AggregateRegistry(real_settings.aggregate_catalog_path)
    planner = PlannerAgent(
        llm_client=llm_client, aggregate_registry=registry,
        semantic_catalog_path=real_settings.semantic_catalog_path,
    )
    question = UserQuestion(user_id="test", text="выручка за март", object_id=506770)
    # Не должен зависнуть — должен вернуть fallback или timeout
    plan = await planner.run_multi(question)
    assert isinstance(plan, MultiPlan)


# ── 11. Parametrized 10 questions → valid MultiPlan ─────────────────────────

_PLANNER_10_QUESTIONS = [
    "Покажи отток клиентов за месяц",
    "Статистика за эту неделю",
    "Динамика выручки по неделям за квартал",
    "Загрузка мастеров за март",
    "Каналы привлечения клиентов",
    "Именинники на этой неделе",
    "Результаты обзвонов за март",
    "Прогноз визитов на следующую неделю",
    "Популярные услуги за месяц",
    "Контроль качества за март",
]


@pytest.mark.parametrize("question_text", _PLANNER_10_QUESTIONS)
async def test_planner_10_questions(
    real_settings, real_registry: AggregateRegistry, ollama_ok, question_text,
):
    if not ollama_ok:
        pytest.skip("Ollama not available")
    llm_client = LLMClient(real_settings)
    planner = PlannerAgent(
        llm_client=llm_client,
        aggregate_registry=real_registry,
        semantic_catalog_path=real_settings.semantic_catalog_path,
    )
    question = UserQuestion(user_id="test", text=question_text, object_id=506770)
    plan = await planner.run_multi(question)
    assert isinstance(plan, MultiPlan)
    assert plan.queries, f"No queries for: {question_text}"
    assert plan.topic, f"No topic for: {question_text}"
    assert plan.intent in ("single", "comparison", "decomposition"), \
        f"Invalid intent '{plan.intent}' for: {question_text}"
