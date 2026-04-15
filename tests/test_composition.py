"""T037: Phase 9 — Composition (US-011).

Тест-кейсы:
- Декомпозиция: планировщик создаёт 4-5 агрегатов (выручка + клиенты + средний чек × 2 периода)
- Факторный анализ: аналитик определяет главный фактор из результатов
- Лимит: максимум 10 запросов, при decomposition — максимум 5
- Пустые результаты → graceful handling (нет исключений, понятный текст)
"""
from __future__ import annotations

import asyncio
import textwrap
from unittest.mock import AsyncMock

import pytest

from swarm_powerbi_bot.agents.analyst import AnalystAgent
from swarm_powerbi_bot.agents.planner import PlannerAgent
from swarm_powerbi_bot.models import AggregateQuery, AggregateResult, MultiPlan, UserQuestion
from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry
from swarm_powerbi_bot.services.llm_client import LLMClient


# ── Fixtures ──────────────────────────────────────────────────────────────────

CATALOG_YAML = textwrap.dedent("""\
    aggregates:
      - id: revenue_summary
        name: Сводка по выручке
        description: Суммарная выручка, количество клиентов и средний чек за период
        procedure: spKDO_Aggregate
        allowed_group_by:
          - total
          - week
          - month
      - id: client_count
        name: Количество клиентов
        description: Уникальные клиенты за период
        procedure: spKDO_Aggregate
        allowed_group_by:
          - total
          - week
          - month
      - id: avg_check
        name: Средний чек
        description: Средний чек за период
        procedure: spKDO_Aggregate
        allowed_group_by:
          - total
          - month
      - id: outflow_clients
        name: Отток клиентов
        description: Клиенты со статусом outflow
        procedure: spKDO_ClientList
        allowed_group_by:
          - list
          - master
""")


@pytest.fixture()
def catalog_path(tmp_path):
    p = tmp_path / "aggregate-catalog.yaml"
    p.write_text(CATALOG_YAML, encoding="utf-8")
    return str(p)


@pytest.fixture()
def registry(catalog_path):
    return AggregateRegistry(catalog_path)


def _make_planner(llm_dict: dict | None, registry: AggregateRegistry) -> PlannerAgent:
    """Создаёт PlannerAgent с моком plan_aggregates, возвращающим llm_dict."""
    from swarm_powerbi_bot.config import Settings
    llm = LLMClient(Settings())
    llm.plan_aggregates = AsyncMock(return_value=llm_dict)
    return PlannerAgent(llm_client=llm, aggregate_registry=registry)


def _make_analyst() -> AnalystAgent:
    """Создаёт AnalystAgent с моком synthesize (не вызывается при decomposition)."""
    from swarm_powerbi_bot.config import Settings
    llm = LLMClient(Settings())
    llm.synthesize = AsyncMock(return_value="мок ответ")
    return AnalystAgent(llm_client=llm)


def _make_decomposition_plan(queries: list[AggregateQuery]) -> MultiPlan:
    return MultiPlan(
        objective="почему упала выручка?",
        intent="decomposition",
        queries=queries,
        topic="statistics",
        render_needed=False,
        notes=["planner_v2:llm"],
    )


# ── T037-1: Декомпозиция → 4-5 агрегатов ────────────────────────────────────

class TestDecompositionPlanning:
    """Планировщик создаёт 4-5 агрегатов при intent=decomposition."""

    def test_decomposition_creates_four_aggregates(self, registry):
        """Базовый сценарий: LLM возвращает 4 запроса при decomposition."""
        llm_response = {
            "intent": "decomposition",
            "queries": [
                {"aggregate_id": "revenue_summary", "params": {"period_hint": "текущий месяц"}, "label": "Выручка (апрель)"},
                {"aggregate_id": "revenue_summary", "params": {"period_hint": "прошлый месяц"}, "label": "Выручка (март)"},
                {"aggregate_id": "client_count", "params": {"period_hint": "текущий месяц"}, "label": "Клиенты (апрель)"},
                {"aggregate_id": "client_count", "params": {"period_hint": "прошлый месяц"}, "label": "Клиенты (март)"},
            ],
            "topic": "statistics",
            "render_needed": False,
        }
        planner = _make_planner(llm_response, registry)
        q = UserQuestion(user_id="1", text="почему упала выручка в апреле?")
        plan = asyncio.run(planner.run_multi(q))

        assert isinstance(plan, MultiPlan)
        assert plan.intent == "decomposition"
        assert len(plan.queries) == 4
        assert "planner_v2:llm" in plan.notes

    def test_decomposition_creates_five_aggregates(self, registry):
        """Расширенный сценарий: выручка×2 + клиенты×2 + средний чек = 5 запросов."""
        llm_response = {
            "intent": "decomposition",
            "queries": [
                {"aggregate_id": "revenue_summary", "params": {}, "label": "Выручка (апрель)"},
                {"aggregate_id": "revenue_summary", "params": {}, "label": "Выручка (март)"},
                {"aggregate_id": "client_count", "params": {}, "label": "Клиенты (апрель)"},
                {"aggregate_id": "client_count", "params": {}, "label": "Клиенты (март)"},
                {"aggregate_id": "avg_check", "params": {}, "label": "Средний чек"},
            ],
            "topic": "statistics",
            "render_needed": False,
        }
        planner = _make_planner(llm_response, registry)
        q = UserQuestion(user_id="1", text="почему упала выручка?")
        plan = asyncio.run(planner.run_multi(q))

        assert plan.intent == "decomposition"
        assert len(plan.queries) == 5
        agg_ids = [aq.aggregate_id for aq in plan.queries]
        assert "revenue_summary" in agg_ids
        assert "client_count" in agg_ids
        assert "avg_check" in agg_ids

    def test_decomposition_labels_preserved(self, registry):
        """Labels корректно сохраняются в AggregateQuery."""
        llm_response = {
            "intent": "decomposition",
            "queries": [
                {"aggregate_id": "revenue_summary", "params": {}, "label": "Выручка (апрель)"},
                {"aggregate_id": "revenue_summary", "params": {}, "label": "Выручка (март)"},
            ],
            "topic": "statistics",
            "render_needed": False,
        }
        planner = _make_planner(llm_response, registry)
        q = UserQuestion(user_id="1", text="сравни выручку апрель vs март")
        plan = asyncio.run(planner.run_multi(q))

        labels = [aq.label for aq in plan.queries]
        assert "Выручка (апрель)" in labels
        assert "Выручка (март)" in labels


# ── T037-2: Лимит запросов ────────────────────────────────────────────────────

class TestQueryLimits:
    """Лимит: максимум 10 запросов в общем случае, 5 при decomposition."""

    def test_decomposition_capped_at_five(self, registry):
        """LLM возвращает 8 запросов при decomposition → обрезается до 5."""
        llm_response = {
            "intent": "decomposition",
            "queries": [
                {"aggregate_id": "revenue_summary", "params": {}, "label": f"q{i}"}
                for i in range(8)
            ],
            "topic": "statistics",
            "render_needed": False,
        }
        planner = _make_planner(llm_response, registry)
        q = UserQuestion(user_id="1", text="почему упала выручка?")
        plan = asyncio.run(planner.run_multi(q))

        assert len(plan.queries) <= 5

    def test_non_decomposition_allows_up_to_ten(self, registry):
        """Для intent=comparison/ranking LLM может вернуть до 10 запросов."""
        llm_response = {
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_summary", "params": {}, "label": f"q{i}"}
                for i in range(10)
            ],
            "topic": "statistics",
            "render_needed": False,
        }
        planner = _make_planner(llm_response, registry)
        q = UserQuestion(user_id="1", text="сравни все периоды")
        plan = asyncio.run(planner.run_multi(q))

        assert len(plan.queries) == 10

    def test_non_decomposition_capped_at_ten(self, registry):
        """LLM возвращает 15 запросов → обрезается до 10 (не decomposition)."""
        llm_response = {
            "intent": "ranking",
            "queries": [
                {"aggregate_id": "revenue_summary", "params": {}, "label": f"q{i}"}
                for i in range(15)
            ],
            "topic": "statistics",
            "render_needed": False,
        }
        planner = _make_planner(llm_response, registry)
        q = UserQuestion(user_id="1", text="рейтинг всех периодов")
        plan = asyncio.run(planner.run_multi(q))

        assert len(plan.queries) <= 10


# ── T037-3: Факторный анализ (AnalystAgent) ───────────────────────────────────

class TestFactorAnalysis:
    """AnalystAgent определяет главный фактор при intent=decomposition."""

    def _make_result(
        self,
        aggregate_id: str,
        label: str,
        revenue: float,
    ) -> AggregateResult:
        return AggregateResult(
            aggregate_id=aggregate_id,
            label=label,
            rows=[{"Revenue": revenue}],
            row_count=1,
            status="ok",
        )

    def test_identifies_main_factor_from_results(self):
        """Аналитик выявляет фактор с наибольшим относительным изменением."""
        analyst = _make_analyst()

        # revenue: 80 vs 100 → −20%
        # clients: 45 vs 50 → −10%
        results = [
            self._make_result("revenue_summary", "Выручка (апрель)", 80),
            self._make_result("revenue_summary", "Выручка (март)", 100),
            self._make_result("client_count", "Клиенты (апрель)", 45),
            self._make_result("client_count", "Клиенты (март)", 50),
        ]
        plan = _make_decomposition_plan([
            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
        ])

        result = asyncio.run(analyst.run_multi("почему упала выручка?", results, plan))

        assert result.answer  # Есть ответ
        # Главный фактор — выручка (−20%), он упал
        assert "упал" in result.answer or "20.0" in result.answer

    def test_answer_contains_main_cause(self):
        """Ответ содержит «Основная причина:» с фактором."""
        analyst = _make_analyst()

        # revenue: 90 vs 100 → −10% (меньше изменение)
        # clients: 40 vs 100 → −60% (больше изменение — это главная причина)
        results = [
            self._make_result("revenue_summary", "Выручка", 90),
            self._make_result("revenue_summary", "Выручка (прошлый)", 100),
            self._make_result("client_count", "Клиенты", 40),
            self._make_result("client_count", "Клиенты (прошлый)", 100),
        ]
        plan = _make_decomposition_plan([
            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
        ])

        result = asyncio.run(analyst.run_multi("почему упала выручка?", results, plan))

        # Клиенты упали сильнее (−60% vs −10%), должны быть основной причиной
        assert "Основная причина" in result.answer
        assert "Клиенты" in result.answer

    def test_max_three_factors_in_response(self):
        """В ответе не более 3 факторов."""
        analyst = _make_analyst()

        # 3 пары: revenue, clients, avg_check — каждая с изменением
        results = [
            self._make_result("revenue_summary", "Выручка", 80),
            self._make_result("revenue_summary", "Выручка (прошлый)", 100),
            self._make_result("client_count", "Клиенты", 70),
            self._make_result("client_count", "Клиенты (прошлый)", 100),
            self._make_result("avg_check", "Средний чек", 90),
            self._make_result("avg_check", "Средний чек (прошлый)", 100),
        ]
        plan = _make_decomposition_plan([
            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
        ])

        result = asyncio.run(analyst.run_multi("почему упала выручка?", results, plan))

        # Ответ содержит максимум 3 строки с процентами (main + 2 secondary)
        pct_lines = [line for line in result.answer.split("\n") if "%" in line]
        assert len(pct_lines) <= 3

    def test_response_confidence_high_with_multiple_results(self):
        """Уверенность high при наличии нескольких результатов."""
        analyst = _make_analyst()
        results = [
            self._make_result("revenue_summary", "Выручка", 80),
            self._make_result("revenue_summary", "Выручка (прошлый)", 100),
        ]
        plan = _make_decomposition_plan([
            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
        ])

        result = asyncio.run(analyst.run_multi("почему упала выручка?", results, plan))

        assert result.confidence == "high"


# ── T037-4: Пустые результаты → graceful handling ────────────────────────────

class TestEmptyResultsGracefulHandling:
    """Пустые результаты → нет исключений, понятный текст в ответе."""

    def test_empty_results_no_exception(self):
        """Пустой список results → нет исключений."""
        analyst = _make_analyst()
        plan = _make_decomposition_plan([])

        result = asyncio.run(analyst.run_multi("почему упала выручка?", [], plan))

        assert result is not None
        assert isinstance(result.answer, str)
        assert len(result.answer) > 0

    def test_empty_results_low_confidence(self):
        """При пустых результатах уверенность low."""
        analyst = _make_analyst()
        plan = _make_decomposition_plan([])

        result = asyncio.run(analyst.run_multi("почему упала выручка?", [], plan))

        assert result.confidence == "low"

    def test_empty_results_informative_message(self):
        """При пустых результатах сообщение информирует об отсутствии данных."""
        analyst = _make_analyst()
        plan = _make_decomposition_plan([])

        result = asyncio.run(analyst.run_multi("почему упала выручка?", [], plan))

        assert "не найдено" in result.answer or "данных" in result.answer.lower()

    def test_all_error_results_no_exception(self):
        """Все результаты со статусом error → нет исключений."""
        analyst = _make_analyst()

        results = [
            AggregateResult(
                aggregate_id="revenue_summary",
                label="Выручка",
                rows=[],
                row_count=0,
                status="error",
                error="SQL timeout",
            ),
            AggregateResult(
                aggregate_id="client_count",
                label="Клиенты",
                rows=[],
                row_count=0,
                status="error",
                error="Connection failed",
            ),
        ]
        plan = _make_decomposition_plan([
            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
        ])

        result = asyncio.run(analyst.run_multi("почему упала выручка?", results, plan))

        assert result is not None
        assert isinstance(result.answer, str)

    def test_partial_error_results(self):
        """Часть результатов с ошибкой → обрабатываем ok-результаты."""
        analyst = _make_analyst()

        results = [
            AggregateResult(
                aggregate_id="revenue_summary",
                label="Выручка",
                rows=[{"Revenue": 100}],
                row_count=1,
                status="ok",
            ),
            AggregateResult(
                aggregate_id="client_count",
                label="Клиенты",
                rows=[],
                row_count=0,
                status="error",
                error="timeout",
            ),
        ]
        plan = _make_decomposition_plan([
            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
        ])

        result = asyncio.run(analyst.run_multi("почему упала выручка?", results, plan))

        assert result is not None
        assert result.confidence != "high"  # Не все ok

    def test_results_without_numeric_data(self):
        """Результаты без числовых данных → graceful fallback."""
        analyst = _make_analyst()

        results = [
            AggregateResult(
                aggregate_id="revenue_summary",
                label="Выручка (апрель)",
                rows=[{"Name": "Salon A"}],  # Только строковые поля
                row_count=1,
                status="ok",
            ),
            AggregateResult(
                aggregate_id="revenue_summary",
                label="Выручка (март)",
                rows=[{"Name": "Salon A"}],
                row_count=1,
                status="ok",
            ),
        ]
        plan = _make_decomposition_plan([
            AggregateQuery(aggregate_id=r.aggregate_id, label=r.label) for r in results
        ])

        # Не должно выбросить исключение
        result = asyncio.run(analyst.run_multi("почему упала выручка?", results, plan))

        assert result is not None
        assert isinstance(result.answer, str)
