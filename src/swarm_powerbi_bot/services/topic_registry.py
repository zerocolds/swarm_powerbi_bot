"""Реестр аналитических тем КДО — маппинг вопросов на хранимые процедуры."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TopicEntry:
    topic_id: str
    procedure: str
    keywords: list[str] = field(default_factory=list)
    description: str = ""


# ──────────────────────────────────────────────
# Реестр 15 тем из модели КДО 3.2.1
# ──────────────────────────────────────────────

TOPICS: list[TopicEntry] = [
    TopicEntry(
        topic_id="all_clients",
        procedure="dbo.spKDO_AllClients",
        keywords=["база клиент", "клиентов в базе", "количество клиент", "новые клиент", "все клиент", "клиентская база"],
        description="Все клиенты — база, сегментация, количество",
    ),
    TopicEntry(
        topic_id="outflow",
        procedure="dbo.spKDO_Outflow",
        keywords=["отток", "потер", "ушедш", "не вернул", "потеряли"],
        description="Отток клиентов — кто уходит и почему",
    ),
    TopicEntry(
        topic_id="leaving",
        procedure="dbo.spKDO_Leaving",
        keywords=["уходящ", "покида", "расставан", "уход клиент", "на грани ухода"],
        description="Уходящие — клиенты на грани ухода",
    ),
    TopicEntry(
        topic_id="statistics",
        procedure="dbo.spKDO_Statistics",
        keywords=["статистик", "сводк", "итог", "показател", "общ", "kpi"],
        description="Статистика — сводные KPI-показатели",
    ),
    TopicEntry(
        topic_id="trend",
        procedure="dbo.spKDO_Trend",
        keywords=["тренд", "динамик", "рост", "падени", "изменен",
                  "сравнен", "сравни", "неделя к недел", "по неделям",
                  "по месяцам", "помесячно", "понедельно"],
        description="Тренды — динамика метрик во времени",
    ),
    TopicEntry(
        topic_id="forecast",
        procedure="dbo.spKDO_Forecast",
        keywords=["прогноз", "предсказ", "ожидаем", "план визит", "загрузк"],
        description="Прогноз визитов — загрузка мастеров",
    ),
    TopicEntry(
        topic_id="communications",
        procedure="dbo.spKDO_Communications",
        keywords=["коммуникац", "звонок", "обзвон", "сообщен", "связь с клиент"],
        description="Коммуникации — работа с клиентами",
    ),
    TopicEntry(
        topic_id="referrals",
        procedure="dbo.spKDO_Referrals",
        keywords=["реферж", "реферал", "приглаш", "рекоменда", "привёл"],
        description="Рефережи — реферальная программа",
    ),
    TopicEntry(
        topic_id="quality",
        procedure="dbo.spKDO_Quality",
        keywords=["качество", "контроль качеств", "оценк", "отзыв", "жалоб"],
        description="Контроль качества — оценки и NPS",
    ),
    TopicEntry(
        topic_id="attachments",
        procedure="dbo.spKDO_Attachments",
        keywords=["вложен", "абонемент", "подписк", "членств"],
        description="Вложения/Абонементы — подписки клиентов",
    ),
    TopicEntry(
        topic_id="birthday",
        procedure="dbo.spKDO_Birthday",
        keywords=["рожден", "именинник", "поздравлен", "день рожд"],
        description="Дни рождения — именинники и поздравления",
    ),
    TopicEntry(
        topic_id="waitlist",
        procedure="dbo.spKDO_WaitList",
        keywords=["ожидан", "лист ожидан", "очередь", "запись"],
        description="Лист ожидания — очередь клиентов",
    ),
    TopicEntry(
        topic_id="training",
        procedure="dbo.spKDO_Training",
        keywords=["обучен", "тренинг", "курс", "материал"],
        description="Обучение — обучающие материалы для мастеров",
    ),
    TopicEntry(
        topic_id="masters",
        procedure="dbo.spKDO_Masters",
        keywords=["мастер", "специалист", "сотрудник", "загрузка мастер", "персонал"],
        description="Мастера — загрузка, эффективность специалистов",
    ),
    TopicEntry(
        topic_id="services",
        procedure="dbo.spKDO_Services",
        keywords=["услуг", "выручк", "чек", "оборот", "продаж", "средний чек", "доход"],
        description="Услуги/Финансы — выручка, средний чек, популярные услуги",
    ),
    TopicEntry(
        topic_id="noshow",
        procedure="dbo.spKDO_NoShow",
        keywords=["недошедш", "не дошёл", "не дошел", "не пришёл", "не пришел", "отменил запись", "отмена записи"],
        description="Недошедшие — клиенты с отменёнными записями",
    ),
    TopicEntry(
        topic_id="opz",
        procedure="dbo.spKDO_OPZ",
        keywords=["опз", "оперативн", "оперативная запись"],
        description="ОПЗ — оперативные записи на другой день",
    ),
]

# Индекс для быстрого поиска
_TOPICS_BY_ID: dict[str, TopicEntry] = {t.topic_id: t for t in TOPICS}

DEFAULT_TOPIC = "statistics"


# Слова-модификаторы: меняют отображение, но не тему
# Если вопрос состоит ТОЛЬКО из модификаторов — это follow-up к предыдущей теме
_MODIFIER_KEYWORDS = {
    "сравнен", "сравни", "неделя к недел", "по неделям", "по месяцам",
    "помесячно", "понедельно", "динамик", "тренд", "изменен",
    "подробн", "детальн", "разбивк", "группиров",
}


def detect_topic(question: str, last_topic: str = "") -> str:
    """Определяет тему вопроса по ключевым словам (скоринг).

    Если вопрос содержит только модификаторы (сравни, по неделям)
    без явной темы — используем last_topic как контекст разговора.
    """
    text = question.lower()
    best_id = DEFAULT_TOPIC
    best_score = 0

    for entry in TOPICS:
        score = sum(1 for kw in entry.keywords if kw in text)
        if score > best_score:
            best_score = score
            best_id = entry.topic_id

    # Follow-up: вопрос без явной темы + есть предыдущий контекст
    if last_topic and last_topic in _TOPICS_BY_ID:
        # Если тема не найдена (score=0) — берём контекст
        if best_score == 0:
            return last_topic
        # Если совпал только trend по модификаторам — это follow-up
        if best_id == "trend" and best_score <= 2:
            has_real_topic = any(
                kw in text for entry in TOPICS
                if entry.topic_id != "trend"
                for kw in entry.keywords
            )
            if not has_real_topic:
                return last_topic

    # Тема не определена и нет контекста разговора — не выполняем SQL
    if best_score == 0:
        return "unknown"

    return best_id


def get_topic(topic_id: str) -> TopicEntry | None:
    return _TOPICS_BY_ID.get(topic_id)


def get_procedure(topic_id: str) -> str:
    entry = _TOPICS_BY_ID.get(topic_id)
    if entry:
        return entry.procedure
    return _TOPICS_BY_ID[DEFAULT_TOPIC].procedure


def get_description(topic_id: str) -> str:
    entry = _TOPICS_BY_ID.get(topic_id)
    return entry.description if entry else ""
