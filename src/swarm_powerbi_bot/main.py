from __future__ import annotations

import logging
import os

from .agents import AnalystAgent, PlannerAgent, PowerBIModelAgent, RenderAgent, SQLAgent
from .config import Settings
from .orchestrator import SwarmOrchestrator
from .services import LLMClient, PowerBIModelClient, PowerBIRenderClient, SQLClient
from .services.aggregate_registry import AggregateRegistry
from .services.query_logger import QueryLogger
from .telegram_bot import TelegramSwarmBot

logger = logging.getLogger(__name__)


def build_orchestrator(settings: Settings) -> SwarmOrchestrator:
    llm_client = LLMClient(settings)

    # Семантический слой агрегатов: загружаем каталог если файл существует
    aggregate_registry: AggregateRegistry | None = None
    query_logger: QueryLogger | None = None
    catalog_path = settings.aggregate_catalog_path
    if catalog_path and os.path.exists(catalog_path):
        try:
            aggregate_registry = AggregateRegistry(catalog_path)
            query_logger = QueryLogger()
            logger.info("AggregateRegistry loaded from %s", catalog_path)
        except Exception as exc:
            logger.error("Failed to load AggregateRegistry from %s: %s", catalog_path, exc)

    planner = PlannerAgent(llm_client=llm_client, aggregate_registry=aggregate_registry)
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
        aggregate_registry=aggregate_registry,
        query_logger=query_logger,
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
