from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from .agents import AnalystAgent, PlannerAgent, PowerBIModelAgent, RenderAgent, SQLAgent
from .models import (
    AggregateResult,
    ModelInsight,
    MultiPlan,
    SQLInsight,
    SwarmResponse,
    UserQuestion,
)
from .services.chart_renderer import render_chart

if TYPE_CHECKING:
    from .services.aggregate_registry import AggregateRegistry
    from .services.query_logger import QueryLogger

logger = logging.getLogger(__name__)


class SwarmOrchestrator:
    def __init__(
        self,
        planner: PlannerAgent,
        sql_agent: SQLAgent,
        powerbi_agent: PowerBIModelAgent,
        render_agent: RenderAgent,
        analyst_agent: AnalystAgent,
        aggregate_registry: "AggregateRegistry | None" = None,
        query_logger: "QueryLogger | None" = None,
    ):
        self.planner = planner
        self.sql_agent = sql_agent
        self.powerbi_agent = powerbi_agent
        self.render_agent = render_agent
        self.analyst_agent = analyst_agent
        self.aggregate_registry = aggregate_registry
        self.query_logger = query_logger

    async def handle_question(self, question: UserQuestion) -> SwarmResponse:
        diagnostics: dict[str, str] = {}

        # T026: Пробуем LLM-планирование с каталогом агрегатов (MultiPlan)
        multi_plan: MultiPlan | None = None
        if getattr(self.planner, "aggregate_registry", None) is not None:
            try:
                multi_plan = await self.planner.run_multi(question)
                planner_v2_mode = (
                    "llm" if "planner_v2:llm" in multi_plan.notes else "keyword"
                )
                logger.info(
                    "[PLAN_V2] %s | intent=%s | topic=%s | queries=%d",
                    planner_v2_mode,
                    multi_plan.intent,
                    multi_plan.topic,
                    len(multi_plan.queries),
                )
                diagnostics["planner_v2"] = planner_v2_mode
            except Exception as exc:
                logger.error("[PLAN_V2] ERROR: %s", exc)
                diagnostics["planner_v2_error"] = str(exc)
                multi_plan = None

        # I1: Пропускаем legacy planner.run() если multi_plan с запросами уже получен —
        # иначе два LLM-вызова на каждый вопрос (двойной cost/latency)
        if multi_plan and multi_plan.queries:
            plan = self.planner.multi_plan_to_plan(multi_plan, question)
        else:
            try:
                plan = await self.planner.run(question)
            except Exception as exc:
                logger.error("[PLAN] ERROR: %s", exc)
                diagnostics["plan_error"] = str(exc)
                plan = self.planner.empty_plan(question.text)

        # T031: Если есть MultiPlan и aggregate_registry — выполняем все запросы через SQLAgent.run_multi()
        multi_results: list[AggregateResult] = []
        if multi_plan and multi_plan.queries and self.aggregate_registry is not None:
            diagnostics["multi_plan_intent"] = multi_plan.intent
            diagnostics["multi_plan_queries"] = str(len(multi_plan.queries))
            try:
                multi_results = await self.sql_agent.run_multi(
                    multi_plan,
                    self.aggregate_registry,
                    logger_=self.query_logger,
                )
                ok_count = sum(1 for r in multi_results if r.status == "ok")
                diagnostics["multi_plan_ok"] = str(ok_count)
                logger.info(
                    "[MULTI_SQL] queries=%d ok=%d",
                    len(multi_results),
                    ok_count,
                )
            except Exception as exc:
                logger.error("[MULTI_SQL] ERROR: %s", exc)
                diagnostics["multi_sql_error"] = str(exc)
        elif multi_plan and multi_plan.queries:
            # Нет registry — логируем только первый агрегат для диагностики
            first_query = multi_plan.queries[0]
            diagnostics["multi_plan_aggregate"] = first_query.aggregate_id
            diagnostics["multi_plan_intent"] = multi_plan.intent

        # Диагностика планировщика
        planner_mode = "llm" if "planner:llm" in plan.notes else "keyword"
        qp = plan.query_params
        if qp:
            logger.info(
                "[PLAN] %s | topic=%s | proc=%s group_by=%s filter=%s reason=%s | %s..%s",
                planner_mode,
                plan.topic,
                qp.procedure,
                qp.group_by,
                qp.filter,
                qp.reason,
                qp.date_from,
                qp.date_to,
            )
        else:
            logger.info(
                "[PLAN] %s | topic=%s | no query_params", planner_mode, plan.topic
            )

        sql_task = asyncio.create_task(self._run_sql(question, plan, diagnostics))
        pbi_task = asyncio.create_task(self._run_pbi(question, plan, diagnostics))

        sql_insight, pbi_insight = await asyncio.gather(sql_task, pbi_task)

        # Генерируем график из SQL-данных (matplotlib)
        image = None
        mime_type = None
        has_chart = False

        if sql_insight.rows:
            try:
                chart_params = dict(sql_insight.params)
                chart_params["topic"] = plan.topic
                chart_bytes = await asyncio.to_thread(
                    render_chart,
                    plan.topic,
                    sql_insight.rows,
                    chart_params,
                )
                if chart_bytes:
                    image = chart_bytes
                    mime_type = "image/png"
                    has_chart = True
                    diagnostics["chart_type"] = "matplotlib"
            except Exception as exc:
                diagnostics["chart_error"] = str(exc)

        # Если matplotlib-график не получился и нужен Power BI рендер
        if image is None and plan.render_needed:
            try:
                artifact = await self.render_agent.run(question, plan)
                if artifact is not None:
                    image = artifact.image_bytes
                    mime_type = artifact.mime_type
                    if artifact.source_url:
                        diagnostics["render_source"] = artifact.source_url
            except Exception as exc:
                diagnostics["render_error"] = str(exc)

        analysis = await self.analyst_agent.run(
            question=question,
            plan=plan,
            sql_insight=sql_insight,
            model_insight=pbi_insight,
            diagnostics=diagnostics,
            has_chart=has_chart,
        )

        merged_diagnostics = dict(diagnostics)
        merged_diagnostics.update(analysis.diagnostics)

        return SwarmResponse(
            answer=analysis.answer,
            image=image,
            mime_type=mime_type,
            confidence=analysis.confidence,
            topic=plan.topic,
            follow_ups=analysis.follow_ups,
            diagnostics=merged_diagnostics,
        )

    async def _run_sql(self, question, plan, diagnostics: dict[str, str]) -> SQLInsight:
        try:
            result = await self.sql_agent.run(question, plan)
            logger.info("[SQL] topic=%s rows=%d", plan.topic, len(result.rows))
            return result
        except Exception as exc:
            logger.error("[SQL] ERROR: %s", exc)
            diagnostics["sql_error"] = str(exc)
            return SQLInsight(rows=[], summary="SQL step failed")

    async def _run_pbi(
        self, question, plan, diagnostics: dict[str, str]
    ) -> ModelInsight:
        try:
            return await self.powerbi_agent.run(question, plan)
        except Exception as exc:
            diagnostics["powerbi_model_error"] = str(exc)
            return ModelInsight(metrics={}, summary="Power BI model step failed")
