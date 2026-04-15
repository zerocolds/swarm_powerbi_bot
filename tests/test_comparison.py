"""T033: Тесты Phase 8 — Comparisons (US-010).

Покрывает:
- Comparison intent → planner создаёт 2 запроса с разными датами для одного агрегата
- "этот месяц vs прошлый" → корректный расчёт дат
- Сравнение мастеров → 2 запроса с разным master_id
- Grouped bar chart рендерится без ошибок
- Неполный текущий месяц → analyst помечает в тексте ответа
"""
from __future__ import annotations

import asyncio
import textwrap
from calendar import monthrange
from datetime import date, timedelta
from unittest.mock import AsyncMock

import pytest

from swarm_powerbi_bot.agents.analyst import AnalystAgent
from swarm_powerbi_bot.agents.planner import PlannerAgent, _resolve_period
from swarm_powerbi_bot.models import (
    AggregateResult,
    ComparisonResult,
    MultiPlan,
    UserQuestion,
)
from swarm_powerbi_bot.services.aggregate_registry import AggregateRegistry
from swarm_powerbi_bot.services.chart_renderer import HAS_MPL, render_comparison
from swarm_powerbi_bot.services.llm_client import LLMClient


# ── Fixtures ──────────────────────────────────────────────────────────────────

CATALOG_YAML = textwrap.dedent("""\
    aggregates:
      - id: revenue_total
        name: Общая выручка
        description: Суммарная выручка за период
        procedure: spKDO_Aggregate
        allowed_group_by:
          - total
          - week
          - month
          - master
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


def _make_planner(llm_json: str | None, registry: AggregateRegistry) -> PlannerAgent:
    """Создаёт PlannerAgent с mock LLM."""
    import json
    import re

    def _parse(text: str | None) -> dict | None:
        if not text:
            return None
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
        if "queries" not in data:
            return None
        return data

    from swarm_powerbi_bot.config import Settings
    llm = LLMClient(Settings())
    llm.plan_aggregates = AsyncMock(return_value=_parse(llm_json))
    return PlannerAgent(llm_client=llm, aggregate_registry=registry)


def _make_analyst() -> AnalystAgent:
    from swarm_powerbi_bot.config import Settings
    llm = LLMClient(Settings())
    return AnalystAgent(llm_client=llm)


# ── T033-1: Comparison intent → 2 запроса с разными датами ───────────────────

class TestComparisonIntentTwoQueries:
    """Comparison intent → planner создаёт 2 запроса с разными датами для одного агрегата."""

    def test_comparison_intent_produces_two_queries(self, registry):
        llm_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total",
                 "params": {"date_from": "2026-04-01", "date_to": "2026-04-15", "group_by": "total"},
                 "label": "Этот месяц"},
                {"aggregate_id": "revenue_total",
                 "params": {"date_from": "2026-03-01", "date_to": "2026-03-31", "group_by": "total"},
                 "label": "Прошлый месяц"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(llm_json, registry)
        q = UserQuestion(user_id="1", text="Сравни выручку этого месяца с прошлым")
        plan = asyncio.run(planner.run_multi(q))

        assert isinstance(plan, MultiPlan)
        assert plan.intent == "comparison"
        assert len(plan.queries) == 2
        # Оба запроса — один агрегат
        assert plan.queries[0].aggregate_id == "revenue_total"
        assert plan.queries[1].aggregate_id == "revenue_total"

    def test_comparison_queries_have_different_date_ranges(self, registry):
        llm_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total",
                 "params": {"date_from": "2026-04-01", "date_to": "2026-04-15"},
                 "label": "Апрель"},
                {"aggregate_id": "revenue_total",
                 "params": {"date_from": "2026-03-01", "date_to": "2026-03-31"},
                 "label": "Март"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(llm_json, registry)
        q = UserQuestion(user_id="1", text="Сравни апрель и март")
        plan = asyncio.run(planner.run_multi(q))

        dates_a = plan.queries[0].params
        dates_b = plan.queries[1].params
        assert dates_a["date_from"] != dates_b["date_from"]
        assert dates_a["date_to"] != dates_b["date_to"]

    def test_comparison_with_single_query_falls_back(self, registry):
        """Если comparison intent но только 1 запрос → fallback на keyword."""
        llm_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total", "params": {}, "label": "Один"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(llm_json, registry)
        q = UserQuestion(user_id="1", text="Сравни выручку")
        plan = asyncio.run(planner.run_multi(q))
        # Должен упасть в fallback
        assert "planner_v2:keyword" in plan.notes


# ── T033-2: "этот месяц vs прошлый" → корректный расчёт дат ─────────────────

class TestPeriodResolution:
    """_resolve_period: корректные вычисления дат для разных подсказок."""

    def test_this_month_starts_on_first(self):
        df, dt = _resolve_period("этот месяц")
        today = date.today()
        assert df == today.replace(day=1).isoformat()
        assert dt == today.isoformat()

    def test_this_month_alias(self):
        df1, dt1 = _resolve_period("этот месяц")
        df2, dt2 = _resolve_period("текущий месяц")
        assert df1 == df2
        assert dt1 == dt2

    def test_prev_month_is_full_month(self):
        df, dt = _resolve_period("прошлый месяц")
        today = date.today()
        first_of_current = today.replace(day=1)
        last_of_prev = first_of_current - timedelta(days=1)
        expected_from = last_of_prev.replace(day=1)
        assert df == expected_from.isoformat()
        assert dt == last_of_prev.isoformat()

    def test_prev_month_last_day_correct(self):
        """Последний день предыдущего месяца должен совпадать с его фактическим последним днём."""
        df, dt = _resolve_period("прошлый месяц")
        today = date.today()
        first_of_current = today.replace(day=1)
        last_of_prev = first_of_current - timedelta(days=1)
        _, last_day = monthrange(last_of_prev.year, last_of_prev.month)
        assert dt.endswith(f"-{last_day:02d}")

    def test_prev_month_alias(self):
        df1, dt1 = _resolve_period("прошлый месяц")
        df2, dt2 = _resolve_period("предыдущий месяц")
        assert df1 == df2
        assert dt1 == dt2

    def test_prev_quarter_returns_full_quarter(self):
        df, dt = _resolve_period("прошлый квартал")
        d_from = date.fromisoformat(df)
        d_to = date.fromisoformat(dt)
        # Разница не менее 88 дней (кварталы 90-92 дня)
        assert (d_to - d_from).days >= 88

    def test_this_week_starts_on_monday(self):
        df, dt = _resolve_period("эта неделя")
        d_from = date.fromisoformat(df)
        assert d_from.weekday() == 0  # понедельник

    def test_prev_week_is_full_week(self):
        df, dt = _resolve_period("прошлая неделя")
        d_from = date.fromisoformat(df)
        d_to = date.fromisoformat(dt)
        assert d_from.weekday() == 0   # понедельник
        assert d_to.weekday() == 6    # воскресенье
        assert (d_to - d_from).days == 6

    def test_unknown_hint_falls_back_to_current_month(self):
        """Неизвестный hint → текущий месяц."""
        df, dt = _resolve_period("непонятный период")
        df_exp, dt_exp = _resolve_period("этот месяц")
        assert df == df_exp
        assert dt == dt_exp

    def test_period_hint_resolved_in_comparison_plan(self, registry):
        """period_hint в params → разрешается в date_from/date_to при comparison."""
        llm_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total",
                 "params": {"period_hint": "этот месяц", "group_by": "total"},
                 "label": "Этот месяц"},
                {"aggregate_id": "revenue_total",
                 "params": {"period_hint": "прошлый месяц", "group_by": "total"},
                 "label": "Прошлый месяц"}
            ],
            "topic": "statistics",
            "render_needed": true
        }"""
        planner = _make_planner(llm_json, registry)
        q = UserQuestion(user_id="1", text="Сравни выручку этого и прошлого месяца")
        plan = asyncio.run(planner.run_multi(q))

        assert plan.intent == "comparison"
        # date_from должен быть проставлен из period_hint
        assert "date_from" in plan.queries[0].params
        assert "date_from" in plan.queries[1].params
        # Даты у периодов разные
        assert plan.queries[0].params["date_from"] != plan.queries[1].params["date_from"]


# ── T033-3: Сравнение мастеров → 2 запроса с разным master_id ────────────────

class TestMasterComparison:
    """Сравнение мастеров → 2 запроса с разными master_id."""

    def test_master_comparison_two_queries(self, registry):
        llm_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total",
                 "params": {"master_id": 101, "date_from": "2026-04-01", "date_to": "2026-04-15"},
                 "label": "Мастер Иванова"},
                {"aggregate_id": "revenue_total",
                 "params": {"master_id": 202, "date_from": "2026-04-01", "date_to": "2026-04-15"},
                 "label": "Мастер Петрова"}
            ],
            "topic": "masters",
            "render_needed": true
        }"""
        planner = _make_planner(llm_json, registry)
        q = UserQuestion(user_id="1", text="Сравни мастеров Иванову и Петрову")
        plan = asyncio.run(planner.run_multi(q))

        assert plan.intent == "comparison"
        assert len(plan.queries) == 2
        master_ids = {q_obj.params.get("master_id") for q_obj in plan.queries}
        assert master_ids == {101, 202}

    def test_master_comparison_labels_preserved(self, registry):
        llm_json = """{
            "intent": "comparison",
            "queries": [
                {"aggregate_id": "revenue_total",
                 "params": {"master_id": 1, "date_from": "2026-04-01", "date_to": "2026-04-15"},
                 "label": "Мастер А"},
                {"aggregate_id": "revenue_total",
                 "params": {"master_id": 2, "date_from": "2026-04-01", "date_to": "2026-04-15"},
                 "label": "Мастер Б"}
            ],
            "topic": "masters",
            "render_needed": true
        }"""
        planner = _make_planner(llm_json, registry)
        q = UserQuestion(user_id="1", text="Сравни двух мастеров")
        plan = asyncio.run(planner.run_multi(q))

        labels = [aq.label for aq in plan.queries]
        assert "Мастер А" in labels
        assert "Мастер Б" in labels


# ── T033-4: Grouped bar chart рендерится без ошибок ──────────────────────────

class TestRenderComparison:
    """render_comparison: grouped bar chart с mock-данными, без исключений."""

    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib не установлен")
    def test_render_comparison_returns_png_bytes(self):
        results_a = [{"Revenue": 150000, "Visits": 200, "UniqueClients": 80}]
        results_b = [{"Revenue": 120000, "Visits": 180, "UniqueClients": 70}]

        png = render_comparison(
            topic="statistics",
            results_a=results_a,
            results_b=results_b,
            label_a="Этот месяц",
            label_b="Прошлый месяц",
        )

        assert isinstance(png, bytes)
        assert png[:4] == b"\x89PNG"

    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib не установлен")
    def test_render_comparison_with_empty_b_no_exception(self):
        """Один из наборов пустой — не должно быть исключения."""
        results_a = [{"Revenue": 100000, "Visits": 150}]
        results_b: list[dict] = []

        png = render_comparison(
            topic="statistics",
            results_a=results_a,
            results_b=results_b,
            label_a="Апрель",
            label_b="Март",
        )
        assert isinstance(png, bytes)
        assert png[:4] == b"\x89PNG"

    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib не установлен")
    def test_render_comparison_with_both_empty_no_exception(self):
        """Оба набора пустые — возвращает PNG пустого графика."""
        png = render_comparison(
            topic="statistics",
            results_a=[],
            results_b=[],
            label_a="Период 1",
            label_b="Период 2",
        )
        assert isinstance(png, bytes)
        assert png[:4] == b"\x89PNG"

    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib не установлен")
    def test_render_comparison_multiple_rows(self):
        """Несколько строк — суммируются корректно, PNG возвращается."""
        results_a = [
            {"Revenue": 50000, "Visits": 80},
            {"Revenue": 60000, "Visits": 90},
            {"Revenue": 40000, "Visits": 70},
        ]
        results_b = [
            {"Revenue": 45000, "Visits": 75},
            {"Revenue": 55000, "Visits": 85},
        ]
        png = render_comparison(
            topic="masters",
            results_a=results_a,
            results_b=results_b,
            label_a="Этот месяц",
            label_b="Прошлый месяц",
        )
        assert isinstance(png, bytes)
        assert png[:4] == b"\x89PNG"

    @pytest.mark.skipif(not HAS_MPL, reason="matplotlib не установлен")
    def test_render_comparison_masters_no_exception(self):
        """Мастера — данные с полем Revenue, без исключений."""
        results_a = [{"MasterName": "Иванова", "Revenue": 75000, "Visits": 50}]
        results_b = [{"MasterName": "Петрова", "Revenue": 60000, "Visits": 40}]

        png = render_comparison(
            topic="masters",
            results_a=results_a,
            results_b=results_b,
            label_a="Иванова",
            label_b="Петрова",
        )
        assert isinstance(png, bytes)
        assert png[:4] == b"\x89PNG"


# ── T033-5: Неполный период → analyst помечает в тексте ──────────────────────

class TestIncompleteCurrentMonth:
    """Если текущий период неполный → analyst добавляет пометку "(неполный период)"."""

    def test_is_incomplete_period_today(self):
        """Сегодняшняя дата → неполный период."""
        today = date.today().isoformat()
        assert AnalystAgent._is_incomplete_period(today) is True

    def test_is_incomplete_period_future(self):
        """Будущая дата → неполный период."""
        future = (date.today() + timedelta(days=5)).isoformat()
        assert AnalystAgent._is_incomplete_period(future) is True

    def test_is_incomplete_period_past(self):
        """Прошлая дата → полный период."""
        past = (date.today() - timedelta(days=1)).isoformat()
        assert AnalystAgent._is_incomplete_period(past) is False

    def test_is_incomplete_period_empty_string(self):
        assert AnalystAgent._is_incomplete_period("") is False

    def test_is_incomplete_period_invalid_string(self):
        assert AnalystAgent._is_incomplete_period("not-a-date") is False

    def test_format_comparison_marks_incomplete_period_a(self):
        """Если period_a неполный → в тексте есть "(неполный период)"."""
        analyst = _make_analyst()
        result_a = AggregateResult(
            aggregate_id="revenue_total",
            label="Этот месяц",
            rows=[{"Revenue": 150000, "Visits": 200}],
            row_count=1,
        )
        result_b = AggregateResult(
            aggregate_id="revenue_total",
            label="Прошлый месяц",
            rows=[{"Revenue": 120000, "Visits": 180}],
            row_count=1,
        )
        comparison = ComparisonResult(
            period_a="Этот месяц",
            period_b="Прошлый месяц",
            results_a=result_a,
            results_b=result_b,
        )
        text = analyst.format_comparison(comparison, incomplete_period_a=True)
        assert "(неполный период)" in text

    def test_format_comparison_no_incomplete_marker_when_full(self):
        """Оба периода полные → нет пометки."""
        analyst = _make_analyst()
        result_a = AggregateResult(
            aggregate_id="revenue_total",
            label="Прошлый месяц",
            rows=[{"Revenue": 150000}],
            row_count=1,
        )
        result_b = AggregateResult(
            aggregate_id="revenue_total",
            label="Позапрошлый месяц",
            rows=[{"Revenue": 120000}],
            row_count=1,
        )
        comparison = ComparisonResult(
            period_a="Прошлый месяц",
            period_b="Позапрошлый месяц",
            results_a=result_a,
            results_b=result_b,
        )
        text = analyst.format_comparison(comparison)
        assert "(неполный период)" not in text

    def test_format_comparison_includes_delta(self):
        """Дельта вычисляется и включается в текст."""
        analyst = _make_analyst()
        result_a = AggregateResult(
            aggregate_id="revenue_total",
            label="Апрель",
            rows=[{"Revenue": 150000}],
            row_count=1,
        )
        result_b = AggregateResult(
            aggregate_id="revenue_total",
            label="Март",
            rows=[{"Revenue": 120000}],
            row_count=1,
        )
        comparison = ComparisonResult(
            period_a="Апрель",
            period_b="Март",
            results_a=result_a,
            results_b=result_b,
        )
        text = analyst.format_comparison(comparison)
        # Дельта = (150000-120000)/120000*100 = 25%
        assert "+25.0%" in text

    def test_format_comparison_negative_delta(self):
        """Отрицательная дельта → знак минус в тексте."""
        analyst = _make_analyst()
        result_a = AggregateResult(
            aggregate_id="revenue_total",
            label="Апрель",
            rows=[{"Revenue": 90000}],
            row_count=1,
        )
        result_b = AggregateResult(
            aggregate_id="revenue_total",
            label="Март",
            rows=[{"Revenue": 100000}],
            row_count=1,
        )
        comparison = ComparisonResult(
            period_a="Апрель",
            period_b="Март",
            results_a=result_a,
            results_b=result_b,
        )
        text = analyst.format_comparison(comparison)
        # Дельта = -10%, в тексте минус (unicode \u2212 или "-")
        assert "10.0%" in text
        # Знак минуса должен быть (unicode или обычный)
        assert "\u2212" in text or "-" in text

    def test_format_comparison_empty_data(self):
        """Нет числовых данных → возвращает сообщение."""
        analyst = _make_analyst()
        result_a = AggregateResult(aggregate_id="revenue_total", rows=[], row_count=0)
        result_b = AggregateResult(aggregate_id="revenue_total", rows=[], row_count=0)
        comparison = ComparisonResult(
            period_a="Период 1",
            period_b="Период 2",
            results_a=result_a,
            results_b=result_b,
        )
        text = analyst.format_comparison(comparison)
        assert "нет" in text.lower() or "данн" in text.lower()

    def test_calc_deltas_positive(self):
        """Дельта положительная: a > b."""
        rows_a = [{"Revenue": 200, "Visits": 10}]
        rows_b = [{"Revenue": 100, "Visits": 8}]
        deltas = AnalystAgent._calc_deltas(rows_a, rows_b)
        assert pytest.approx(deltas["Revenue"], rel=1e-3) == 100.0
        assert pytest.approx(deltas["Visits"], rel=1e-3) == 25.0

    def test_calc_deltas_negative(self):
        """Дельта отрицательная: a < b."""
        rows_a = [{"Revenue": 80}]
        rows_b = [{"Revenue": 100}]
        deltas = AnalystAgent._calc_deltas(rows_a, rows_b)
        assert pytest.approx(deltas["Revenue"], rel=1e-3) == -20.0

    def test_calc_deltas_zero_base(self):
        """Делитель ноль → дельта 0."""
        rows_a = [{"Revenue": 100}]
        rows_b = [{"Revenue": 0}]
        deltas = AnalystAgent._calc_deltas(rows_a, rows_b)
        assert deltas["Revenue"] == 0.0

    def test_calc_deltas_multiple_rows_summed(self):
        """Несколько строк — суммируются перед расчётом."""
        rows_a = [{"Revenue": 50}, {"Revenue": 50}]  # 100 total
        rows_b = [{"Revenue": 80}]
        deltas = AnalystAgent._calc_deltas(rows_a, rows_b)
        assert pytest.approx(deltas["Revenue"], rel=1e-3) == 25.0
