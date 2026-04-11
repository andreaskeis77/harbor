"""Tests for configuration edge cases, error paths, and resilience.

Validates:
- DatabaseNotConfiguredError → 503 response via middleware
- Config redaction handles various URL formats without leaking passwords
- database_status_payload handles connectivity errors gracefully
- database_status_payload returns "configured" when check is not requested
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from harbor.config import HarborSettings, clear_settings_cache
from harbor.persistence.status import database_status_payload

_ENV_KEYS = (
    "HARBOR_SQLALCHEMY_DATABASE_URL",
    "HARBOR_POSTGRES_HOST",
    "HARBOR_POSTGRES_PORT",
    "HARBOR_POSTGRES_DB",
    "HARBOR_POSTGRES_USER",
    "HARBOR_POSTGRES_PASSWORD",
)


@pytest.fixture()
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()
    yield
    clear_settings_cache()


# ---------------------------------------------------------------------------
# 1. DatabaseNotConfiguredError → 503 via middleware
# ---------------------------------------------------------------------------


def test_database_not_configured_returns_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When no DB is configured, DB-dependent endpoints must return 503."""
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()

    from harbor.app import create_app

    settings = HarborSettings()
    app = create_app(settings=settings)
    with TestClient(app, raise_server_exceptions=False) as tc:
        response = tc.get("/api/v1/projects")

    assert response.status_code == 503
    assert "not configured" in response.json()["detail"].lower()
    clear_settings_cache()


# ---------------------------------------------------------------------------
# 2. Config redaction — password never leaks
# ---------------------------------------------------------------------------


def test_redaction_explicit_url_with_password(_clean_env: None) -> None:
    settings = HarborSettings(
        sqlalchemy_database_url="postgresql+psycopg://admin:s3cret@db.host:5432/harbor"
    )
    redacted = settings.sqlalchemy_database_url_redacted
    assert redacted is not None
    assert "s3cret" not in redacted
    assert "***" in redacted
    assert "admin" in redacted
    assert "db.host" in redacted


def test_redaction_explicit_url_without_credentials(_clean_env: None) -> None:
    settings = HarborSettings(
        sqlalchemy_database_url="sqlite+pysqlite:///test.db"
    )
    redacted = settings.sqlalchemy_database_url_redacted
    assert redacted == "sqlite+pysqlite:///test.db"


def test_redaction_postgres_from_parts(_clean_env: None) -> None:
    settings = HarborSettings(
        postgres_host="db.example.com",
        postgres_port=5432,
        postgres_db="harbordb",
        postgres_user="harboruser",
        postgres_password="topsecret",
    )
    redacted = settings.sqlalchemy_database_url_redacted
    assert redacted is not None
    assert "topsecret" not in redacted
    assert "***" in redacted
    assert "harboruser" in redacted


def test_redaction_none_when_not_configured(_clean_env: None) -> None:
    settings = HarborSettings()
    assert settings.sqlalchemy_database_url_redacted is None


def test_effective_url_from_explicit(_clean_env: None) -> None:
    settings = HarborSettings(
        sqlalchemy_database_url="sqlite+pysqlite:///test.db"
    )
    assert settings.sqlalchemy_database_url_effective == "sqlite+pysqlite:///test.db"


def test_effective_url_from_parts(_clean_env: None) -> None:
    settings = HarborSettings(
        postgres_host="localhost",
        postgres_port=5432,
        postgres_db="harbor",
        postgres_user="user",
        postgres_password="pass",
    )
    url = settings.sqlalchemy_database_url_effective
    assert url is not None
    assert url.startswith("postgresql+psycopg://")
    assert "user:pass@localhost:5432/harbor" in url


def test_effective_url_none_when_not_configured(_clean_env: None) -> None:
    settings = HarborSettings()
    assert settings.sqlalchemy_database_url_effective is None


# ---------------------------------------------------------------------------
# 3. database_status_payload edge cases
# ---------------------------------------------------------------------------


def test_status_configured_without_connectivity_check(_clean_env: None) -> None:
    """When DB is configured but check not requested, return 'configured' without connecting."""
    settings = HarborSettings(
        sqlalchemy_database_url="postgresql+psycopg://u:p@host:5432/db"
    )
    payload = database_status_payload(
        settings=settings, connectivity_check_requested=False
    )
    assert payload["status"] == "configured"
    assert payload["connectivity"] is None
    assert payload["connectivity_check_requested"] is False


def test_status_connectivity_error_is_captured(_clean_env: None) -> None:
    """When connectivity check fails, error details must be captured, not raised."""
    settings = HarborSettings(
        sqlalchemy_database_url="postgresql+psycopg://u:p@nonexistent:5432/db"
    )
    # Mock get_engine to return an engine that fails on connect
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = ConnectionError("Connection refused")

    with patch("harbor.persistence.status.get_engine", return_value=mock_engine):
        payload = database_status_payload(
            settings=settings, connectivity_check_requested=True
        )

    assert payload["status"] == "connectivity_error"
    assert isinstance(payload["connectivity"], dict)
    assert payload["connectivity"]["status"] == "error"
    assert "ConnectionError" in payload["connectivity"]["error_type"]
    assert "Connection refused" in payload["connectivity"]["message"]


def test_status_connectivity_ok_with_working_db(client: TestClient) -> None:
    """The DB status endpoint with check=true should return 'ok' when DB is healthy."""
    response = client.get("/db/status?connectivity_check=true")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["connectivity"] == "ok"
