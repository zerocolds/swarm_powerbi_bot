from __future__ import annotations

import logging
import os
import re
from datetime import date

from .base import Agent
from ..models import AggregateQuery, MultiPlan, Plan, QueryParams, UserQuestion
from ..services.aggregate_registry import AggregateRegistry
from ..services.llm_client import LLMClient
from ..services.topic_registry import detect_topic, get_procedure

logger = logging.getLogger(__name__)

# Если True — используем v2 процедуры (spKDO_Aggregate/ClientList/CommAgg)
# Если False — маппим обратно на старые процедуры (spKDO_Outflow и т.д.)
_USE_V2 = os.getenv("USE_V2_PROCEDURES", "").strip().lower() in {"1", "true", "yes"}

# Маппинг (procedure, group_by/filter) → topic для chart_renderer и analyst
_PROCEDURE_TOPIC_MAP: dict[tuple[str, str], str] = {
    # Aggregate
    ("spKDO_Aggregate", "total"): "statistics",
    ("spKDO_Aggregate", "week"): "trend",
    ("spKDO_Aggregate", "month"): "trend",
    ("spKDO_Aggregate", "master"): "masters",
    ("spKDO_Aggregate", "service"): "services",
    ("spKDO_Aggregate", "salon"): "statistics",
    ("spKDO_Aggregate", "channel"): "referrals",
    # ClientList
    ("spKDO_ClientList", "outflow"): "outflow",
    ("spKDO_ClientList", "leaving"): "leaving",
    ("spKDO_ClientList", "forecast"): "forecast",
    ("spKDO_ClientList", "noshow"): "noshow",
    ("spKDO_ClientList", "quality"): "quality",
    ("spKDO_ClientList", "birthday"): "birthday",
    ("spKDO_ClientList", "all"): "all_clients",
    # CommAgg
    ("spKDO_CommAgg", "all"): "communications",
    ("spKDO_CommAgg", "waitlist"): "waitlist",
    ("spKDO_CommAgg", "opz"): "opz",
}

# Старые процедуры, которые LLM может вернуть (абонементы, обучение)
_LEGACY_PROCEDURE_TOPIC = {
    "spKDO_Attachments": "attachments",
    "spKDO_Training": "training",
}

# Допустимые имена процедур (whitelist)
_ALLOWED_PROCEDURES = {
    "spKDO_Aggregate", "spKDO_ClientList", "spKDO_CommAgg",
    "spKDO_Attachments", "spKDO_Training",
    # Старые — для обратной совместимости fallback
    "spKDO_Statistics", "spKDO_Trend", "spKDO_Outflow", "spKDO_Leaving",
    "spKDO_Forecast", "spKDO_Masters", "spKDO_Services", "spKDO_Communications",
    "spKDO_Referrals", "spKDO_Quality", "spKDO_NoShow", "spKDO_AllClients",
    "spKDO_Birthday", "spKDO_WaitList", "spKDO_OPZ",
}

# Маппинг v2 → v1: topic → старая процедура (для работы до деплоя v2)
_V2_TO_V1: dict[str, str] = {
    "statistics": "dbo.spKDO_Statistics",
    "trend": "dbo.spKDO_Trend",
    "outflow": "dbo.spKDO_Outflow",
    "leaving": "dbo.spKDO_Leaving",
    "forecast": "dbo.spKDO_Forecast",
    "masters": "dbo.spKDO_Masters",
    "services": "dbo.spKDO_Services",
    "communications": "dbo.spKDO_Communications",
    "referrals": "dbo.spKDO_Referrals",
    "quality": "dbo.spKDO_Quality",
    "noshow": "dbo.spKDO_NoShow",
    "all_clients": "dbo.spKDO_AllClients",
    "birthday": "dbo.spKDO_Birthday",
    "waitlist": "dbo.spKDO_WaitList",
    "attachments": "dbo.spKDO_Attachments",
    "training": "dbo.spKDO_Training",
    "opz": "dbo.spKDO_OPZ",
}


class PlannerAgent(Agent):
    name = "planner"

    REPORT_TAG_RE = re.compile(r"report\s*:\s*([\w\-/]+)", re.IGNORECASE)

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        aggregate_registry: AggregateRegistry | None = None,
    ):
        self.llm_client = llm_client
        self.aggregate_registry = aggregate_registry

    async def run_multi(self, question: UserQuestion) -> MultiPlan:
        """T024: Одношаговое LLM-планирование с каталогом агрегатов → MultiPlan.

        Алгоритм:
        1. Если есть LLM + aggregate_registry — строим catalog/semantic промпт
           и вызываем LLMClient.plan_aggregates()
        2. Парсим JSON → проверяем каждый aggregate_id против whitelist
        3. Если ANY aggregate_id невалиден → fallback на TopicRegistry
        4. Fallback: TopicRegistry detect_topic → один AggregateQuery
        """
        text = question.text.lower()
        render_needed = "без картинки" not in text and "text only" not in text

        # Пробуем LLM-планирование с каталогом агрегатов
        if self.llm_client and self.aggregate_registry:
            multi_plan = await self._llm_plan_multi(question, render_needed)
            if multi_plan is not None:
                return multi_plan

        # Fallback: keyword-matching → один AggregateQuery
        return self._fallback_multi_plan(question, render_needed)

    async def _llm_plan_multi(
        self, question: UserQuestion, render_needed: bool
    ) -> MultiPlan | None:
        """Вызывает LLM для получения MultiPlan с каталогом агрегатов."""
        registry = self.aggregate_registry
        assert registry is not None

        # Формируем промпт из каталога агрегатов
        catalog_lines: list[str] = []
        for agg in registry.list_aggregates():
            agg_id = agg.get("id", "")
            name = agg.get("name", "")
            desc = agg.get("description", "")
            allowed = ", ".join(agg.get("allowed_group_by", []))
            catalog_lines.append(
                f"- {agg_id}: {name}. {desc} "
                f"(allowed_group_by: {allowed})"
            )
        catalog_prompt = "\n".join(catalog_lines) if catalog_lines else "(пусто)"
        semantic_prompt = "(нет семантического каталога)"

        raw_dict = await self.llm_client.plan_aggregates(  # type: ignore[union-attr]
            question=question.text,
            catalog_prompt=catalog_prompt,
            semantic_prompt=semantic_prompt,
        )
        if not raw_dict:
            return None

        queries_raw = raw_dict.get("queries")
        if not queries_raw or not isinstance(queries_raw, list):
            logger.warning("plan_aggregates: 'queries' is missing or empty")
            return None

        # Валидируем каждый aggregate_id против whitelist
        queries: list[AggregateQuery] = []
        for q in queries_raw:
            agg_id = q.get("aggregate_id", "")
            if not registry.get_aggregate(agg_id):
                logger.warning(
                    "plan_aggregates: aggregate_id %r not in catalog — falling back",
                    agg_id,
                )
                return None  # ANY invalid → полный fallback
            queries.append(AggregateQuery(
                aggregate_id=agg_id,
                params=q.get("params", {}),
                label=q.get("label", ""),
            ))

        if not queries:
            return None

        topic = raw_dict.get("topic", "statistics")
        intent = raw_dict.get("intent", "single")

        return MultiPlan(
            objective=question.text,
            intent=intent,
            queries=queries,
            topic=topic,
            render_needed=render_needed,
            notes=["planner_v2:llm"],
        )

    def _fallback_multi_plan(
        self, question: UserQuestion, render_needed: bool
    ) -> MultiPlan:
        """Fallback: keyword-based TopicRegistry → один AggregateQuery."""
        topic = detect_topic(question.text, last_topic=question.last_topic)

        # Формируем AggregateQuery используя topic как aggregate_id
        agg_query = AggregateQuery(
            aggregate_id=topic,
            params={},
            label=topic,
        )

        return MultiPlan(
            objective=question.text,
            intent="single",
            queries=[agg_query],
            topic=topic,
            render_needed=render_needed,
            notes=["planner_v2:keyword"],
        )

    async def run(self, question: UserQuestion) -> Plan:
        text = question.text.lower()

        sql_needed = "только powerbi" not in text and "only powerbi" not in text
        powerbi_needed = "только sql" not in text and "only sql" not in text
        render_needed = "без картинки" not in text and "text only" not in text

        # Пробуем LLM-планирование
        llm_result = await self._llm_plan(question)
        used_llm = llm_result is not None

        if used_llm:
            query_params = llm_result
            topic = self._derive_topic(query_params, question)
        else:
            # Fallback: keyword-matching → старые процедуры
            topic = detect_topic(question.text, last_topic=question.last_topic)
            query_params = self._fallback_params(question, topic)

        notes: list[str] = [f"topic:{topic}"]
        notes.append("planner:llm" if used_llm else "planner:keyword")

        # Флаги анализа
        if any(kw in text for kw in ("сравни", "compare", "сравнен")):
            notes.append("comparison_requested")
        if any(kw in text for kw in ("тренд", "trend", "динамик", "изменен")):
            notes.append("trend_requested")
        if any(kw in text for kw in ("прогноз", "forecast", "предсказ")):
            notes.append("forecast_requested")
        if any(kw in text for kw in ("топ", "лучш", "худш", "рейтинг", "ranking")):
            notes.append("ranking_requested")

        # Детекция группировки
        if any(kw in text for kw in ("по салон", "по объект", "по филиал")):
            notes.append("breakdown_by_object")
        if "по мастер" in text:
            notes.append("breakdown_by_master")

        # Детекция периода
        if "недел" in text:
            notes.append("period:week")
        elif "месяц" in text:
            notes.append("period:month")
        elif "квартал" in text:
            notes.append("period:quarter")
        elif "год" in text and "новый год" not in text:
            notes.append("period:year")

        # Если LLM не доступен: клиентские темы + сравнение → trend (fallback logic)
        if not used_llm:
            _CLIENT_TOPICS = {"outflow", "leaving", "all_clients", "noshow", "forecast"}
            if topic in _CLIENT_TOPICS and (
                "comparison_requested" in notes or "trend_requested" in notes
            ):
                notes.append(f"original_topic:{topic}")
                topic = "trend"
                query_params.procedure = get_procedure("trend")

        # Если v2 процедуры не задеплоены — маппим обратно на старые
        if not _USE_V2 and query_params and query_params.procedure in (
            "spKDO_Aggregate", "spKDO_ClientList", "spKDO_CommAgg",
        ):
            old_proc = _V2_TO_V1.get(topic)
            if old_proc:
                logger.info(
                    "v2→v1 fallback: %s → %s (topic=%s)",
                    query_params.procedure, old_proc, topic,
                )
                query_params.procedure = old_proc
                # Убираем v2-параметры — старые процедуры их не принимают
                query_params.group_by = ""
                query_params.filter = ""
                query_params.reason = ""

        report_id = question.report_id or self._extract_report_id(question.text)

        return Plan(
            objective=question.text,
            topic=topic,
            sql_needed=sql_needed,
            powerbi_needed=powerbi_needed,
            render_needed=render_needed,
            render_report_id=report_id,
            notes=notes,
            query_params=query_params,
        )

    async def _llm_plan(self, question: UserQuestion) -> QueryParams | None:
        """Вызывает LLM для планирования запроса."""
        if not self.llm_client:
            return None

        today = date.today().isoformat()
        result = await self.llm_client.plan_query(
            question.text, today=today, last_topic=question.last_topic,
        )
        if not result:
            return None

        # Нормализуем имя процедуры
        procedure = result.get("procedure", "").strip()
        procedure = procedure.replace("dbo.", "")
        if procedure not in _ALLOWED_PROCEDURES:
            return None

        return QueryParams(
            procedure=procedure,
            date_from=result.get("date_from", ""),
            date_to=result.get("date_to", ""),
            object_id=question.object_id,  # ObjectId всегда из подписки
            master_name=result.get("master_name", ""),
            top=result.get("top", 20),
            group_by=result.get("group_by", ""),
            filter=result.get("filter", ""),
            reason=result.get("reason", ""),
        )

    def _derive_topic(self, qp: QueryParams, question: UserQuestion) -> str:
        """Определяет topic из параметров LLM-запроса."""
        proc = qp.procedure

        # Старые процедуры (Attachments, Training)
        if proc in _LEGACY_PROCEDURE_TOPIC:
            return _LEGACY_PROCEDURE_TOPIC[proc]

        # Новые универсальные процедуры
        if proc == "spKDO_Aggregate":
            key = (proc, qp.group_by or "total")
            return _PROCEDURE_TOPIC_MAP.get(key, "statistics")

        if proc == "spKDO_ClientList":
            key = (proc, qp.filter or "all")
            return _PROCEDURE_TOPIC_MAP.get(key, "all_clients")

        if proc == "spKDO_CommAgg":
            key = (proc, qp.reason or "all")
            return _PROCEDURE_TOPIC_MAP.get(key, "communications")

        # Если LLM вернул старую процедуру — нормализуем
        raw = proc.replace("spKDO_", "").lower()
        from ..services.topic_registry import _TOPICS_BY_ID
        if raw in _TOPICS_BY_ID:
            return raw
        _ALIASES = {
            "allclients": "all_clients", "all_clients": "all_clients",
        }
        return _ALIASES.get(raw, detect_topic(question.text, last_topic=question.last_topic))

    def _fallback_params(self, question: UserQuestion, topic: str) -> QueryParams:
        """Fallback: формирует QueryParams из keyword-детекции (старые процедуры)."""
        from ..services.sql_client import extract_date_params
        dates = extract_date_params(question.text)
        procedure = get_procedure(topic)

        return QueryParams(
            procedure=procedure,
            date_from=dates["DateFrom"].isoformat(),
            date_to=dates["DateTo"].isoformat(),
            object_id=question.object_id,
            top=20,
        )

    def _extract_report_id(self, text: str) -> str | None:
        match = self.REPORT_TAG_RE.search(text)
        if not match:
            return None
        return match.group(1).strip()
