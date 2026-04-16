"""Тесты переключения и сохранения контекста разговора.

Проверяет что бот:
- Сохраняет тему после вопроса
- Использует last_topic для follow-up вопросов
- Переключает тему при явном указании
- Не путает модификаторы (сравни, по неделям) с темой
"""
from swarm_powerbi_bot.services.topic_registry import detect_topic


# ── Follow-up: тема сохраняется ──────────────────────────────

class TestContextRetention:
    """Если новый вопрос — модификатор (сравни, подробнее),
    тема должна остаться от предыдущего вопроса."""

    def test_comparison_keeps_outflow(self):
        topic = detect_topic("сравни месяц к месяцу", last_topic="outflow")
        assert topic == "outflow"

    def test_weekly_keeps_outflow(self):
        topic = detect_topic("покажи по неделям", last_topic="outflow")
        assert topic == "outflow"

    def test_details_keeps_masters(self):
        topic = detect_topic("подробнее", last_topic="masters")
        assert topic == "masters"

    def test_monthly_keeps_services(self):
        topic = detect_topic("по месяцам за квартал", last_topic="services")
        assert topic == "services"

    def test_dynamics_keeps_leaving(self):
        topic = detect_topic("покажи динамику", last_topic="leaving")
        assert topic == "leaving"

    def test_breakdown_keeps_quality(self):
        """'разбивка по категориям' — нет явной темы, follow-up."""
        topic = detect_topic("разбивка по категориям", last_topic="quality")
        assert topic == "quality"


# ── Явное переключение темы ──────────────────────────────────

class TestContextSwitch:
    """При явных ключевых словах другой темы — переключаемся."""

    def test_switch_from_outflow_to_masters(self):
        topic = detect_topic("покажи мастеров за неделю", last_topic="outflow")
        assert topic == "masters"

    def test_switch_from_outflow_to_services(self):
        # «выручка за месяц» → statistics (FR-001: период + «выручк» → statistics)
        topic = detect_topic("какая выручка за месяц?", last_topic="outflow")
        assert topic == "statistics"

    def test_switch_from_masters_to_outflow(self):
        topic = detect_topic("покажи отток", last_topic="masters")
        assert topic == "outflow"

    def test_switch_from_statistics_to_quality(self):
        topic = detect_topic("контроль качества за неделю", last_topic="statistics")
        assert topic == "quality"

    def test_switch_from_outflow_to_noshow(self):
        topic = detect_topic("кто не дошёл?", last_topic="outflow")
        assert topic == "noshow"


# ── Без контекста — fallback ─────────────────────────────────

class TestNoContext:
    """Без last_topic модификаторы идут в trend, остальное в statistics."""

    def test_comparison_without_context_goes_trend(self):
        topic = detect_topic("сравни по неделям")
        assert topic == "trend"

    def test_gibberish_returns_unknown(self):
        # score=0, нет контекста — возвращаем sentinel "unknown" вместо дефолта
        topic = detect_topic("привет как дела")
        assert topic == "unknown"

    def test_clear_topic_without_context(self):
        topic = detect_topic("отток за месяц")
        assert topic == "outflow"


# ── Пограничные случаи ──────────────────────────────────────

class TestEdgeCases:
    """Вопросы с неочевидным поведением."""

    def test_empty_question_with_context(self):
        topic = detect_topic("", last_topic="outflow")
        assert topic == "outflow"

    def test_period_only_keeps_context(self):
        """'за последнюю неделю' без темы — follow-up."""
        topic = detect_topic("за последнюю неделю", last_topic="outflow")
        assert topic == "outflow"

    def test_invalid_last_topic_ignored(self):
        # invalid last_topic не попадает в _TOPICS_BY_ID, поэтому контекст не используется.
        # score=0 → возвращаем "unknown"
        topic = detect_topic("привет", last_topic="nonexistent_topic")
        assert topic == "unknown"

    def test_trend_with_explicit_revenue_switches(self):
        """'тренд выручки' — явно про тренд, не follow-up."""
        topic = detect_topic("тренд выручки", last_topic="outflow")
        # "выручк" matches services, "тренд" matches trend
        assert topic in ("trend", "services")
