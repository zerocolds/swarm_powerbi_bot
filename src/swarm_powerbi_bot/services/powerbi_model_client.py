from __future__ import annotations

from typing import Any

import httpx

from ..config import Settings


class PowerBIModelClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def query_metrics(self, question: str, report_id: str | None = None) -> dict[str, Any]:
        if not self.settings.powerbi_model_query_url:
            return {
                "metrics": {},
                "note": "POWERBI_MODEL_QUERY_URL is not set; model step skipped",
            }

        headers: dict[str, str] = {}
        if self.settings.powerbi_model_query_token:
            headers["Authorization"] = f"Bearer {self.settings.powerbi_model_query_token}"

        payload = {"question": question, "report_id": report_id}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                self.settings.powerbi_model_query_url,
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            body = resp.json()

        if not isinstance(body, dict):
            return {"metrics": {}, "note": "model endpoint returned non-object payload"}

        metrics = body.get("metrics")
        if not isinstance(metrics, dict):
            metrics = {}
            body["metrics"] = metrics
        return body
