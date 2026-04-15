"""Тесты LLM-планировщика запросов (v2 — универсальные процедуры).

Проверяет:
- Парсинг JSON из ответа LLM
- plan_query() с мок-LLM
- PlannerAgent с LLM vs fallback
- Маппинг (procedure, group_by/filter) → topic
- Передачу QueryParams в SQLAgent
"""
import asyncio
from unittest.mock import AsyncMock


from swarm_powerbi_bot.agents.planner import PlannerAgent
from swarm_powerbi_bot.models import QueryParams, UserQuestion
from swarm_powerbi_bot.services.llm_client import LLMClient, _PLANNER_SYSTEM_PROMPT


# ── Парсинг JSON из LLM-ответа ─────────────────────────────────

class TestPlanJsonParsing:
    """LLM может вернуть JSON в разных обёртках."""

    def setup_method(self):
        from swarm_powerbi_bot.config import Settings
        self.client = LLMClient(Settings())

    def test_clean_json(self):
        raw = '{"procedure": "spKDO_Aggregate", "group_by": "total", "filter": "", "reason": "", "date_from": "2026-03-15", "date_to": "2026-04-14", "top": 20, "master_name": ""}'
        result = self.client._parse_plan_json(raw)
        assert result is not None
        assert result["procedure"] == "spKDO_Aggregate"
        assert result["group_by"] == "total"

    def test_json_in_markdown(self):
        raw = '```json\n{"procedure": "spKDO_Aggregate", "group_by": "week", "filter": "", "reason": "", "date_from": "2026-01-01", "date_to": "2026-04-14", "top": 20, "master_name": ""}\n```'
        result = self.client._parse_plan_json(raw)
        assert result is not None
        assert result["procedure"] == "spKDO_Aggregate"
        assert result["group_by"] == "week"

    def test_json_with_prefix_text(self):
        raw = 'Вот параметры: {"procedure": "spKDO_Aggregate", "group_by": "master", "filter": "", "reason": "", "date_from": "2026-03-15", "date_to": "2026-04-14", "top": 10, "master_name": "Анна"}'
        result = self.client._parse_plan_json(raw)
        assert result is not None
        assert result["master_name"] == "Анна"

    def test_no_json(self):
        result = self.client._parse_plan_json("Я не понимаю вопрос")
        assert result is None

    def test_invalid_json(self):
        result = self.client._parse_plan_json("{broken json here}")
        assert result is None

    def test_json_without_procedure(self):
        result = self.client._parse_plan_json('{"group_by": "week", "date_from": "2026-01-01"}')
        assert result is None


# ── PlannerAgent с LLM (v2 — универсальные процедуры) ──────────

class TestPlannerWithLLM:
    """PlannerAgent использует LLM для сборки запроса из компонентов."""

    def _make_planner(self, llm_response: dict | None):
        from swarm_powerbi_bot.config import Settings
        llm = LLMClient(Settings())
        llm.plan_query = AsyncMock(return_value=llm_response)
        return PlannerAgent(llm_client=llm)

    def test_llm_outflow_topic(self):
        """LLM определяет тему outflow, процедура зависит от USE_V2."""
        planner = self._make_planner({
            "procedure": "spKDO_ClientList",
            "group_by": "list",
            "filter": "outflow",
            "reason": "",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="покажи отток за месяц"),
        ))
        assert plan.topic == "outflow"
        assert plan.query_params is not None
        assert "planner:llm" in plan.notes
        # Процедура: v2=ClientList, v1=Outflow — главное topic верный
        assert "Outflow" in plan.query_params.procedure or "ClientList" in plan.query_params.procedure

    def test_llm_trend_topic(self):
        """LLM определяет тренд по неделям."""
        planner = self._make_planner({
            "procedure": "spKDO_Aggregate",
            "group_by": "week",
            "filter": "",
            "reason": "",
            "date_from": "2026-01-14",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="сравни по неделям", last_topic="outflow"),
        ))
        assert plan.topic == "trend"
        assert "Trend" in plan.query_params.procedure or "Aggregate" in plan.query_params.procedure

    def test_llm_masters_with_name(self):
        planner = self._make_planner({
            "procedure": "spKDO_Aggregate",
            "group_by": "master",
            "filter": "",
            "reason": "",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
            "top": 10,
            "master_name": "Анна",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="покажи загрузку мастера Анна"),
        ))
        assert plan.topic == "masters"
        assert plan.query_params.master_name == "Анна"

    def test_llm_communications_topic(self):
        planner = self._make_planner({
            "procedure": "spKDO_CommAgg",
            "group_by": "reason",
            "filter": "",
            "reason": "all",
            "date_from": "2026-04-07",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="коммуникации за неделю"),
        ))
        assert plan.topic == "communications"

    def test_llm_outflow_by_master_topic(self):
        """LLM: отток по мастерам → topic=outflow."""
        planner = self._make_planner({
            "procedure": "spKDO_ClientList",
            "group_by": "master",
            "filter": "outflow",
            "reason": "",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="отток по мастерам"),
        ))
        assert plan.topic == "outflow"

    def test_llm_fallback_on_none(self):
        """Если LLM недоступен — fallback на keyword-matching."""
        planner = self._make_planner(None)
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert plan.topic == "outflow"
        assert plan.query_params is not None
        assert "planner:keyword" in plan.notes

    def test_llm_preserves_object_id(self):
        planner = self._make_planner({
            "procedure": "spKDO_Aggregate",
            "group_by": "total",
            "filter": "",
            "reason": "",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
            "top": 20,
            "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="статистика", object_id=12345),
        ))
        assert plan.query_params.object_id == 12345

    def test_llm_invalid_procedure_fallback(self):
        """Если LLM вернул невалидную процедуру — fallback."""
        planner = self._make_planner({
            "procedure": "spKDO_Hacked; DROP TABLE",
            "group_by": "total",
            "date_from": "2026-03-15",
            "date_to": "2026-04-14",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="статистика за неделю"),
        ))
        assert "planner:keyword" in plan.notes  # fallback


# ── PlannerAgent без LLM (fallback) ────────────────────────────

class TestPlannerFallback:
    def test_no_llm_outflow(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="отток за месяц"),
        ))
        assert plan.topic == "outflow"
        assert "planner:keyword" in plan.notes

    def test_no_llm_statistics(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="покажи статистику за неделю"),
        ))
        assert plan.topic == "statistics"

    def test_no_llm_with_context_retention(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="подробнее", last_topic="outflow"),
        ))
        assert plan.topic == "outflow"

    def test_no_llm_comparison_switches_to_trend(self):
        planner = PlannerAgent()
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="сравни отток по неделям"),
        ))
        assert plan.topic == "trend"
        assert "comparison_requested" in plan.notes


# ── Маппинг topic ───────────────────────────────────────────────

class TestTopicMapping:
    """_derive_topic корректно маппит (procedure, params) → topic."""

    def setup_method(self):
        self.planner = PlannerAgent()
        self.q = UserQuestion(user_id="1", text="test")

    def test_aggregate_mappings(self):
        cases = {
            "total": "statistics",
            "week": "trend",
            "month": "trend",
            "master": "masters",
            "service": "services",
            "channel": "referrals",
        }
        for group_by, expected_topic in cases.items():
            qp = QueryParams(procedure="spKDO_Aggregate", group_by=group_by)
            topic = self.planner._derive_topic(qp, self.q)
            assert topic == expected_topic, f"group_by={group_by}"

    def test_clientlist_mappings(self):
        cases = {
            "outflow": "outflow",
            "leaving": "leaving",
            "forecast": "forecast",
            "noshow": "noshow",
            "quality": "quality",
            "birthday": "birthday",
            "all": "all_clients",
        }
        for filter_val, expected_topic in cases.items():
            qp = QueryParams(procedure="spKDO_ClientList", filter=filter_val)
            topic = self.planner._derive_topic(qp, self.q)
            assert topic == expected_topic, f"filter={filter_val}"

    def test_commagg_mappings(self):
        cases = {
            "all": "communications",
            "waitlist": "waitlist",
            "opz": "opz",
        }
        for reason, expected_topic in cases.items():
            qp = QueryParams(procedure="spKDO_CommAgg", reason=reason)
            topic = self.planner._derive_topic(qp, self.q)
            assert topic == expected_topic, f"reason={reason}"

    def test_legacy_procedures(self):
        qp = QueryParams(procedure="spKDO_Attachments")
        assert self.planner._derive_topic(qp, self.q) == "attachments"

        qp = QueryParams(procedure="spKDO_Training")
        assert self.planner._derive_topic(qp, self.q) == "training"


# ── Промпт планировщика v2 ─────────────────────────────────────

class TestPlannerPrompt:
    def test_prompt_has_3_procedures(self):
        assert "spKDO_Aggregate" in _PLANNER_SYSTEM_PROMPT
        assert "spKDO_ClientList" in _PLANNER_SYSTEM_PROMPT
        assert "spKDO_CommAgg" in _PLANNER_SYSTEM_PROMPT

    def test_prompt_has_group_by_options(self):
        assert "group_by" in _PLANNER_SYSTEM_PROMPT
        assert "week" in _PLANNER_SYSTEM_PROMPT
        assert "month" in _PLANNER_SYSTEM_PROMPT
        assert "master" in _PLANNER_SYSTEM_PROMPT

    def test_prompt_has_filter_options(self):
        assert "outflow" in _PLANNER_SYSTEM_PROMPT
        assert "leaving" in _PLANNER_SYSTEM_PROMPT
        assert "forecast" in _PLANNER_SYSTEM_PROMPT

    def test_prompt_has_context_placeholder(self):
        assert "{context}" in _PLANNER_SYSTEM_PROMPT
        assert "{today}" in _PLANNER_SYSTEM_PROMPT

    def test_prompt_has_json_format(self):
        assert '"procedure"' in _PLANNER_SYSTEM_PROMPT
        assert '"group_by"' in _PLANNER_SYSTEM_PROMPT


# ── E2E: LLM собирает запрос — покрытие сценариев ─────────────

class TestLLMScenarios:
    """Реальные пользовательские вопросы → ожидаемые компоненты."""

    def _make_planner(self, llm_response):
        from swarm_powerbi_bot.config import Settings
        llm = LLMClient(Settings())
        llm.plan_query = AsyncMock(return_value=llm_response)
        return PlannerAgent(llm_client=llm)

    def test_revenue_by_week(self):
        """'выручка по неделям' → Aggregate+week (не Services!)"""
        planner = self._make_planner({
            "procedure": "spKDO_Aggregate",
            "group_by": "week",
            "filter": "", "reason": "",
            "date_from": "2026-03-15", "date_to": "2026-04-14",
            "top": 20, "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="выручка по неделям"),
        ))
        assert plan.topic == "trend"  # week → trend
        # group_by очищается при v2→v1 fallback, но topic корректный

    def test_outflow_by_salon(self):
        """'отток по салонам' — нет такого в ClientList, но Aggregate+salon тоже не то.
        Правильно: ClientList+outflow (LLM должен понять что отток = ClientList)."""
        planner = self._make_planner({
            "procedure": "spKDO_ClientList",
            "group_by": "list", "filter": "outflow", "reason": "",
            "date_from": "2026-03-15", "date_to": "2026-04-14",
            "top": 20, "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="покажи отток"),
        ))
        assert plan.topic == "outflow"

    def test_waitlist_commagg(self):
        """'лист ожидания' → CommAgg+waitlist."""
        planner = self._make_planner({
            "procedure": "spKDO_CommAgg",
            "group_by": "list", "filter": "", "reason": "waitlist",
            "date_from": "2026-03-15", "date_to": "2026-04-14",
            "top": 20, "master_name": "",
        })
        plan = asyncio.run(planner.run(
            UserQuestion(user_id="1", text="лист ожидания"),
        ))
        assert plan.topic == "waitlist"
