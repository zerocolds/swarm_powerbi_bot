from __future__ import annotations

import json
from datetime import date
from typing import Literal

from .base import Agent
from ..models import AggregateResult, AnalysisResult, ComparisonResult, ModelInsight, MultiPlan, Plan, SQLInsight, UserQuestion
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

# Русские названия метрик (колонки SQL → Telegram)
_METRIC_LABELS: dict[str, str] = {
    "ClientCount": "Клиенты",
    "TotalVisits": "Визиты",
    "TotalSpent": "Сумма трат (₽)",
    "Revenue": "Выручка (₽)",
    "TotalRevenue": "Выручка (₽)",
    "AvgCheck": "Средний чек (₽)",
    "UniqueClients": "Уникальные клиенты",
    "Visits": "Визиты",
    "ActiveMasters": "Активные мастера",
    "TotalHours": "Часов работы",
    "BookedCount": "Записались",
    "RefusedCount": "Отказались",
    "TotalCount": "Всего коммуникаций",
    "ReturningClients": "Вернувшиеся клиенты",
    "RevenuePerHour": "Выручка в час (₽)",
    "ServiceCount": "Количество услуг",
}

# Русские названия полей для fallback_summary
_FIELD_LABELS: dict[str, str] = {
    "ClientName": "Клиент",
    "DaysSinceLastVisit": "Дней с последнего визита",
    "DaysOverdue": "Дней просрочки",
    "TotalSpent": "Сумма трат (₽)",
    "TotalVisits": "Визитов",
    "LastVisit": "Последний визит",
    "ExpectedNextVisit": "Ожидаемый визит",
    "ServicePeriodDays": "Период визитов (дни)",
    "Revenue": "Выручка (₽)",
    "TotalRevenue": "Выручка (₽)",
    "AvgCheck": "Средний чек (₽)",
    "Visits": "Визиты",
    "UniqueClients": "Уникальные клиенты",
    "ActiveMasters": "Активные мастера",
    "ClientStatus": "Статус",
    "Category": "Категория",
    "MasterName": "Мастер",
    "ServiceName": "Услуга",
    "Reason": "Причина",
    "Result": "Результат",
    "Manager": "Менеджер",
}

# Поля, которые не показываем в fallback (технические, приватные)
_HIDDEN_FIELDS = {
    "Phone", "CRMId", "ObjectId", "MasterId", "ClientId", "Id", "Top",
    "SalonName", "FirstVisit", "LastCommResult", "ServicePeriodDays",
}


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

        # Период из SQL-параметров
        date_from = sql_insight.params.get("DateFrom") or sql_insight.params.get("date_from")
        date_to = sql_insight.params.get("DateTo") or sql_insight.params.get("date_to")
        if date_from and date_to:
            df = date_from.isoformat() if isinstance(date_from, date) else str(date_from)[:10]
            dt = date_to.isoformat() if isinstance(date_to, date) else str(date_to)[:10]
            lines.append(f"Период: {df} — {dt}")

        if lines:
            lines.append("")

        if sql_insight.rows:
            # Topic-specific форматтеры
            topic = plan.topic
            if topic in ("outflow", "leaving", "noshow"):
                lines.append(self._format_client_list_summary(sql_insight.rows, topic))
            elif topic in ("statistics",):
                lines.append(self._format_statistics_summary(sql_insight.rows))
            else:
                lines.append(f"Найдено записей: {len(sql_insight.rows)}")
                # Переведённые поля первой строки
                row = sql_insight.rows[0]
                preview = []
                for key, val in row.items():
                    if key in _HIDDEN_FIELDS or val is None:
                        continue
                    label = _FIELD_LABELS.get(key, key)
                    if isinstance(val, float):
                        val = f"{val:,.2f}"
                    elif isinstance(val, str) and "T" in val and len(val) > 10:
                        val = val[:10]  # ISO datetime → дата
                    preview.append(f"• {label}: {val}")
                    if len(preview) >= 5:
                        break
                if preview:
                    lines.append("")
                    lines.extend(preview)
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

    @staticmethod
    def _format_client_list_summary(rows: list[dict], topic: str) -> str:
        """Агрегированная статистика для outflow/leaving/noshow."""
        count = len(rows)
        overdue_key = "DaysOverdue" if "DaysOverdue" in (rows[0] if rows else {}) else "DaysSinceLastVisit"
        overdue_vals = [abs(r.get(overdue_key, 0) or 0) for r in rows]
        spent_vals = [r.get("TotalSpent", 0) or 0 for r in rows]

        parts = [f"Найдено клиентов: {count}"]
        if overdue_vals and any(overdue_vals):
            parts.append(f"Просрочка — от {min(overdue_vals)} до {max(overdue_vals)} дней")

        if spent_vals and any(spent_vals):
            top = max(rows, key=lambda r: r.get("TotalSpent", 0) or 0)
            top_name = top.get("ClientName", "?")
            top_spent = top.get("TotalSpent", 0) or 0
            top_visits = top.get("TotalVisits", 0) or 0
            parts.append(
                f"Наибольшая сумма трат у клиента {top_name} — "
                f"{top_spent:,.0f} ₽ за {top_visits} визитов"
            )
        return ".\n".join(parts) + "."

    @staticmethod
    def _format_statistics_summary(rows: list[dict]) -> str:
        """Форматирует statistics (одна строка с KPI)."""
        if not rows:
            return "Данных не найдено."
        row = rows[0]
        _MONEY_FIELDS = {"Revenue", "TotalRevenue", "AvgCheck", "RevenuePerHour"}
        parts = []
        for key in ("Visits", "UniqueClients", "TotalRevenue", "Revenue", "AvgCheck", "ActiveMasters"):
            val = row.get(key)
            if val is None:
                continue
            label = _METRIC_LABELS.get(key, key)
            if key in _MONEY_FIELDS and isinstance(val, (int, float)):
                parts.append(f"{label}: {val:,.2f}")
            elif isinstance(val, float):
                parts.append(f"{label}: {val:,.0f}")
            else:
                parts.append(f"{label}: {val}")
        return " | ".join(parts) if parts else f"Найдено записей: {len(rows)}"

    async def run_multi(
        self,
        question: str,
        results: list[AggregateResult],
        plan: MultiPlan,
    ) -> AnalysisResult:
        """T030/T039: Синтезирует результаты нескольких агрегатных запросов в один ответ.

        - Пропускает результаты со статусом != "ok"
        - Использует label из AggregateResult для контекста
        - При intent="decomposition": сравнивает метрики по периодам и выявляет главный фактор
        - Возвращает AnalysisResult с ответом на вопрос
        """
        ok_results = [r for r in results if r.status == "ok"]
        skipped = len(results) - len(ok_results)

        # T039: специальная ветка для факторного анализа
        if plan.intent == "decomposition":
            return self._synthesize_decomposition(question, ok_results, plan, skipped)

        fallback = self._fallback_multi(question, ok_results, plan, skipped)

        # Формируем данные для LLM
        data: dict = {
            "question": question,
            "intent": plan.intent,
            "topic": plan.topic,
            "results_count": len(ok_results),
            "skipped_count": skipped,
            "results": [
                {
                    "aggregate_id": r.aggregate_id,
                    "label": r.label or r.aggregate_id,
                    "row_count": r.row_count,
                    "rows": r.rows[:5],  # первые 5 строк для контекста
                }
                for r in ok_results
            ],
        }

        user_prompt = json.dumps(data, ensure_ascii=False)
        answer = await self.llm_client.synthesize(self.SYSTEM_PROMPT, user_prompt, fallback)

        confidence: Literal["low", "medium", "high"]
        if ok_results:
            confidence = "high" if len(ok_results) == len(results) else "medium"
        else:
            confidence = "low"

        follow_ups = _TOPIC_FOLLOW_UPS.get(plan.topic, _DEFAULT_FOLLOW_UPS)

        return AnalysisResult(
            answer=answer,
            confidence=confidence,
            follow_ups=follow_ups,
        )

    # ── T039: Decomposition / factor analysis ─────────────────────────────────

    def _synthesize_decomposition(
        self,
        question: str,
        ok_results: list[AggregateResult],
        plan: MultiPlan,
        skipped: int,
    ) -> AnalysisResult:
        """Факторный анализ: сравнивает метрики по двум периодам, выявляет главный фактор.

        Алгоритм:
        1. Группирует результаты попарно (текущий / предыдущий период) по aggregate_id
        2. Вычисляет относительное изменение для каждого агрегата
        3. Определяет фактор с наибольшим относительным изменением
        4. Формирует ответ: «Выручка упала на X%. Основная причина: <фактор> (−Y%)»
        5. Максимум 3 фактора в ответе
        """
        if not ok_results:
            answer = "Данных по запросу не найдено."
            if skipped:
                answer += f" Пропущено запросов с ошибкой: {skipped}."
            return AnalysisResult(
                answer=answer,
                confidence="low",
                follow_ups=_DEFAULT_FOLLOW_UPS,
            )

        # Извлекаем скалярное значение из результата агрегата
        factors = self._extract_factors(ok_results)

        if not factors:
            # Нет числовых данных — возвращаем простой список
            lines = [f"• {r.label or r.aggregate_id}: {r.row_count} записей" for r in ok_results]
            if skipped:
                lines.append(f"_Пропущено: {skipped} ошибок._")
            return AnalysisResult(
                answer="\n".join(lines),
                confidence="medium",
                follow_ups=_TOPIC_FOLLOW_UPS.get(plan.topic, _DEFAULT_FOLLOW_UPS),
            )

        # Сортируем по модулю относительного изменения (убывание)
        factors_sorted = sorted(factors, key=lambda f: abs(f["rel_change"]), reverse=True)

        # Основная метрика: если topic совпадает с label фактора — используем его.
        # Иначе — фактор с наибольшим абсолютным изменением (первый в отсортированном списке).
        topic_lower = plan.topic.lower()
        target_factor = next(
            (f for f in factors if topic_lower in f["label"].lower()),
            None,
        )
        main_factor = target_factor if target_factor is not None else factors_sorted[0]
        main_pct = main_factor["rel_change"]
        main_label = main_factor["label"]
        direction = "упал" if main_pct < 0 else "вырос"

        lines: list[str] = [
            f"{main_label} {direction} на {abs(main_pct):.1f}%."
        ]

        # Дополнительные факторы (до 2-х, итого max 3 с основным).
        # Исключаем main_factor из полного списка, т.к. он может быть не в factors_sorted[0].
        secondary = [f for f in factors_sorted if f["label"] != main_label][:2]
        if secondary:
            cause_label = secondary[0]["label"]
            cause_pct = secondary[0]["rel_change"]
            sign = "−" if cause_pct < 0 else "+"
            lines.append(
                f"Основная причина: {cause_label} ({sign}{abs(cause_pct):.1f}%)."
            )
            for f in secondary[1:]:
                f_pct = f["rel_change"]
                f_sign = "−" if f_pct < 0 else "+"
                lines.append(f"Также: {f['label']} ({f_sign}{abs(f_pct):.1f}%).")

        if skipped:
            lines.append(f"_Пропущено запросов с ошибкой: {skipped}._")

        confidence: Literal["low", "medium", "high"] = "high" if len(ok_results) >= 2 else "medium"
        return AnalysisResult(
            answer="\n".join(lines),
            confidence=confidence,
            follow_ups=_TOPIC_FOLLOW_UPS.get(plan.topic, _DEFAULT_FOLLOW_UPS),
        )

    @staticmethod
    def _extract_factors(
        results: list[AggregateResult],
    ) -> list[dict]:
        """Группирует результаты попарно и вычисляет относительные изменения.

        Пара определяется по одинаковому aggregate_id. Первый встреченный считается
        «текущим» периодом, второй — «предыдущим» (порядок из MultiPlan.queries).
        Скалярное значение берётся из первой строки первого числового поля.
        """
        _NUMERIC_FIELDS = (
            "Revenue", "AvgCheck", "Visits", "Clients", "Count",
            "Total", "Value", "Amount", "Cnt", "Sum",
        )

        def _scalar(r: AggregateResult) -> float | None:
            if not r.rows:
                return None
            row = r.rows[0]
            for field in _NUMERIC_FIELDS:
                val = row.get(field)
                if isinstance(val, (int, float)):
                    return float(val)
            # Fallback: первое числовое значение в строке
            for val in row.values():
                if isinstance(val, (int, float)):
                    return float(val)
            return None

        # Группируем по aggregate_id (сохраняем порядок первого вхождения)
        seen: dict[str, AggregateResult] = {}
        pairs: list[tuple[AggregateResult, AggregateResult]] = []

        for r in results:
            agg_id = r.aggregate_id
            if agg_id not in seen:
                seen[agg_id] = r
            else:
                pairs.append((seen.pop(agg_id), r))

        orphans: list[AggregateResult] = list(seen.values())

        factors: list[dict] = []
        for current, previous in pairs:
            cur_val = _scalar(current)
            prev_val = _scalar(previous)
            if cur_val is None or prev_val is None or prev_val == 0:
                continue
            rel_change = (cur_val - prev_val) / abs(prev_val) * 100
            label = current.label or current.aggregate_id
            factors.append({"label": label, "rel_change": rel_change})

        # Одиночные результаты (нет пары) — включаем со счётчиком строк
        for r in orphans:
            if r.row_count > 0:
                factors.append({"label": r.label or r.aggregate_id, "rel_change": 0.0})

        return factors

    def _fallback_multi(
        self,
        question: str,
        ok_results: list[AggregateResult],
        plan: MultiPlan,
        skipped: int,
    ) -> str:
        lines: list[str] = []

        topic_desc = get_description(plan.topic)
        if topic_desc:
            lines.append(f"*{topic_desc}*")
            lines.append("")

        if not ok_results:
            lines.append("Данных по запросу не найдено.")
            if skipped:
                lines.append(f"Пропущено запросов с ошибкой: {skipped}.")
            return "\n".join(lines)

        # Comparison: показываем ключевую метрику с дельтой
        if plan.intent == "comparison" and len(ok_results) >= 2:
            lines.append(self._format_comparison_text(ok_results))
        else:
            for r in ok_results:
                label = r.label or r.aggregate_id
                # Показываем ключевую метрику вместо "N записей"
                metric_str = self._extract_key_metric(r)
                lines.append(f"• {label}: {metric_str}")

        if skipped:
            lines.append(f"\n_Пропущено запросов с ошибкой: {skipped}._")

        return "\n".join(lines)

    @staticmethod
    def _extract_key_metric(result: AggregateResult) -> str:
        """Извлекает ключевую метрику из AggregateResult для отображения."""
        if not result.rows:
            return "нет данных"
        # Для grouped данных (несколько строк) — показываем count
        if len(result.rows) > 1:
            return f"{result.row_count} записей"
        # Для single-row — показываем ключевые метрики
        row = result.rows[0]
        parts = []
        for key in ("Revenue", "Visits", "UniqueClients", "ClientCount", "TotalCount", "AvgCheck"):
            val = row.get(key)
            if val is not None and isinstance(val, (int, float)):
                label = _METRIC_LABELS.get(key, key)
                parts.append(f"{label}: {val:,.0f}" if val > 100 else f"{label}: {val}")
                if len(parts) >= 3:
                    break
        return ", ".join(parts) if parts else f"{result.row_count} записей"

    @staticmethod
    def _format_comparison_text(ok_results: list[AggregateResult]) -> str:
        """Форматирует текст сравнения двух периодов с дельтами."""
        r_a, r_b = ok_results[0], ok_results[1]
        label_a = r_a.label or "Период 1"
        label_b = r_b.label or "Период 2"

        lines = [f"Сравнение: {label_a} vs {label_b}"]

        # Суммируем числовые метрики для каждого периода
        skip = {"ObjectId", "MasterId", "ClientId", "Id", "CRMId", "Top"}

        def _sum(rows: list[dict]) -> dict[str, float]:
            totals: dict[str, float] = {}
            for row in rows:
                for k, v in row.items():
                    if isinstance(v, (int, float)) and k not in skip:
                        totals[k] = totals.get(k, 0.0) + float(v)
            return totals

        agg_a = _sum(r_a.rows) if r_a.rows else {}
        agg_b = _sum(r_b.rows) if r_b.rows else {}

        # Показываем до 4 ключевых метрик
        shown = 0
        for key in list(dict.fromkeys(list(agg_a.keys()) + list(agg_b.keys()))):
            if shown >= 4:
                break
            va = agg_a.get(key, 0.0)
            vb = agg_b.get(key, 0.0)
            if va == 0 and vb == 0:
                continue
            label = _METRIC_LABELS.get(key, key)
            delta_str = ""
            if vb != 0:
                delta = (va - vb) / abs(vb) * 100
                sign = "+" if delta > 0 else ("\u2212" if delta < 0 else "")
                delta_str = f" ({sign}{abs(delta):.0f}%)"
            lines.append(
                f"• {label}: {label_a} {va:,.0f}, {label_b} {vb:,.0f}{delta_str}"
            )
            shown += 1

        return "\n".join(lines)

    # ── T036: Comparison ──────────────────────────────────────────────────────

    @staticmethod
    def _is_incomplete_period(date_to_str: str) -> bool:
        """Возвращает True если дата окончания периода — сегодня или в будущем.

        Неполный период — текущий незавершённый месяц/неделя, т.е. date_to >= сегодня.
        """
        if not date_to_str:
            return False
        try:
            d = date.fromisoformat(date_to_str[:10])
            return d >= date.today()
        except ValueError:
            return False

    @staticmethod
    def _calc_deltas(rows_a: list[dict], rows_b: list[dict]) -> dict[str, float]:
        """Вычисляет дельты числовых метрик между двумя наборами данных (в процентах).

        Суммирует числовые колонки каждого набора и считает (a - b) / |b| * 100.
        """
        skip = {"ObjectId", "MasterId", "ClientId", "Id", "CRMId", "Top"}

        def _sum_rows(rows: list[dict]) -> dict[str, float]:
            totals: dict[str, float] = {}
            for row in rows:
                for k, v in row.items():
                    if isinstance(v, (int, float)) and k not in skip:
                        totals[k] = totals.get(k, 0.0) + float(v)
            return totals

        agg_a = _sum_rows(rows_a)
        agg_b = _sum_rows(rows_b)

        deltas: dict[str, float] = {}
        all_keys = set(agg_a.keys()) | set(agg_b.keys())
        for k in all_keys:
            va = agg_a.get(k, 0.0)
            vb = agg_b.get(k, 0.0)
            if vb != 0:
                deltas[k] = (va - vb) / abs(vb) * 100
            else:
                deltas[k] = 0.0
        return deltas

    def format_comparison(
        self,
        comparison: ComparisonResult,
        *,
        incomplete_period_a: bool = False,
        incomplete_period_b: bool = False,
    ) -> str:
        """T036: Форматирует результат сравнения двух периодов в текст.

        Формат: "Метрика за период 1: X. За период 2: Y. Изменение: +/-Z%"
        Если период неполный — добавляет пометку "(неполный период)".
        """
        lines: list[str] = []

        label_a = comparison.period_a or "Период 1"
        label_b = comparison.period_b or "Период 2"

        if incomplete_period_a:
            label_a += " (неполный период)"
        if incomplete_period_b:
            label_b += " (неполный период)"

        # Считаем дельты если не посчитаны
        deltas = comparison.deltas
        if not deltas:
            deltas = self._calc_deltas(
                comparison.results_a.rows,
                comparison.results_b.rows,
            )

        # Суммируем метрики для отображения
        def _agg(rows: list[dict]) -> dict[str, float]:
            skip = {"ObjectId", "MasterId", "ClientId", "Id", "CRMId", "Top"}
            totals: dict[str, float] = {}
            for row in rows:
                for k, v in row.items():
                    if isinstance(v, (int, float)) and k not in skip:
                        totals[k] = totals.get(k, 0.0) + float(v)
            return totals

        agg_a = _agg(comparison.results_a.rows)
        agg_b = _agg(comparison.results_b.rows)

        all_keys = list(dict.fromkeys(list(agg_a.keys()) + list(agg_b.keys())))

        for metric in all_keys[:6]:  # не более 6 метрик в тексте
            va = agg_a.get(metric, 0.0)
            vb = agg_b.get(metric, 0.0)
            delta = deltas.get(metric, 0.0)

            if delta > 0:
                delta_str = f"+{delta:.1f}%"
            elif delta < 0:
                delta_str = f"\u2212{abs(delta):.1f}%"
            else:
                delta_str = "0%"

            val_a_str = f"{va:,.0f}" if va == int(va) else f"{va:,.1f}"
            val_b_str = f"{vb:,.0f}" if vb == int(vb) else f"{vb:,.1f}"

            lines.append(
                f"• {metric} — {label_a}: {val_a_str}. "
                f"{label_b}: {val_b_str}. Изменение: {delta_str}."
            )

        if not lines:
            lines.append("Нет числовых данных для сравнения.")

        return "\n".join(lines)
