from __future__ import annotations

import asyncio
import logging
import re
import time
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from ..config import Settings
from ..models import AggregateResult, QueryParams
from .topic_registry import detect_topic, get_procedure

if TYPE_CHECKING:
    from .aggregate_registry import AggregateRegistry

logger = logging.getLogger(__name__)

try:
    import pyodbc  # type: ignore
except Exception:  # pragma: no cover
    pyodbc = None
    logger.warning("pyodbc not available — SQL queries will be disabled")


# ── Извлечение дат из русского текста ────────────────────────

_MONTH_MAP: dict[str, int] = {
    "январ": 1,
    "феврал": 2,
    "март": 3,
    "апрел": 4,
    "мая": 5,
    "май": 5,
    "июн": 6,
    "июл": 7,
    "август": 8,
    "сентябр": 9,
    "октябр": 10,
    "ноябр": 11,
    "декабр": 12,
}

_RE_MONTH = re.compile(
    r"за\s+(январ\w*|феврал\w*|март\w*|апрел\w*|ма[йя]\w*|"
    r"июн\w*|июл\w*|август\w*|сентябр\w*|октябр\w*|ноябр\w*|декабр\w*)"
    r"(?:\s+(\d{4}))?",
    re.IGNORECASE,
)

_RE_MONTH_BARE = re.compile(
    r"\b(январ[яеюиь]?\b|феврал[яеюиь]?\b|март\b|апрел[яеюиь]?\b|ма[йя]\b|"
    r"июн[яеюиь]?\b|июл[яеюиь]?\b|август\b|сентябр[яеюиь]?\b|"
    r"октябр[яеюиь]?\b|ноябр[яеюиь]?\b|декабр[яеюиь]?\b)"
    r"(?:\s+(\d{4}))?",
    re.IGNORECASE,
)

_RE_RANGE = re.compile(
    r"с\s+(\d{1,2})\s+по\s+(\d{1,2})\s+"
    r"(январ\w*|феврал\w*|март\w*|апрел\w*|ма[йя]\w*|"
    r"июн\w*|июл\w*|август\w*|сентябр\w*|октябр\w*|ноябр\w*|декабр\w*)"
    r"(?:\s+(\d{4}))?",
    re.IGNORECASE,
)


def _match_month(text: str) -> int:
    low = text.lower()
    for stem, num in _MONTH_MAP.items():
        if low.startswith(stem):
            return num
    return 0


_PERIOD_HINTS = (
    "недел",
    "месяц",
    "месяч",
    "меся",
    "квартал",
    "год",
    "вчера",
    "сегодн",
    "полугод",
    "полгод",
)


def has_period_hint(question: str) -> bool:
    """Проверяет, указан ли в вопросе какой-либо период."""
    text = question.lower()
    if _RE_MONTH.search(text) or _RE_RANGE.search(text) or _RE_MONTH_BARE.search(text):
        return True
    return any(h in text for h in _PERIOD_HINTS)


def extract_date_params(question: str) -> dict[str, date]:
    """Извлекает @DateFrom / @DateTo из вопроса на русском."""
    today = date.today()
    text = question.lower()

    # «за январь 2025»
    m = _RE_MONTH.search(text)
    if m:
        month = _match_month(m.group(1))
        year = int(m.group(2)) if m.group(2) else today.year
        if month:
            first = date(year, month, 1)
            if month == 12:
                last = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last = date(year, month + 1, 1) - timedelta(days=1)
            return {"DateFrom": first, "DateTo": last}

    # «с 1 по 15 марта»
    m = _RE_RANGE.search(text)
    if m:
        day_from, day_to = int(m.group(1)), int(m.group(2))
        month = _match_month(m.group(3))
        year = int(m.group(4)) if m.group(4) else today.year
        if month:
            return {
                "DateFrom": date(year, month, day_from),
                "DateTo": date(year, month, day_to),
            }

    # «вчера»
    if "вчера" in text:
        yesterday = today - timedelta(days=1)
        return {"DateFrom": yesterday, "DateTo": yesterday}

    # «сегодня»
    if "сегодн" in text:
        return {"DateFrom": today, "DateTo": today}

    # «за последнюю неделю» / «за неделю»
    if "недел" in text:
        return {"DateFrom": today - timedelta(days=7), "DateTo": today}

    # «за последний месяц» / «за месяц» / «за меся»
    if "месяц" in text or "меся" in text:
        return {"DateFrom": today - timedelta(days=30), "DateTo": today}

    # «за квартал»
    if "квартал" in text:
        return {"DateFrom": today - timedelta(days=90), "DateTo": today}

    # «за полугодие»
    if "полугод" in text or "полгод" in text:
        return {"DateFrom": today - timedelta(days=180), "DateTo": today}

    # «за год»
    if "год" in text and "новый год" not in text:
        return {"DateFrom": today - timedelta(days=365), "DateTo": today}

    # По умолчанию — последние 30 дней
    return {"DateFrom": today - timedelta(days=30), "DateTo": today}


_RE_OBJECT_ID = re.compile(r"салон[а-яё]*\s*(?:id\s*)?(\d{4,})", re.IGNORECASE)
_RE_MASTER_ID = re.compile(r"мастер[а-яё]*\s*(?:id\s*)?(\d{4,})", re.IGNORECASE)


def _extract_object_id(question: str) -> int | None:
    """Извлекает ObjectId (SalonId/YClientsId) из вопроса."""
    m = _RE_OBJECT_ID.search(question)
    return int(m.group(1)) if m else None


def _extract_master_id(question: str) -> int | None:
    """Извлекает MasterId из вопроса."""
    m = _RE_MASTER_ID.search(question)
    return int(m.group(1)) if m else None


class SQLClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def execute_query(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Выполняет произвольный параметризованный SELECT-запрос.

        Используется MasterResolver для поиска мастеров.
        """
        conn_str = self.settings.sql_connection_string()
        if not conn_str or pyodbc is None:
            logger.warning("execute_query: no connection string or pyodbc unavailable")
            return []

        def _sync() -> list[dict[str, Any]]:
            conn = pyodbc.connect(conn_str, timeout=10)
            try:
                cursor = conn.cursor()
                # Извлекаем имена параметров из SQL в порядке появления
                param_names = re.findall(r"@(\w+)", sql)
                p = params or {}
                sql_args = [p[name] for name in param_names if name in p]
                query = re.sub(r"@\w+", "?", sql)
                cursor.execute(query, sql_args)
                columns = (
                    [col[0] for col in cursor.description] if cursor.description else []
                )
                rows = []
                for row in cursor.fetchall():
                    rows.append(dict(zip(columns, row)))
                return rows
            finally:
                conn.close()

        return await asyncio.to_thread(_sync)

    async def execute_aggregate(
        self,
        aggregate_id: str,
        params: dict[str, Any],
        registry: "AggregateRegistry",  # type: ignore[name-defined]
    ) -> AggregateResult:
        """T027: Выполняет агрегатный запрос по aggregate_id из каталога.

        1. Валидирует через registry.validate() — возвращает AggregateResult(status=error) если невалиден.
        2. Маппит aggregate_id на процедуру через каталог.
        3. Выполняет SQL и возвращает AggregateResult(status=ok|error|timeout).
        """
        # Валидация
        ok, msg = registry.validate(aggregate_id, params)
        if not ok:
            logger.warning(
                "execute_aggregate: validation failed for %r: %s", aggregate_id, msg
            )
            return AggregateResult(
                aggregate_id=aggregate_id,
                label=params.get("label", ""),
                status="error",
                error=f"validation failed: {msg}",
            )

        agg_entry = registry.get_aggregate(aggregate_id)
        if not agg_entry:
            return AggregateResult(
                aggregate_id=aggregate_id,
                status="error",
                error=f"aggregate_id not found in catalog: {aggregate_id!r}",
            )

        procedure = agg_entry.get("procedure", "")
        if not procedure:
            return AggregateResult(
                aggregate_id=aggregate_id,
                status="error",
                error=f"no procedure mapped for aggregate_id: {aggregate_id!r}",
            )

        start_ms = int(time.monotonic() * 1000)

        try:
            rows, _topic, _p = await asyncio.to_thread(
                self._execute_aggregate_sync, aggregate_id, procedure, params
            )
        except asyncio.TimeoutError:
            duration_ms = int(time.monotonic() * 1000) - start_ms
            return AggregateResult(
                aggregate_id=aggregate_id,
                status="timeout",
                error="SQL query timed out",
                duration_ms=duration_ms,
            )
        except Exception as exc:
            duration_ms = int(time.monotonic() * 1000) - start_ms
            logger.error("execute_aggregate error for %r: %s", aggregate_id, exc)
            return AggregateResult(
                aggregate_id=aggregate_id,
                status="error",
                error=str(exc),
                duration_ms=duration_ms,
            )

        duration_ms = int(time.monotonic() * 1000) - start_ms
        return AggregateResult(
            aggregate_id=aggregate_id,
            label=params.get("label", aggregate_id),
            rows=rows,
            row_count=len(rows),
            duration_ms=duration_ms,
            status="ok",
        )

    def _execute_aggregate_sync(
        self,
        aggregate_id: str,
        procedure: str,
        params: dict[str, Any],
        max_rows: int = 20,
    ) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
        """Синхронное выполнение агрегатного запроса.

        Делегирует в DATA_METHODS[aggregate_id] для всех каталожных агрегатов.
        Для legacy-процедур (spKDO_Attachments, spKDO_Training и т.д.) использует
        прямой SQL-вызов.
        """
        d_from_raw = params.get("date_from")
        d_to_raw = params.get("date_to")
        try:
            d_from = date.fromisoformat(d_from_raw) if d_from_raw else date.today() - timedelta(days=30)
        except (ValueError, TypeError):
            logger.warning("Invalid date_from %r for %s, using default", d_from_raw, aggregate_id)
            d_from = date.today() - timedelta(days=30)
        try:
            d_to = date.fromisoformat(d_to_raw) if d_to_raw else date.today()
        except (ValueError, TypeError):
            logger.warning("Invalid date_to %r for %s, using default", d_to_raw, aggregate_id)
            d_to = date.today()

        conn_str = self.settings.sql_connection_string()
        if not conn_str or pyodbc is None:
            logger.warning(
                "_execute_aggregate_sync: no connection string or pyodbc unavailable for %s",
                aggregate_id,
            )
            return [], aggregate_id, {"DateFrom": d_from, "DateTo": d_to}

        obj_id = params.get("object_id")
        if obj_id is None and self.settings.default_object_id:
            obj_id = self.settings.default_object_id

        group_by = params.get("group_by", "")
        if obj_id is None and group_by != "salon":
            logger.warning(
                "execute_aggregate: no ObjectId for %s — returning empty", aggregate_id
            )
            return [], aggregate_id, {"DateFrom": d_from, "DateTo": d_to}

        # Каталог использует "top", LLM может передать "top_n" — принимаем оба
        top_n = params.get("top", params.get("top_n", max_rows))
        master_id = params.get("master_id")

        # Делегируем в DATA_METHODS для всех каталожных агрегатов
        from .data_methods import DATA_METHODS  # noqa: PLC0415
        if aggregate_id in DATA_METHODS:
            try:
                df = DATA_METHODS[aggregate_id](
                    conn_str=conn_str,
                    date_from=d_from,
                    date_to=d_to,
                    object_id=obj_id,
                    master_id=master_id,
                    top=top_n,
                )
                rows = df.to_dict("records")[:max_rows]
                return rows, aggregate_id, {"DateFrom": d_from, "DateTo": d_to}
            except Exception as exc:
                logger.error("DATA_METHODS[%r] error: %s — re-raising", aggregate_id, exc)
                raise

        # Legacy-путь для процедур не в каталоге (spKDO_Attachments, spKDO_Training и др.)
        bare = procedure.replace("dbo.", "", 1) if procedure.startswith("dbo.") else procedure
        if not re.fullmatch(r"[a-zA-Z0-9_.]+", bare):
            logger.error("Invalid procedure name rejected: %r", procedure)
            return [], aggregate_id, {}
        if not procedure.startswith("dbo."):
            procedure = f"dbo.{procedure}"

        sql_parts = [f"EXEC {procedure} @DateFrom=?, @DateTo=?"]
        sql_args: list[Any] = [d_from, d_to]

        if obj_id is not None:
            sql_parts.append("@ObjectId=?")
            sql_args.append(obj_id)

        if master_id is not None:
            sql_parts.append("@MasterId=?")
            sql_args.append(master_id)

        if group_by:
            sql_parts.append("@GroupBy=?")
            sql_args.append(group_by)

        filter_val = params.get("filter", "")
        if filter_val:
            sql_parts.append("@Filter=?")
            sql_args.append(filter_val)

        reason = params.get("reason", "")
        if reason:
            sql_parts.append("@Reason=?")
            sql_args.append(reason)

        sql_parts.append("@Top=?")
        sql_args.append(top_n)

        sql = ", ".join(sql_parts) + ";"
        logger.debug("execute_aggregate SQL (legacy): %s | args: %s", sql, sql_args)

        rows: list[dict[str, Any]] = []
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cur = conn.cursor()
            cur.execute(sql, sql_args)
            cols = [desc[0] for desc in (cur.description or [])]
            for idx, row in enumerate(cur.fetchall()):
                if idx >= max_rows:
                    break
                item = {}
                for cidx, col in enumerate(cols):
                    val = row[cidx]
                    item[col] = val.isoformat() if hasattr(val, "isoformat") else val
                rows.append(item)

        return rows, aggregate_id, {"DateFrom": d_from, "DateTo": d_to}

    async def fetch_rows_with_params(
        self,
        qp: QueryParams,
        *,
        max_rows: int = 20,
    ) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
        """Выполняет запрос с LLM-определёнными параметрами."""
        return await asyncio.to_thread(
            self._fetch_with_query_params,
            qp,
            max_rows,
        )

    def _fetch_with_query_params(
        self,
        qp: QueryParams,
        max_rows: int,
    ) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
        """Вызывает процедуру с параметрами из QueryParams."""
        procedure = qp.procedure or "spKDO_Aggregate"
        # Защита от SQL injection: только alphanumeric + underscore + точка
        if not re.fullmatch(r"[a-zA-Z0-9_.]+", procedure):
            logger.error("Invalid procedure name rejected: %r", procedure)
            return [], "", {}
        # Добавляем dbo. если не указано
        if not procedure.startswith("dbo."):
            procedure = f"dbo.{procedure}"
        topic_id = procedure.replace("dbo.spKDO_", "").lower()

        # Парсим даты (LLM может вернуть невалидную строку)
        try:
            d_from = date.fromisoformat(qp.date_from) if qp.date_from else date.today() - timedelta(days=30)
        except (ValueError, TypeError):
            logger.warning("Invalid date_from %r, using default", qp.date_from)
            d_from = date.today() - timedelta(days=30)
        try:
            d_to = date.fromisoformat(qp.date_to) if qp.date_to else date.today()
        except (ValueError, TypeError):
            logger.warning("Invalid date_to %r, using default", qp.date_to)
            d_to = date.today()

        conn_str = self.settings.sql_connection_string()
        if not conn_str or pyodbc is None:
            logger.warning(
                "_fetch_with_query_params: no connection string or pyodbc unavailable for %s",
                procedure,
            )
            return [], topic_id, {"DateFrom": d_from, "DateTo": d_to}

        # ObjectId: из QueryParams, или дефолтный
        obj_id = qp.object_id
        if obj_id is None and self.settings.default_object_id:
            obj_id = self.settings.default_object_id

        # GUARD: без ObjectId большинство процедур делают full scan
        if obj_id is None:
            # salon допускает без ObjectId (cross-salon comparison)
            if qp.group_by != "salon":
                logger.warning(
                    "No ObjectId for %s — returning empty to protect DB", procedure
                )
                return [], topic_id, {"DateFrom": d_from, "DateTo": d_to}

        top = qp.top or max_rows

        params: dict[str, Any] = {
            "DateFrom": d_from,
            "DateTo": d_to,
            "Top": top,
        }

        sql_parts = [f"EXEC {procedure} @DateFrom=?, @DateTo=?"]
        sql_args: list[Any] = [d_from, d_to]

        if obj_id is not None:
            sql_parts.append("@ObjectId=?")
            sql_args.append(obj_id)
            params["ObjectId"] = obj_id

        if qp.master_id is not None:
            sql_parts.append("@MasterId=?")
            sql_args.append(qp.master_id)
            params["MasterId"] = qp.master_id

        # Параметры универсальных процедур v2
        if qp.group_by:
            sql_parts.append("@GroupBy=?")
            sql_args.append(qp.group_by)
            params["GroupBy"] = qp.group_by

        if qp.filter:
            sql_parts.append("@Filter=?")
            sql_args.append(qp.filter)
            params["Filter"] = qp.filter

        if qp.reason:
            sql_parts.append("@Reason=?")
            sql_args.append(qp.reason)
            params["Reason"] = qp.reason

        sql_parts.append("@Top=?")
        sql_args.append(top)

        sql = ", ".join(sql_parts) + ";"

        logger.debug("SQL (LLM-planned): %s | args: %s", sql, sql_args)

        rows: list[dict[str, Any]] = []
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cur = conn.cursor()
            cur.execute(sql, sql_args)
            cols = [desc[0] for desc in (cur.description or [])]
            for idx, row in enumerate(cur.fetchall()):
                if idx >= max_rows:
                    break
                item = {}
                for cidx, col in enumerate(cols):
                    val = row[cidx]
                    item[col] = val.isoformat() if hasattr(val, "isoformat") else val
                rows.append(item)

        return rows, topic_id, params

    async def fetch_rows(
        self,
        question: str,
        *,
        topic: str | None = None,
        max_rows: int = 20,
        object_id: int | None = None,
    ) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
        """Возвращает (rows, topic_id, params). Fallback путь."""
        return await asyncio.to_thread(
            self._fetch_rows_sync,
            question,
            topic,
            max_rows,
            object_id,
        )

    def _fetch_rows_sync(
        self,
        question: str,
        topic: str | None,
        max_rows: int,
        object_id: int | None,
    ) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
        topic_id = topic or detect_topic(question)
        procedure = get_procedure(topic_id)
        # Защита от SQL injection: только alphanumeric + underscore + точка
        bare = procedure.replace("dbo.", "", 1) if procedure.startswith("dbo.") else procedure
        if not re.fullmatch(r"[a-zA-Z0-9_.]+", bare):
            logger.error("Invalid procedure name rejected: %r", procedure)
            return [], topic_id, {}
        date_params = extract_date_params(question)

        conn_str = self.settings.sql_connection_string()
        if not conn_str or pyodbc is None:
            logger.warning(
                "_fetch_rows_sync: no connection string or pyodbc unavailable for %s",
                topic_id,
            )
            return [], topic_id, date_params

        # ObjectId берётся только из переданного параметра (подписка пользователя) или дефолта.
        # Парсинг из текста запроса намеренно убран — он позволял угадать чужой салон.
        obj_id = object_id
        if obj_id is None and self.settings.default_object_id:
            obj_id = self.settings.default_object_id

        # GUARD: без ObjectId — full scan на миллионы строк
        if obj_id is None:
            logger.warning(
                "No ObjectId for %s — returning empty to protect DB", procedure
            )
            return [], topic_id, date_params

        master_id = _extract_master_id(question)

        params: dict[str, Any] = {
            "DateFrom": date_params["DateFrom"],
            "DateTo": date_params["DateTo"],
            "Top": max_rows,
        }

        # Формируем SQL с полным набором параметров
        sql_parts = [f"EXEC {procedure} @DateFrom=?, @DateTo=?"]
        sql_args: list[Any] = [params["DateFrom"], params["DateTo"]]

        if obj_id is not None:
            sql_parts.append("@ObjectId=?")
            sql_args.append(obj_id)
            params["ObjectId"] = obj_id

        if master_id is not None:
            sql_parts.append("@MasterId=?")
            sql_args.append(master_id)
            params["MasterId"] = master_id

        sql_parts.append("@Top=?")
        sql_args.append(max_rows)

        sql = ", ".join(sql_parts) + ";"

        logger.debug("SQL: %s | args: %s", sql, sql_args)

        rows: list[dict[str, Any]] = []
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cur = conn.cursor()
            cur.execute(sql, sql_args)
            cols = [desc[0] for desc in (cur.description or [])]
            for idx, row in enumerate(cur.fetchall()):
                if idx >= max_rows:
                    break
                item = {}
                for cidx, col in enumerate(cols):
                    val = row[cidx]
                    item[col] = val.isoformat() if hasattr(val, "isoformat") else val
                rows.append(item)

        return rows, topic_id, params
