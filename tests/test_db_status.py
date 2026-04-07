from __future__ import annotations

import pytest

from harbor.config import HarborSettings
from harbor.persistence.status import database_status_payload


def test_db_status_not_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HARBOR_SQLALCHEMY_DATABASE_URL", raising=False)
    monkeypatch.delenv("HARBOR_POSTGRES_HOST", raising=False)
    monkeypatch.delenv("HARBOR_POSTGRES_DB", raising=False)
    monkeypatch.delenv("HARBOR_POSTGRES_USER", raising=False)
    monkeypatch.delenv("HARBOR_POSTGRES_PASSWORD", raising=False)

    payload = database_status_payload(settings=HarborSettings())

    assert payload["status"] == "not_configured"
    assert payload["database"]["postgres_configured"] is False
