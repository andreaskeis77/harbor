from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache
from harbor.persistence import Base
from harbor.persistence.session import build_engine


@pytest.fixture()
def client(tmp_path):
    db_file = tmp_path / "projects_test.db"
    os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = f"sqlite+pysqlite:///{db_file.as_posix()}"
    clear_settings_cache()

    settings = HarborSettings()
    engine = build_engine(settings)
    assert engine is not None
    Base.metadata.create_all(bind=engine)

    app = create_app(settings=settings)
    with TestClient(app) as client:
        yield client

    os.environ.pop("HARBOR_SQLALCHEMY_DATABASE_URL", None)
    clear_settings_cache()


def test_create_list_get_project(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/projects",
        json={
            "title": "Scuba Research",
            "short_description": "Hotels with house reef",
            "project_type": "standard",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Scuba Research"
    assert created["status"] == "draft"

    list_response = client.get("/api/v1/projects")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed["items"]) == 1
    assert listed["items"][0]["project_id"] == created["project_id"]

    get_response = client.get(f"/api/v1/projects/{created['project_id']}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["project_id"] == created["project_id"]
    assert fetched["short_description"] == "Hotels with house reef"


def test_get_project_404(client: TestClient) -> None:
    response = client.get("/api/v1/projects/not-found")
    assert response.status_code == 404
