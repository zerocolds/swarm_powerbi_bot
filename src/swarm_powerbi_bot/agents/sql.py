from __future__ import annotations

from .base import Agent
from ..models import Plan, SQLInsight, UserQuestion
from ..services.sql_client import SQLClient


class SQLAgent(Agent):
    name = "sql"

    def __init__(self, client: SQLClient):
        self.client = client

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

        if not rows:
            return SQLInsight(
                rows=[],
                summary="SQL вернул 0 строк или соединение не настроено",
                topic=topic_id or plan.topic,
                params=params,
            )

        return SQLInsight(
            rows=rows,
            summary=f"SQL вернул {len(rows)} строк(и) по теме «{topic_id or plan.topic}»",
            topic=topic_id or plan.topic,
            params=params,
        )
