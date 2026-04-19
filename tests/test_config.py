from swarm_powerbi_bot.config import Settings


def test_report_base_url_fallback_from_legacy_env(monkeypatch):
    monkeypatch.setenv("USE_DOTENV", "0")
    monkeypatch.delenv("REPORT_BASE_URL", raising=False)
    monkeypatch.setenv("PBI_HOST", "10.10.10.10")
    monkeypatch.setenv("PBI_USER", "repManager")
    monkeypatch.setenv("PBI_PASS", "secret")

    settings = Settings.from_env()
    assert settings.report_base_url.startswith("https://repManager:secret@10.10.10.10/")


def test_report_base_url_explicit_wins(monkeypatch):
    monkeypatch.setenv("USE_DOTENV", "0")
    monkeypatch.setenv("REPORT_BASE_URL", "http://custom/powerbi/?id=")
    monkeypatch.setenv("PBI_HOST", "10.10.10.10")
    monkeypatch.setenv("PBI_USER", "repManager")
    monkeypatch.setenv("PBI_PASS", "secret")

    settings = Settings.from_env()
    assert settings.report_base_url == "http://custom/powerbi/?id="
