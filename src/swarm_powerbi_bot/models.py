from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class UserQuestion:
    user_id: str
    text: str
    report_id: str | None = None
    object_id: int | None = None  # SalonId из подписки пользователя
    last_topic: str = ""  # Тема предыдущего вопроса (для контекста разговора)


@dataclass
class QueryParams:
    """Параметры запроса, определённые LLM-планировщиком.

    Соответствует 3 универсальным процедурам:
    - spKDO_Aggregate: group_by определяет оси (total/week/month/master/service/salon/channel)
    - spKDO_ClientList: filter определяет статус (outflow/leaving/forecast/noshow/quality/birthday/all)
    - spKDO_CommAgg: reason + group_by определяют срез коммуникаций
    """

    procedure: str = ""  # spKDO_Aggregate / spKDO_ClientList / spKDO_CommAgg
    date_from: str = ""  # ISO: 2026-03-15
    date_to: str = ""  # ISO: 2026-04-14
    object_id: int | None = None  # SalonId (из подписки)
    master_id: int | None = None
    master_name: str = ""  # имя мастера из вопроса
    top: int = 20
    group_by: str = ""  # total/week/month/master/service/salon/channel/list/status/reason/result/manager
    filter: str = (
        ""  # outflow/leaving/forecast/noshow/quality/birthday/all (для ClientList)
    )
    reason: str = ""  # all/outflow/leaving/.../waitlist/opz (для CommAgg)


@dataclass
class Plan:
    objective: str
    topic: str = "statistics"
    sql_needed: bool = True
    powerbi_needed: bool = True
    render_needed: bool = True
    render_report_id: str | None = None
    notes: list[str] = field(default_factory=list)
    query_params: QueryParams | None = None  # LLM-определённые параметры запроса


@dataclass
class SQLInsight:
    rows: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    topic: str = ""
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelInsight:
    metrics: dict[str, Any] = field(default_factory=dict)
    summary: str = ""


@dataclass
class RenderedArtifact:
    image_bytes: bytes
    mime_type: str = "image/png"
    source_url: str | None = None


@dataclass
class AnalysisResult:
    answer: str
    confidence: Literal["low", "medium", "high"] = "medium"
    follow_ups: list[str] = field(default_factory=list)
    diagnostics: dict[str, str] = field(default_factory=dict)


# --- Semantic Aggregate Layer models ---


@dataclass
class AggregateQuery:
    """Один запрос к агрегату из каталога (whitelist)."""

    aggregate_id: str
    params: dict[str, Any] = field(default_factory=dict)
    label: str = ""


@dataclass
class MultiPlan:
    """План выполнения для одного вопроса (результат одношагового LLM planning)."""

    objective: str
    intent: Literal["single", "comparison", "decomposition", "trend", "ranking"] = (
        "single"
    )
    queries: list[AggregateQuery] = field(default_factory=list)
    topic: str = "statistics"
    render_needed: bool = True
    notes: list[str] = field(default_factory=list)


@dataclass
class AggregateResult:
    """Результат одного агрегатного запроса."""

    aggregate_id: str = ""
    label: str = ""
    rows: list[dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    duration_ms: int = 0
    status: Literal["ok", "error", "timeout"] = "ok"
    error: str | None = None


@dataclass
class ComparisonResult:
    """Результат сравнения двух наборов данных."""

    period_a: str = ""
    period_b: str = ""
    results_a: AggregateResult = field(default_factory=AggregateResult)
    results_b: AggregateResult = field(default_factory=AggregateResult)
    deltas: dict[str, float] = field(default_factory=dict)


@dataclass
class SwarmResponse:
    answer: str
    image: bytes | None = None
    mime_type: str | None = None
    confidence: Literal["low", "medium", "high"] = "medium"
    topic: str = ""  # Определённая тема (для контекста следующего вопроса)
    follow_ups: list[str] = field(default_factory=list)
    diagnostics: dict[str, str] = field(default_factory=dict)
