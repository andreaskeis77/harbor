from fastapi.testclient import TestClient

from harbor.app import app


def test_healthz_returns_ok_payload() -> None:
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app_name"] == "Harbor"
    assert "version" in payload


def test_root_returns_runtime_message() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["name"] == "Harbor"
