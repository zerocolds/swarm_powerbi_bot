from __future__ import annotations

import calendar
import logging
import os
import re
from datetime import date, timedelta

from .base import Agent
from ..models import AggregateParams, AggregateQuery, MultiPlan, Plan, QueryParams, UserQuestion
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
    "spKDO_Aggregate",
    "spKDO_ClientList",
    "spKDO_CommAgg",
    "spKDO_Attachments",
    "spKDO_Training",
    # Старые — для обратной совместимости fallback
    "spKDO_Statistics",
    "spKDO_Trend",
    "spKDO_Outflow",
    "spKDO_Leaving",
    "spKDO_Forecast",
    "spKDO_Masters",
    "spKDO_Services",
    "spKDO_Communications",
    "spKDO_Referrals",
    "spKDO_Quality",
    "spKDO_NoShow",
    "spKDO_AllClients",
    "spKDO_Birthday",
    "spKDO_WaitList",
    "spKDO_OPZ",
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


def _resolve_period(hint: str) -> tuple[str, str]:
    """Преобразует словесный период в пару (date_from, date_to) в формате ISO.

    Поддерживаемые значения hint:
    - "этот месяц" / "текущий месяц" → 1-й день текущего месяца .. сегодня
    - "прошлый месяц" / "предыдущий месяц" → полный предыдущий месяц
    - "прошлый квартал" / "предыдущий квартал" → полный предыдущий квартал
    - "эта неделя" / "текущая неделя" → понедельник текущей недели .. сегодня
    - "прошлая неделя" / "предыдущая неделя" → полная предыдущая неделя (пн-вс)
    - Всё остальное → текущий месяц (как "этот месяц")
    """
    today = date.today()
    hint_lower = hint.lower().strip()

    if hint_lower in ("этот месяц", "текущий месяц"):
        date_from = today.replace(day=1)
        date_to = today
        return date_from.isoformat(), date_to.isoformat()

    if hint_lower in ("прошлый месяц", "предыдущий месяц"):
        first_of_current = today.replace(day=1)
        last_of_prev = first_of_current - timedelta(days=1)
        date_from = last_of_prev.replace(day=1)
        date_to = last_of_prev
        return date_from.isoformat(), date_to.isoformat()

    if hint_lower in ("прошлый квартал", "предыдущий квартал"):
        current_quarter = (today.month - 1) // 3 + 1
        if current_quarter == 1:
            # Q4 прошлого года
            date_from = date(today.year - 1, 10, 1)
            date_to = date(today.year - 1, 12, 31)
        else:
            prev_q_start_month = (current_quarter - 2) * 3 + 1
            date_from = date(today.year, prev_q_start_month, 1)
            last_month = prev_q_start_month + 2
            last_day = calendar.monthrange(today.year, last_month)[1]
            date_to = date(today.year, last_month, last_day)
        return date_from.isoformat(), date_to.isoformat()

    if hint_lower in ("эта неделя", "текущая неделя"):
        monday = today - timedelta(days=today.weekday())
        return monday.isoformat(), today.isoformat()

    if hint_lower in ("прошлая неделя", "предыдущая неделя"):
        monday_this = today - timedelta(days=today.weekday())
        monday_prev = monday_this - timedelta(weeks=1)
        sunday_prev = monday_this - timedelta(days=1)
        return monday_prev.isoformat(), sunday_prev.isoformat()

    # По умолчанию — текущий месяц
    date_from = today.replace(day=1)
    return date_from.isoformat(), today.isoformat()


class PlannerAgent(Agent):
    name = "planner"

    REPORT_TAG_RE = re.compile(r"report\s*:\s*([\w\-/]+)", re.IGNORECASE)

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        aggregate_registry: AggregateRegistry | None = None,
        semantic_catalog_path: str = "",
    ):
        self.llm_client = llm_client
        self.aggregate_registry = aggregate_registry
        self._semantic_prompt = self._load_semantic_catalog(semantic_catalog_path)

    @staticmethod
    def _load_semantic_catalog(path: str) -> str:
        """Загружает semantic-catalog.yaml как текст для LLM промпта."""
        if not path:
            return "(нет семантического каталога)"
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                return content
        except FileNotFoundError:
            logger.info("Semantic catalog not found at %s — using placeholder", path)
        except Exception as exc:
            logger.warning("Failed to load semantic catalog from %s: %s", path, exc)
        return "(нет семантического каталога)"

    def multi_plan_to_plan(self, multi_plan: MultiPlan, question: UserQuestion) -> Plan:
        """Конвертирует MultiPlan в legacy Plan для обратной совместимости."""
        return Plan(
            objective=multi_plan.objective,
            topic=multi_plan.topic,
            sql_needed=bool(multi_plan.queries),
            powerbi_needed=False,
            render_needed=multi_plan.render_needed,
            notes=list(multi_plan.notes),
        )

    @staticmethod
    def empty_plan(text: str) -> Plan:
        """Минимальный Plan при сбое планировщика."""
        return Plan(
            objective=text,
            topic="statistics",
            sql_needed=False,
            powerbi_needed=False,
            render_needed=False,
            notes=["planner:error"],
        )

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
        if registry is None:
            return None

        # Формируем промпт из каталога агрегатов
        catalog_lines: list[str] = []
        for agg in registry.list_aggregates():
            agg_id = agg.get("id", "")
            name = agg.get("name", "")
            desc = agg.get("description", "")
            allowed = ", ".join(agg.get("allowed_group_by", []))
            catalog_lines.append(
                f"- {agg_id}: {name}. {desc} (allowed_group_by: {allowed})"
            )
        catalog_prompt = "\n".join(catalog_lines) if catalog_lines else "(пусто)"
        semantic_prompt = self._semantic_prompt

        raw_dict = await self.llm_client.plan_aggregates(  # type: ignore[union-attr]
            question=question.text,
            catalog_prompt=catalog_prompt,
            semantic_prompt=semantic_prompt,
            last_topic=question.last_topic,
        )
        if not raw_dict:
            return None

        queries_raw = raw_dict.get("queries")
        if not queries_raw or not isinstance(queries_raw, list):
            logger.warning("plan_aggregates: 'queries' is missing or empty")
            return None

        _ALLOWED_INTENTS = {"single", "comparison", "decomposition", "trend", "ranking"}
        raw_intent = raw_dict.get("intent", "single")
        intent = raw_intent if raw_intent in _ALLOWED_INTENTS else "single"
        if raw_intent != intent:
            logger.warning(
                "plan_aggregates: unknown intent %r from LLM, falling back to 'single'",
                raw_intent,
            )

        # T037/T038: для декомпозиции допускаем до 5 запросов; глобальный max — 10
        _MAX_QUERIES_DECOMPOSITION = 5
        _MAX_QUERIES_DEFAULT = 10
        max_queries = (
            _MAX_QUERIES_DECOMPOSITION
            if intent == "decomposition"
            else _MAX_QUERIES_DEFAULT
        )
        queries_raw = queries_raw[:max_queries]

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
            raw_params = dict(q.get("params", {}))
            # Always scope to the subscriber's salon — even for aggregates that
            # mark object_id as optional (e.g. revenue_by_salon).  Without this,
            # any authenticated user can read data across all salons (IDOR).
            if "object_id" not in raw_params and question.object_id is not None:
                raw_params["object_id"] = question.object_id
            queries.append(
                AggregateQuery(
                    aggregate_id=agg_id,
                    params=AggregateParams(raw_params),
                    label=q.get("label", ""),
                )
            )

        if not queries:
            return None

        topic = raw_dict.get("topic", "statistics")
        # intent was already extracted above for query limit calculation

        # Разрешаем period_hint → конкретные даты для ВСЕХ интентов
        for q_obj in queries:
            period_hint = q_obj.params.get("period_hint", "")
            if period_hint and "date_from" not in q_obj.params:
                resolved_from, resolved_to = _resolve_period(period_hint)
                q_obj.params["date_from"] = resolved_from
                q_obj.params["date_to"] = resolved_to

        # T034: для intent="comparison" убеждаемся что есть ровно 2 запроса
        if intent == "comparison":
            if len(queries) < 2:
                logger.warning(
                    "plan_aggregates: comparison intent but only %d queries — falling back",
                    len(queries),
                )
                return None

        return MultiPlan(
            objective=question.text,
            intent=intent,
            queries=queries,
            topic=topic,
            render_needed=render_needed,
            notes=["planner_v2:llm"],
        )

    _COMPARISON_KEYWORDS = {"сравни", "сравнен", "сравнить", "сравнение", "compare", "сопостав", "vs"}
    _CLIENT_AGGREGATES = {
        "clients_outflow", "clients_leaving", "clients_forecast",
        "clients_noshow", "clients_quality", "clients_birthday", "clients_all",
    }
    # Маппинг legacy TopicRegistry topic_id → catalog aggregate_id
    _LEGACY_TO_CATALOG: dict[str, str] = {
        "outflow": "clients_outflow",
        "leaving": "clients_leaving",
        "forecast": "clients_forecast",
        "noshow": "clients_noshow",
        "quality": "clients_quality",
        "birthday": "clients_birthday",
        "all_clients": "clients_all",
        "statistics": "revenue_total",
        "services": "revenue_by_service",
        "masters": "revenue_by_master",
        "communications": "comm_all_by_reason",
    }

    def _fallback_multi_plan(
        self, question: UserQuestion, render_needed: bool
    ) -> MultiPlan:
        """Fallback: keyword-based TopicRegistry → AggregateQuery(s).

        Определяет intent=comparison по ключевым словам и генерирует
        2 запроса с разными периодами при наличии контекста (last_topic).
        """
        topic = detect_topic(question.text, last_topic=question.last_topic)
        text_lower = question.text.lower()

        is_comparison = any(kw in text_lower for kw in self._COMPARISON_KEYWORDS)

        if is_comparison and question.last_topic:
            # Проверяем что last_topic — валидный catalog aggregate_id
            registry = self.aggregate_registry
            agg_id = question.last_topic
            if registry and not registry.get_aggregate(agg_id):
                # Пробуем маппинг legacy topic → catalog aggregate_id
                mapped = self._LEGACY_TO_CATALOG.get(agg_id, "")
                agg_id = mapped if mapped and registry.get_aggregate(mapped) else ""
            if not agg_id:
                # Нет валидного aggregate_id для comparison → обычный single
                pass
            else:
                # Для клиентских агрегатов — group_by=status (агрегированные цифры)
                group_by = "status" if agg_id in self._CLIENT_AGGREGATES else ""
                today = date.today()
                first_of_current = today.replace(day=1)
                last_of_prev = first_of_current - timedelta(days=1)
                first_of_prev = last_of_prev.replace(day=1)

                params_prev: dict = {
                    "date_from": first_of_prev.isoformat(),
                    "date_to": last_of_prev.isoformat(),
                }
                params_curr: dict = {
                    "date_from": first_of_current.isoformat(),
                    "date_to": today.isoformat(),
                }
                # H4: object_id обязателен для большинства агрегатов
                if question.object_id is not None:
                    params_prev["object_id"] = question.object_id
                    params_curr["object_id"] = question.object_id
                if group_by:
                    params_prev["group_by"] = group_by
                    params_curr["group_by"] = group_by

                _RU_MONTHS = [
                    "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
                ]
                prev_label = f"{_RU_MONTHS[first_of_prev.month]} {first_of_prev.year}"
                curr_label = f"{_RU_MONTHS[first_of_current.month]} {first_of_current.year}"

                queries = [
                    AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_prev), label=prev_label),
                    AggregateQuery(aggregate_id=agg_id, params=AggregateParams(params_curr), label=curr_label),
                ]
                return MultiPlan(
                    objective=question.text,
                    intent="comparison",
                    queries=queries,
                    topic=agg_id,
                    render_needed=render_needed,
                    notes=["planner_v2:keyword", "comparison:fallback"],
                )

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
        if (
            not _USE_V2
            and query_params
            and query_params.procedure
            in (
                "spKDO_Aggregate",
                "spKDO_ClientList",
                "spKDO_CommAgg",
            )
        ):
            old_proc = _V2_TO_V1.get(topic)
            if old_proc:
                logger.info(
                    "v2→v1 fallback: %s → %s (topic=%s)",
                    query_params.procedure,
                    old_proc,
                    topic,
                )
                query_params.procedure = old_proc
                # Убираем v2-параметры — старые процедуры их не принимают
                query_params.group_by = ""
                query_params.filter = ""
                query_params.reason = ""

        # Do not extract report_id from free text — IDOR: users must not specify arbitrary report IDs
        report_id = question.report_id

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
            question.text,
            today=today,
            last_topic=question.last_topic,
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
            # TODO: master_name нужно разрешить в master_id через MasterResolver
            # (async-операция, требует изменения интерфейса планировщика — отдельный PR).
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
            "allclients": "all_clients",
            "all_clients": "all_clients",
        }
        return _ALIASES.get(
            raw, detect_topic(question.text, last_topic=question.last_topic)
        )

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
