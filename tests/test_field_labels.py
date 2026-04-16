"""Тесты: маппинг полей и поведение _fallback_summary для услуг и мастеров (US2)."""

import pytest

from swarm_powerbi_bot.agents.analyst import _FIELD_LABELS, _HIDDEN_FIELDS, AnalystAgent


# ---------------------------------------------------------------------------
# T007: все поля services-темы переведены или скрыты
# ---------------------------------------------------------------------------

SERVICES_FIELDS = [
    "ServiceCategory",
    "ServiceCount",
]


@pytest.mark.parametrize("field", SERVICES_FIELDS)
def test_services_fields_translated_or_hidden(field: str) -> None:
    """Каждое поле services-темы должно быть в _FIELD_LABELS или в _HIDDEN_FIELDS."""
    assert field in _FIELD_LABELS or field in _HIDDEN_FIELDS, (
        f"Поле '{field}' не переведено и не скрыто — добавьте в _FIELD_LABELS или _HIDDEN_FIELDS"
    )


# ---------------------------------------------------------------------------
# T008: все поля masters-темы переведены или скрыты
# ---------------------------------------------------------------------------

MASTERS_FIELDS = [
    "MasterCategory",
    "Rating",
    "ReturningClients",
    "TotalHours",
    "EndOfWeek",
    "WeekLabel",
]


@pytest.mark.parametrize("field", MASTERS_FIELDS)
def test_masters_fields_translated_or_hidden(field: str) -> None:
    """Каждое поле masters-темы должно быть в _FIELD_LABELS или в _HIDDEN_FIELDS."""
    assert field in _FIELD_LABELS or field in _HIDDEN_FIELDS, (
        f"Поле '{field}' не переведено и не скрыто — добавьте в _FIELD_LABELS или _HIDDEN_FIELDS"
    )


# ---------------------------------------------------------------------------
# T009: неизвестное поле пропускается в fallback summary (не показывается raw name)
# ---------------------------------------------------------------------------

class _FakeLLM:
    """Заглушка LLM-клиента — возвращает fallback без обращения к сети."""
    async def synthesize(self, system: str, user: str, fallback: str) -> str:
        return fallback


def _make_sql_insight(rows):
    from swarm_powerbi_bot.models import SQLInsight
    return SQLInsight(rows=rows, summary="test", params={})


def _make_model_insight():
    from swarm_powerbi_bot.models import ModelInsight
    return ModelInsight(summary="", metrics={})


def _make_plan(topic: str):
    from swarm_powerbi_bot.models import Plan
    return Plan(objective="тест", topic=topic)


def _make_question(text: str = "тест"):
    from swarm_powerbi_bot.models import UserQuestion
    return UserQuestion(user_id="0", text=text)


def test_unknown_field_skipped_in_fallback_summary() -> None:
    """Поле без маппинга в _FIELD_LABELS не должно отображаться raw именем."""
    agent = AnalystAgent(_FakeLLM())  # type: ignore[arg-type]

    unknown_field = "UnknownRawField_XYZ"
    assert unknown_field not in _FIELD_LABELS, "Тест-поле случайно оказалось в маппинге"
    assert unknown_field not in _HIDDEN_FIELDS, "Тест-поле случайно попало в hidden"

    rows = [
        {
            "ClientName": "Иван Иванов",
            unknown_field: "raw_value_should_not_appear",
        }
    ]

    sql_insight = _make_sql_insight(rows)
    model_insight = _make_model_insight()
    plan = _make_plan("services")
    question = _make_question()

    summary = agent._fallback_summary(question, plan, sql_insight, model_insight, {})

    assert unknown_field not in summary, (
        f"Raw-имя поля '{unknown_field}' не должно появляться в fallback summary"
    )
    assert "raw_value_should_not_appear" not in summary, (
        "Значение поля без маппинга не должно появляться в fallback summary"
    )
    # Известное поле должно переводиться
    assert "Клиент" in summary, "Известное поле ClientName должно быть переведено"
