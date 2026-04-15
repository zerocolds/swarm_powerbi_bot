from __future__ import annotations

import asyncio
import logging

from typing import TYPE_CHECKING

from .base import Agent
from ..config import Settings
from ..models import AggregateQuery, AggregateResult, MultiPlan, Plan, SQLInsight, UserQuestion
from ..services.sql_client import SQLClient

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..services.aggregate_registry import AggregateRegistry
    from ..services.query_logger import QueryLogger


class SQLAgent(Agent):
    name = "sql"

    def __init__(self, client: SQLClient, settings: Settings | None = None):
        self.client = client
        self.settings = settings

    async def run(self, question: UserQuestion, plan: Plan) -> SQLInsight:
        if not plan.sql_needed:
            return SQLInsight(rows=[], summary="SQL step skipped by planner")

        # Если есть LLM-параметры — используем их напрямую
        if plan.query_params and plan.query_params.procedure:
            rows, topic_id, params = await self.client.fetch_rows_with_params(
                plan.query_params,
            )
        else:
            # Fallback: старый путь через keyword-детекцию
            rows, topic_id, params = await self.client.fetch_rows(
                question.text, topic=plan.topic, object_id=question.object_id,
            )

        effective_topic = topic_id or plan.topic
        status = "ok" if rows else "empty"
        logger.info(
            "sql.run user=%s topic=%s rows=%d status=%s",
            question.user_id,
            effective_topic,
            len(rows),
            status,
        )

        if not rows:
            return SQLInsight(
                rows=[],
                summary="SQL вернул 0 строк или соединение не настроено",
                topic=effective_topic,
                params=params,
            )

        return SQLInsight(
            rows=rows,
            summary=f"SQL вернул {len(rows)} строк(и) по теме «{effective_topic}»",
            topic=effective_topic,
            params=params,
        )

    async def run_multi(
        self,
        plan: MultiPlan,
        registry: "AggregateRegistry",
        sql_client: SQLClient | None = None,
        logger_: "QueryLogger | None" = None,
        user_id: str = "system",
    ) -> list[AggregateResult]:
        """T029/T032: Выполняет несколько агрегатных запросов параллельно.

        - Ограничивает количество запросов до settings.sql_max_queries
        - Использует asyncio.Semaphore(settings.sql_max_concurrency) для ограничения параллельности
        - При timeout/error возвращает AggregateResult с соответствующим статусом
        - Логирует каждый вызов через QueryLogger если передан
        """
        client = sql_client or self.client

        # Определяем лимиты из settings или используем дефолты
        max_queries = 10
        max_concurrency = 5
        query_timeout = 10
        if self.settings is not None:
            max_queries = self.settings.sql_max_queries
            max_concurrency = self.settings.sql_max_concurrency
            query_timeout = self.settings.sql_query_timeout

        queries = plan.queries[:max_queries]
        semaphore = asyncio.Semaphore(max_concurrency)

        async def _run_one(query: AggregateQuery) -> AggregateResult:
            async with semaphore:
                try:
                    result = await asyncio.wait_for(
                        client.execute_aggregate(query.aggregate_id, query.params, registry),
                        timeout=query_timeout,
                    )
                    # Подставляем label из запроса (приоритет над label из результата)
                    effective_label = query.label or result.label
                    if effective_label != result.label:
                        result = AggregateResult(
                            aggregate_id=result.aggregate_id,
                            label=effective_label,
                            rows=result.rows,
                            row_count=result.row_count,
                            duration_ms=result.duration_ms,
                            status=result.status,
                            error=result.error,
                        )
                except asyncio.TimeoutError:
                    result = AggregateResult(
                        aggregate_id=query.aggregate_id,
                        label=query.label,
                        status="timeout",
                        error="SQL query timed out",
                    )
                except Exception as exc:
                    logger.error("run_multi error for %r: %s", query.aggregate_id, exc)
                    result = AggregateResult(
                        aggregate_id=query.aggregate_id,
                        label=query.label,
                        status="error",
                        error=str(exc),
                    )

                # T032: логируем каждый вызов
                if logger_ is not None:
                    try:
                        logger_.log(
                            user_id=user_id,
                            aggregate_id=result.aggregate_id,
                            params=query.params,
                            duration_ms=result.duration_ms,
                            row_count=result.row_count,
                            status=result.status,
                            error=result.error,
                        )
                    except Exception as log_exc:
                        logger.warning("QueryLogger.log failed: %s", log_exc)

                return result

        return list(await asyncio.gather(*[_run_one(q) for q in queries]))
