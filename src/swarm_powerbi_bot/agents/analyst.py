from __future__ import annotations

import json

from .base import Agent
from ..models import AnalysisResult, ModelInsight, Plan, SQLInsight, UserQuestion
from ..services.llm_client import LLMClient
from ..services.topic_registry import get_description

# ── Подсказки для описания графиков ──────────────────────────

_CHART_HINTS: dict[str, str] = {
    "statistics": "На графике показаны ключевые KPI: визиты, клиенты, выручка, средний чек.",
    "trend": "На графике показана динамика по неделям: визиты, клиенты и выручка.",
    "outflow": "На графике показаны клиенты в оттоке — отсортированы по просроченности.",
    "leaving": "На графике показаны уходящие клиенты — просрочка 1-30 дней.",
    "forecast": "На графике показаны клиенты, которых ожидаем в ближайшие 14 дней.",
    "communications": "На графике показана сводка коммуникаций по типам и результатам.",
    "referrals": "На диаграмме показано распределение клиентов по каналам привлечения.",
    "masters": "На графике показаны мастера по выручке/загрузке.",
    "services": "На графике показаны услуги по выручке.",
    "quality": "На графике показаны клиенты на контроле качества.",
    "noshow": "На графике показаны недошедшие клиенты.",
    "opz": "На графике показаны оперативные записи.",
    "training": "На графике показано выполнение плана по обучению мастеров.",
    "attachments": "На графике показаны абонементы по статусам.",
    "all_clients": "На графике показана клиентская база.",
}

# Тематические follow-up подсказки
_TOPIC_FOLLOW_UPS: dict[str, list[str]] = {
    "all_clients": [
        "Хотите посмотреть клиентов по конкретному салону?",
        "Показать динамику клиентской базы по месяцам?",
    ],
    "outflow": [
        "Хотите сравнить отток по салонам?",
        "Показать причины оттока за другой период?",
    ],
    "leaving": [
        "Показать уходящих по конкретному мастеру?",
        "Хотите увидеть историю визитов этих клиентов?",
    ],
    "statistics": [
        "Хотите детализацию по конкретному показателю?",
        "Сравнить KPI за разные периоды?",
    ],
    "trend": [
        "Показать тренд по другому показателю?",
        "Хотите прогноз на основе текущего тренда?",
    ],
    "forecast": [
        "Хотите прогноз по конкретному мастеру?",
        "Показать загрузку по салонам?",
    ],
    "communications": [
        "Хотите посмотреть результативность обзвонов?",
        "Показать коммуникации по конкретному менеджеру?",
    ],
    "referrals": [
        "Показать рефережи по салонам?",
        "Хотите увидеть конверсию рефералов в постоянных клиентов?",
    ],
    "quality": [
        "Показать оценки по конкретному мастеру?",
        "Хотите увидеть динамику качества за период?",
    ],
    "attachments": [
        "Показать абонементы с истекающим сроком?",
        "Хотите увидеть статистику продлений?",
    ],
    "birthday": [
        "Показать именинников на следующую неделю?",
        "Хотите увидеть кого ещё не поздравили?",
    ],
    "waitlist": [
        "Показать лист ожидания по услугам?",
        "Хотите увидеть среднее время ожидания?",
    ],
    "training": [
        "Показать кто ещё не прошёл обучение?",
        "Хотите статистику по завершённости курсов?",
    ],
    "masters": [
        "Сравнить мастеров по загрузке?",
        "Показать выручку по мастерам за период?",
    ],
    "services": [
        "Показать топ-5 популярных услуг?",
        "Хотите динамику среднего чека по месяцам?",
    ],
    "noshow": [
        "Показать недошедших за другой период?",
        "Хотите увидеть результаты обзвона недошедших?",
    ],
    "opz": [
        "Показать ОПЗ по конкретному менеджеру?",
        "Хотите статистику конверсии ОПЗ?",
    ],
}

_DEFAULT_FOLLOW_UPS = [
    "Уточните период анализа (неделя/месяц/квартал)",
    "Уточните разрез: салон, мастер, категория",
]


class AnalystAgent(Agent):
    name = "analyst"

    SYSTEM_PROMPT = (
        "Ты — дашборд салона красоты (КДО). Озвучиваешь данные из SQL текстом.\n\n"
        "СЛОВАРЬ ПОЛЕЙ (используй эти названия при описании):\n"
        "• ClientName — имя клиента\n"
        "• TotalSpent — сумма трат этого клиента за всю историю (₽)\n"
        "• TotalVisits — количество визитов этого клиента\n"
        "• DaysSinceLastVisit — дней с последнего визита\n"
        "• DaysOverdue — дней просрочки (на сколько опоздал от ожидаемого визита)\n"
        "• ServicePeriodDays — средний период между визитами клиента (дни)\n"
        "• LastVisit — дата последнего визита\n"
        "• ExpectedNextVisit — ожидаемая дата следующего визита\n"
        "• Category — категория клиента в CRM\n"
        "• ClientStatus — статус клиента (отток/уходящий/прогноз и т.д.)\n"
        "• SalonName — название салона\n"
        "• Revenue / AvgCheck — выручка / средний чек\n\n"
        "ПРАВИЛА (нарушение = брак):\n"
        "1. Описывай ТОЛЬКО данные из sql_rows. Ни слова от себя.\n"
        "2. ЗАПРЕЩЕНО: рекомендации, оценки, прогнозы, "
        "слова «срочно/критично/тревожно/VIP/топ/рекомендую/необходимо».\n"
        "3. ЗАПРЕЩЕНО: таблицы (| --- |). Только текст и • списки.\n"
        "4. ЗАПРЕЩЕНО: выдумывать ранги, категории, причины.\n"
        "5. Формат: МАКСИМУМ 4 предложения. Тема, период, кол-во записей, "
        "главные цифры. Если график — одно предложение что на осях. "
        "Это чат в Telegram — стена текста = плохо.\n"
        "6. Числа относятся к КОНКРЕТНОМУ клиенту, не ко всем сразу. "
        "TotalSpent=8000 значит «этот клиент потратил 8000₽», "
        "а НЕ «общая сумма 8000₽».\n\n"
        "Пример:\n"
        "«Отток за 30 дней: 20 клиентов. Просрочка от 31 до 240 дней. "
        "Клиент с наибольшей историей трат — 57 000 ₽ за 59 визитов. "
        "На графике — клиенты по убыванию просрочки.»"
    )

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def run(
        self,
        question: UserQuestion,
        plan: Plan,
        sql_insight: SQLInsight,
        model_insight: ModelInsight,
        diagnostics: dict[str, str],
        *,
        has_chart: bool = False,
    ) -> AnalysisResult:
        fallback = self._fallback_summary(
            question, plan, sql_insight, model_insight, diagnostics, has_chart=has_chart,
        )

        user_prompt = self._compose_prompt(
            question, plan, sql_insight, model_insight, diagnostics, has_chart=has_chart,
        )
        answer = await self.llm_client.synthesize(self.SYSTEM_PROMPT, user_prompt, fallback)

        confidence = "low"
        if sql_insight.rows and model_insight.metrics:
            confidence = "high"
        elif sql_insight.rows or model_insight.metrics:
            confidence = "medium"

        follow_ups = _TOPIC_FOLLOW_UPS.get(plan.topic, _DEFAULT_FOLLOW_UPS)

        return AnalysisResult(
            answer=answer,
            confidence=confidence,
            follow_ups=follow_ups,
            diagnostics=diagnostics,
        )

    def _compose_prompt(
        self,
        question: UserQuestion,
        plan: Plan,
        sql_insight: SQLInsight,
        model_insight: ModelInsight,
        diagnostics: dict[str, str],
        *,
        has_chart: bool = False,
    ) -> str:
        topic_desc = get_description(plan.topic)
        data: dict = {
            "question": question.text,
            "topic": plan.topic,
            "topic_description": topic_desc,
            "sql_summary": sql_insight.summary,
            "row_count": len(sql_insight.rows),
            "sql_rows": sql_insight.rows[:10],
            "sql_params": {k: str(v) for k, v in sql_insight.params.items()},
            "model_summary": model_insight.summary,
            "model_metrics": model_insight.metrics,
        }
        if has_chart:
            chart_hint = _CHART_HINTS.get(plan.topic, "К ответу прикреплён график.")
            data["chart_attached"] = True
            data["chart_description_hint"] = chart_hint
        return json.dumps(data, ensure_ascii=False)

    def _fallback_summary(
        self,
        question: UserQuestion,
        plan: Plan,
        sql_insight: SQLInsight,
        model_insight: ModelInsight,
        diagnostics: dict[str, str],
        *,
        has_chart: bool = False,
    ) -> str:
        topic_desc = get_description(plan.topic)
        lines = []

        if topic_desc:
            lines.append(f"*{topic_desc}*")
            lines.append("")

        if sql_insight.rows:
            lines.append(f"Найдено записей: {len(sql_insight.rows)}")
            # Показываем ключевые поля первой строки человеко-читаемо
            row = sql_insight.rows[0]
            preview_fields = []
            for key, val in row.items():
                if key in ("SalonName",) or val is None:
                    continue
                preview_fields.append(f"• {key}: {val}")
                if len(preview_fields) >= 5:
                    break
            if preview_fields:
                lines.append("")
                lines.append("*Пример:*")
                lines.extend(preview_fields)
        else:
            lines.append("Данных за указанный период не найдено.")

        if has_chart:
            chart_hint = _CHART_HINTS.get(plan.topic, "")
            if chart_hint:
                lines.append("")
                lines.append(chart_hint)

        follow_ups = _TOPIC_FOLLOW_UPS.get(plan.topic, _DEFAULT_FOLLOW_UPS)
        if follow_ups:
            lines.append("")
            lines.append("_Попробуйте уточнить период или фильтры._")

        return "\n".join(lines)
