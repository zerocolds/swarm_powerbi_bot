"""Тесты keyword fallback scoring для detect_topic() — US1 (FR-001).

Покрывает:
- T001: контекстные правила period + «выручк» → statistics, не services
- T002: ranking + финансы → masters
- T003: прямые маппинги сохраняются (популярные услуги → services, отток → outflow)
"""
from swarm_powerbi_bot.services.topic_registry import detect_topic


class TestContextRulesPeriodRevenue:
    """T001 — period context + «выручк» → statistics, не services."""

    def test_revenue_this_week_routes_to_statistics(self):
        """«выручка за неделю» — период «за недел» → statistics."""
        assert detect_topic("выручка за неделю") == "statistics"

    def test_revenue_this_month_routes_to_statistics(self):
        """«выручка за месяц» — период «за месяц» → statistics."""
        assert detect_topic("выручка за месяц") == "statistics"

    def test_revenue_quarter_routes_to_statistics(self):
        """«выручка за квартал» → statistics."""
        assert detect_topic("выручка за квартал") == "statistics"

    def test_revenue_year_routes_to_statistics(self):
        """«выручка за год» → statistics."""
        assert detect_topic("выручка за год") == "statistics"

    def test_revenue_plain_routes_to_services(self):
        """«выручка по услугам» без периода → services (выручк + услуг)."""
        result = detect_topic("выручка по услугам")
        # Слово «услуг» в services, «выручк» тоже в services — ожидаем services
        assert result == "services"

    def test_stat_weekly_kpi(self):
        """«статистика за неделю» → statistics (прямое совпадение)."""
        assert detect_topic("статистика за неделю") == "statistics"


class TestContextRulesMastersRanking:
    """T002 — ranking + финансы → masters."""

    def test_who_brought_more_money(self):
        """«кто больше принёс денег» → masters."""
        assert detect_topic("кто больше принёс денег") == "masters"

    def test_who_earned_most(self):
        """«кто больше заработал» → masters."""
        assert detect_topic("кто больше заработал") == "masters"

    def test_top_masters_by_revenue(self):
        """«топ мастеров по выручке» → masters."""
        assert detect_topic("топ мастеров по выручке") == "masters"

    def test_rating_by_money(self):
        """«рейтинг по деньгам» — rating + денег → masters."""
        assert detect_topic("рейтинг мастеров по деньгам") == "masters"

    def test_best_by_income(self):
        """«лучший по доходу» — лучш + доход → masters."""
        assert detect_topic("кто лучший по доходу") == "masters"


class TestDirectMappingsPreserved:
    """T003 — прямые маппинги сохраняются без деградации."""

    def test_popular_services_routes_to_services(self):
        """«популярные услуги» → services (услуг без периода)."""
        assert detect_topic("популярные услуги за месяц") == "services"

    def test_outflow_routes_to_outflow(self):
        """«отток» → outflow."""
        assert detect_topic("отток клиентов") == "outflow"

    def test_outflow_keyword_preserved(self):
        """«клиенты потерянные» → outflow (потер)."""
        assert detect_topic("потеряли клиентов за месяц") == "outflow"

    def test_masters_direct_keyword(self):
        """«загрузка мастеров» → masters (прямой маппинг)."""
        assert detect_topic("загрузка мастеров на неделю") == "masters"

    def test_trend_dynamic(self):
        """«динамика выручки по неделям» → trend (тренд + изменен)."""
        assert detect_topic("динамика выручки по неделям") == "trend"

    def test_unknown_topic_no_context(self):
        """Вопрос без ключевых слов, нет last_topic → unknown."""
        assert detect_topic("как дела") == "unknown"

    def test_default_with_context(self):
        """Вопрос без ключевых слов + есть last_topic → берём last_topic."""
        assert detect_topic("как дела", last_topic="services") == "services"
