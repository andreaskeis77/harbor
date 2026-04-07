from __future__ import annotations

from harbor.config import HarborSettings


def test_runtime_dict_contains_expected_fields() -> None:
    settings = HarborSettings()
    payload = settings.runtime_dict()

    assert payload["app_name"] == "Harbor"
    assert payload["environment"] == "dev"
    assert payload["version"] == "0.1.3a0"
    assert payload["postgres_configured"] is False


def test_db_runtime_dict_redacts_or_none() -> None:
    settings = HarborSettings()
    payload = settings.db_runtime_dict()

    assert payload["postgres_configured"] is False
    assert payload["sqlalchemy_database_url_redacted"] is None
