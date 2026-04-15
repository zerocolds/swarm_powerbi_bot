from __future__ import annotations

from .base import Agent
from ..config import Settings
from ..models import Plan, RenderedArtifact, UserQuestion
from ..services.powerbi_render_client import PowerBIRenderClient


class RenderAgent(Agent):
    name = "render"

    def __init__(self, client: PowerBIRenderClient, settings: Settings):
        self.client = client
        self.settings = settings

    async def run(self, question: UserQuestion, plan: Plan) -> RenderedArtifact | None:
        if not plan.render_needed:
            return None

        report_url = self.settings.report_url(plan.render_report_id or question.report_id)
        if not report_url:
            return None

        png = await self.client.render_report(
            report_url=report_url,
            target_xpath=self.settings.render_target_xpath,
        )
        return RenderedArtifact(image_bytes=png, source_url=report_url)
