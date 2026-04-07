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
    db_file = tmp_path / "search_run_test.db"
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


def create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Run Project",
            "short_description": "Search run baseline",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_campaign(client: TestClient, project_id: str) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns",
        json={
            "title": "Initial discovery",
            "query_text": "house reef dive resort",
            "campaign_kind": "manual",
            "status": "planned",
            "note": "Seed search campaign",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_list_get_and_patch_search_run(client: TestClient) -> None:
    project = create_project(client)
    campaign = create_campaign(client, project["project_id"])

    create_response = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs",
        json={
            "title": "Run 1",
            "run_kind": "manual",
            "status": "planned",
            "query_text_snapshot": "house reef dive resort",
            "note": "first run",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Run 1"

    list_response = client.get(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs"
    )
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed["items"]) == 1

    patch_response = client.patch(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{created['search_run_id']}/status",
        json={"status": "running", "note": "started"},
    )
    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["status"] == "running"
    assert patched["note"] == "started"
    assert patched["started_at"] is not None

    get_response = client.get(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{created['search_run_id']}"
    )
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["search_run_id"] == created["search_run_id"]


def test_search_run_404_for_missing_campaign(client: TestClient) -> None:
    project = create_project(client)
    response = client.get(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/not-found/runs"
    )
    assert response.status_code == 404
