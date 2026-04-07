from __future__ import annotations

from fastapi.testclient import TestClient

from harbor.app import create_app
from harbor.config import HarborSettings


def test_root() -> None:
    app = create_app(settings=HarborSettings())
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_healthz() -> None:
    app = create_app(settings=HarborSettings())
    with TestClient(app) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
