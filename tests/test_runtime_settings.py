from __future__ import annotations

import pytest

from harbor.config import HarborSettings, clear_settings_cache

_RUNTIME_ENV_KEYS = (
    "HARBOR_SQLALCHEMY_DATABASE_URL",
    "HARBOR_POSTGRES_HOST",
    "HARBOR_POSTGRES_PORT",
    "HARBOR_POSTGRES_DB",
    "HARBOR_POSTGRES_USER",
    "HARBOR_POSTGRES_PASSWORD",
    "HARBOR_OPENAI_API_KEY",
    "HARBOR_OPENAI_MODEL",
    "HARBOR_OPENAI_BASE_URL",
    "HARBOR_OPENAI_TIMEOUT_SECONDS",
)


@pytest.fixture()
def isolated_runtime_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _RUNTIME_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_runtime_dict_contains_expected_fields(isolated_runtime_env: None) -> None:
    settings = HarborSettings()
    payload = settings.runtime_dict()

    assert payload["app_name"] == "Harbor"
    assert payload["environment"] == "dev"
    assert payload["version"] == "0.1.4a0"
    assert payload["postgres_configured"] is False
    assert payload["openai_configured"] is False
    assert payload["openai_model"] == "gpt-5"


def test_db_runtime_dict_redacts_or_none(isolated_runtime_env: None) -> None:
    settings = HarborSettings()
    payload = settings.db_runtime_dict()

    assert payload["postgres_configured"] is False
    assert payload["sqlalchemy_database_url_redacted"] is None


def test_openai_runtime_dict_defaults(isolated_runtime_env: None) -> None:
    settings = HarborSettings()
    payload = settings.openai_runtime_dict()

    assert payload["provider"] == "openai"
    assert payload["configured"] is False
    assert payload["api_key_present"] is False
    assert payload["model"] == "gpt-5"
    assert payload["base_url"] is None
    assert payload["timeout_seconds"] == 30.0
