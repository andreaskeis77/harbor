from __future__ import annotations

from harbor.config import Settings


def test_default_settings_postgres_not_configured() -> None:
    settings = Settings()
    assert settings.postgres_configured is False
    assert settings.sqlalchemy_database_url_redacted is None


def test_runtime_defaults() -> None:
    settings = Settings()
    assert settings.environment == "dev"
    assert settings.port == 8000
