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
    db_file = tmp_path / "source_test.db"
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
            "title": "Source Project",
            "short_description": "Research source slice",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_attach_and_list_project_sources(client: TestClient) -> None:
    project = create_project(client)

    source_response = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "Dive resort page",
            "canonical_url": "https://example.com/dive-resort",
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    )
    assert source_response.status_code == 201
    source = source_response.json()

    attach_response = client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
            "note": "Promising resort source",
        },
    )
    assert attach_response.status_code == 201
    attached = attach_response.json()
    assert attached["project_id"] == project["project_id"]
    assert attached["source"]["source_id"] == source["source_id"]

    list_response = client.get(f"/api/v1/projects/{project['project_id']}/sources")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed["items"]) == 1
    assert listed["items"][0]["source"]["canonical_url"] == "https://example.com/dive-resort"


def test_duplicate_project_source_returns_409(client: TestClient) -> None:
    project = create_project(client)

    source_response = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "Duplicate source",
            "canonical_url": "https://example.com/duplicate-source",
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    )
    assert source_response.status_code == 201
    source = source_response.json()

    first_attach = client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    )
    assert first_attach.status_code == 201

    second_attach = client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    )
    assert second_attach.status_code == 409
