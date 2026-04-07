from __future__ import annotations

from fastapi.testclient import TestClient

from harbor.app import app

client = TestClient(app)


def test_db_status_reports_not_configured_by_default() -> None:
    response = client.get("/db/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not_configured"
    assert body["database"]["postgres_configured"] is False
