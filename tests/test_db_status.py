from __future__ import annotations

from harbor.config import HarborSettings
from harbor.persistence.status import database_status_payload


def test_db_status_not_configured() -> None:
    payload = database_status_payload(settings=HarborSettings())

    assert payload["status"] == "not_configured"
    assert payload["database"]["postgres_configured"] is False
