from __future__ import annotations

from .base import Agent
from ..models import ModelInsight, Plan, UserQuestion
from ..services.powerbi_model_client import PowerBIModelClient


class PowerBIModelAgent(Agent):
    name = "powerbi_model"

    def __init__(self, client: PowerBIModelClient):
        self.client = client

    async def run(self, question: UserQuestion, plan: Plan) -> ModelInsight:
        if not plan.powerbi_needed:
            return ModelInsight(metrics={}, summary="Power BI model step skipped by planner")

        payload = await self.client.query_metrics(
            question=question.text,
            report_id=plan.render_report_id,
        )
        metrics = payload.get("metrics", {}) if isinstance(payload, dict) else {}
        note = payload.get("note", "") if isinstance(payload, dict) else ""
        summary = note or f"Model metrics keys: {', '.join(metrics.keys()) or 'none'}"
        return ModelInsight(metrics=metrics, summary=summary)
