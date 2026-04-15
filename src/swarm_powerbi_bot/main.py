from __future__ import annotations

import logging

from .agents import AnalystAgent, PlannerAgent, PowerBIModelAgent, RenderAgent, SQLAgent
from .config import Settings
from .orchestrator import SwarmOrchestrator
from .services import LLMClient, PowerBIModelClient, PowerBIRenderClient, SQLClient
from .telegram_bot import TelegramSwarmBot


def build_orchestrator(settings: Settings) -> SwarmOrchestrator:
    llm_client = LLMClient(settings)
    planner = PlannerAgent(llm_client=llm_client)
    sql_agent = SQLAgent(SQLClient(settings))
    powerbi_agent = PowerBIModelAgent(PowerBIModelClient(settings))
    render_agent = RenderAgent(PowerBIRenderClient(settings), settings)
    analyst_agent = AnalystAgent(llm_client)

    return SwarmOrchestrator(
        planner=planner,
        sql_agent=sql_agent,
        powerbi_agent=powerbi_agent,
        render_agent=render_agent,
        analyst_agent=analyst_agent,
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    settings = Settings.from_env()
    if not settings.tg_token:
        raise RuntimeError("TG_TOKEN is required")

    orchestrator = build_orchestrator(settings)
    bot = TelegramSwarmBot(token=settings.tg_token, orchestrator=orchestrator, settings=settings)
    bot.run()


if __name__ == "__main__":
    main()
