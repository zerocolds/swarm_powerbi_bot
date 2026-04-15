from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger(__name__)


def _as_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning("Invalid integer for %s=%r, using default %d", name, raw, default)
        return default


def _as_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "y"}


def _in_docker() -> bool:
    return os.path.exists("/.dockerenv") or os.getenv("IN_DOCKER") == "1"


def _maybe_load_dotenv() -> None:
    """
    Локально по умолчанию загружаем .env.
    В Docker по умолчанию не загружаем .env.
    Переменные окружения имеют приоритет над .env (override=False).

    Дополнительно пытаемся использовать ../.env, чтобы новый проект мог
    брать секреты из основного проекта без копирования.
    """
    use_dotenv = os.getenv("USE_DOTENV")
    if use_dotenv is None:
        use_dotenv = "0" if _in_docker() else "1"

    if use_dotenv.strip().lower() not in {"1", "true", "yes", "on"}:
        return

    try:
        from dotenv import find_dotenv, load_dotenv  # type: ignore
    except Exception:
        return

    candidates: list[str] = []

    env_file = os.getenv("ENV_FILE", "").strip()
    if env_file:
        candidates.append(env_file)

    found = find_dotenv(".env", usecwd=True)
    if found:
        candidates.append(found)

    parent_env = Path.cwd().parent / ".env"
    if parent_env.exists():
        candidates.append(str(parent_env))

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            load_dotenv(candidate, override=False)
            break


def _build_report_base_from_legacy_env() -> str:
    host = os.getenv("PBI_HOST", "").strip()
    if not host:
        return ""

    user = os.getenv("PBI_USER", "").strip()
    password = os.getenv("PBI_PASS", "").strip()

    userinfo = quote(user, safe="") if user else ""
    if userinfo and password:
        userinfo = f"{userinfo}:{quote(password, safe='')}"

    if userinfo:
        return f"http://{userinfo}@{host}/powerbi/?id="
    return f"http://{host}/powerbi/?id="


@dataclass(frozen=True)
class Settings:
    tg_token: str = ""
    timezone: str = "Europe/Moscow"

    report_base_url: str = ""
    default_report_id: str = "sales/kpi"
    selenium_hub_url: str = ""
    render_wait_seconds: int = 8
    render_target_xpath: str = ""
    chromedriver_path: str = "/usr/bin/chromedriver"

    mssql_dsn: str = field(default="", repr=False)
    mssql_server: str = ""
    mssql_port: str = "1433"
    mssql_db: str = ""
    mssql_user: str = ""
    mssql_pwd: str = field(default="", repr=False)
    mssql_driver: str = "ODBC Driver 17 for SQL Server"

    powerbi_model_query_url: str = ""
    powerbi_model_query_token: str = field(default="", repr=False)

    ollama_api_key: str = field(default="", repr=False)
    ollama_model: str = "glm-5:cloud"
    ollama_base_url: str = "https://ollama.com/api"

    whisper_base_url: str = "https://ollama.com/api"
    whisper_model: str = "whisper-large:cloud"

    # ObjectId по умолчанию (SalonId/YClientsId) — обязателен для процедур со статусами клиентов
    default_object_id: int = 0

    debug: bool = False

    # Пути к каталогам семантического слоя
    catalog_dir: str = "catalogs"
    semantic_catalog_path: str = "catalogs/semantic-catalog.yaml"
    aggregate_catalog_path: str = "catalogs/aggregate-catalog.yaml"

    # LLM planning
    llm_plan_timeout: int = 5  # секунд на LLM-вызов
    llm_circuit_breaker_threshold: int = 3  # consecutive timeouts → fallback
    llm_circuit_breaker_cooldown: int = 60  # секунд fallback на TopicRegistry

    # SQL multi-query
    sql_query_timeout: int = 10  # секунд на один агрегатный запрос
    sql_max_queries: int = 10  # максимум запросов за один вопрос
    sql_max_concurrency: int = 5  # asyncio.Semaphore

    @classmethod
    def from_env(cls) -> "Settings":
        _maybe_load_dotenv()
        report_base_url = os.getenv("REPORT_BASE_URL", "").strip()
        if not report_base_url:
            report_base_url = _build_report_base_from_legacy_env()

        return cls(
            tg_token=os.getenv("TG_TOKEN", "").strip(),
            timezone=os.getenv("TZ", "Europe/Moscow").strip(),
            report_base_url=report_base_url,
            default_report_id=os.getenv("DEFAULT_REPORT_ID", "sales/kpi").strip(),
            selenium_hub_url=os.getenv("SELENIUM_HUB_URL", "").strip(),
            render_wait_seconds=_as_int("RENDER_WAIT_SECONDS", 8),
            render_target_xpath=os.getenv("RENDER_TARGET_XPATH", "").strip(),
            chromedriver_path=os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver").strip(),
            mssql_dsn=os.getenv("MSSQL_DSN", "").strip(),
            mssql_server=os.getenv("MSSQL_SERVER", "").strip(),
            mssql_port=os.getenv("MSSQL_PORT", "1433").strip(),
            mssql_db=os.getenv("MSSQL_DB", "").strip(),
            mssql_user=os.getenv("MSSQL_USER", "").strip(),
            mssql_pwd=os.getenv("MSSQL_PWD", "").strip(),
            mssql_driver=os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server").strip(),
            powerbi_model_query_url=os.getenv("POWERBI_MODEL_QUERY_URL", "").strip(),
            powerbi_model_query_token=os.getenv("POWERBI_MODEL_QUERY_TOKEN", "").strip(),
            ollama_api_key=os.getenv("OLLAMA_API_KEY", "").strip(),
            ollama_model=os.getenv("OLLAMA_MODEL", "glm-5:cloud").strip(),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "https://ollama.com/api").strip(),
            whisper_base_url=os.getenv("WHISPER_BASE_URL", os.getenv("OLLAMA_BASE_URL", "https://ollama.com/api")).strip(),
            whisper_model=os.getenv("WHISPER_MODEL", "whisper-large:cloud").strip(),
            default_object_id=_as_int("DEFAULT_OBJECT_ID", 0),
            debug=_as_bool("DEBUG", False),
            catalog_dir=os.getenv("CATALOG_DIR", "catalogs").strip(),
            semantic_catalog_path=os.getenv("SEMANTIC_CATALOG_PATH", "catalogs/semantic-catalog.yaml").strip(),
            aggregate_catalog_path=os.getenv("AGGREGATE_CATALOG_PATH", "catalogs/aggregate-catalog.yaml").strip(),
            llm_plan_timeout=_as_int("LLM_PLAN_TIMEOUT", 5),
            llm_circuit_breaker_threshold=_as_int("LLM_CIRCUIT_BREAKER_THRESHOLD", 3),
            llm_circuit_breaker_cooldown=_as_int("LLM_CIRCUIT_BREAKER_COOLDOWN", 60),
            sql_query_timeout=_as_int("SQL_QUERY_TIMEOUT", 10),
            sql_max_queries=_as_int("SQL_MAX_QUERIES", 10),
            sql_max_concurrency=_as_int("SQL_MAX_CONCURRENCY", 5),
        )

    def sql_connection_string(self) -> str:
        if self.mssql_dsn:
            return self.mssql_dsn

        if not (self.mssql_server and self.mssql_db and self.mssql_user):
            return ""

        driver = self.mssql_driver.replace("{", "").replace("}", "")
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={self.mssql_server},{self.mssql_port};"
            f"DATABASE={self.mssql_db};"
            f"UID={self.mssql_user};"
            f"PWD={self.mssql_pwd};"
            "TrustServerCertificate=yes;Encrypt=no;"
        )

    def report_url(self, report_id: str | None) -> str:
        report = (report_id or self.default_report_id).strip()
        if not self.report_base_url:
            return report

        base = self.report_base_url
        if not base.endswith("="):
            if not base.endswith("/"):
                base = f"{base}/"
            return f"{base}{quote(report, safe='/')}"
        return f"{base}{quote(report, safe='/')}"
