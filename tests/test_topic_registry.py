from swarm_powerbi_bot.services.topic_registry import (
    TOPICS,
    detect_topic,
    get_description,
    get_procedure,
    get_topic,
)


def test_all_topics_have_keywords():
    for entry in TOPICS:
        assert len(entry.keywords) > 0, f"topic {entry.topic_id} has no keywords"


def test_all_topics_have_procedure():
    for entry in TOPICS:
        assert entry.procedure.startswith("dbo.spKDO_"), (
            f"topic {entry.topic_id} procedure should start with dbo.spKDO_"
        )


def test_detect_outflow():
    assert detect_topic("Покажи отток клиентов за месяц") == "outflow"


def test_detect_clients():
    assert detect_topic("Сколько всего клиентов в базе?") == "all_clients"


def test_detect_referrals():
    assert detect_topic("Сколько клиентов пришло по рефералам?") == "referrals"


def test_detect_masters():
    assert detect_topic("Загрузка мастеров за неделю") == "masters"


def test_detect_services():
    assert detect_topic("Какая выручка и средний чек?") == "services"


def test_detect_quality():
    assert detect_topic("Покажи контроль качества и отзывы") == "quality"


def test_detect_communications():
    assert detect_topic("Статистика обзвонов и коммуникаций") == "communications"


def test_detect_trend():
    assert detect_topic("Покажи тренд и динамику показателей") == "trend"


def test_detect_forecast():
    assert detect_topic("Прогноз визитов на следующую неделю") == "forecast"


def test_detect_birthday():
    assert detect_topic("Кто именинник на этой неделе?") == "birthday"


def test_detect_waitlist():
    assert detect_topic("Покажи лист ожидания") == "waitlist"


def test_detect_leaving():
    assert detect_topic("Кто из клиентов уходящий?") == "leaving"


def test_detect_attachments():
    assert detect_topic("Статистика по абонементам и вложениям") == "attachments"


def test_detect_training():
    assert detect_topic("Какие обучения прошли мастера?") == "training"


def test_detect_fallback_to_statistics():
    assert detect_topic("Привет, как дела?") == "statistics"


def test_get_topic_exists():
    entry = get_topic("outflow")
    assert entry is not None
    assert entry.topic_id == "outflow"


def test_get_topic_none():
    assert get_topic("nonexistent") is None


def test_get_procedure_exists():
    assert get_procedure("outflow") == "dbo.spKDO_Outflow"


def test_get_procedure_fallback():
    assert get_procedure("nonexistent") == "dbo.spKDO_Statistics"


def test_get_description():
    desc = get_description("services")
    assert "выручка" in desc.lower() or "услуг" in desc.lower()
