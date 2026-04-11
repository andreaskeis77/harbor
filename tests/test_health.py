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
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "Harbor"
    assert "version" in body
    assert "environment" in body


def test_runtime() -> None:
    app = create_app(settings=HarborSettings())
    with TestClient(app) as client:
        response = client.get("/runtime")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    runtime = body["runtime"]
    assert runtime["app_name"] == "Harbor"
    assert "version" in runtime
    assert "postgres_configured" in runtime
    assert "openai_configured" in runtime
