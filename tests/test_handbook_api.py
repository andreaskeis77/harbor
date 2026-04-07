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
    db_file = tmp_path / "handbook_test.db"
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
            "title": "Handbook Project",
            "short_description": "Research handbook baseline",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()



def test_handbook_empty_then_versioned(client: TestClient) -> None:
    project = create_project(client)
    project_id = project["project_id"]

    empty_response = client.get(f"/api/v1/projects/{project_id}/handbook")
    assert empty_response.status_code == 200
    empty_payload = empty_response.json()
    assert empty_payload["has_handbook"] is False
    assert empty_payload["current"] is None

    first_response = client.put(
        f"/api/v1/projects/{project_id}/handbook",
        json={
            "handbook_markdown": "# Scope\n\nInitial handbook.",
            "change_note": "Initial version",
        },
    )
    assert first_response.status_code == 200
    first_payload = first_response.json()
    assert first_payload["version_number"] == 1

    second_response = client.put(
        f"/api/v1/projects/{project_id}/handbook",
        json={
            "handbook_markdown": "# Scope\n\nUpdated handbook.",
            "change_note": "Second version",
        },
    )
    assert second_response.status_code == 200
    second_payload = second_response.json()
    assert second_payload["version_number"] == 2

    current_response = client.get(f"/api/v1/projects/{project_id}/handbook")
    assert current_response.status_code == 200
    current_payload = current_response.json()
    assert current_payload["has_handbook"] is True
    assert current_payload["current"]["version_number"] == 2
    assert current_payload["current"]["handbook_markdown"] == "# Scope\n\nUpdated handbook."

    versions_response = client.get(f"/api/v1/projects/{project_id}/handbook/versions")
    assert versions_response.status_code == 200
    versions_payload = versions_response.json()
    assert len(versions_payload["items"]) == 2
    assert versions_payload["items"][0]["version_number"] == 2
    assert versions_payload["items"][1]["version_number"] == 1



def test_handbook_404_for_missing_project(client: TestClient) -> None:
    response = client.get("/api/v1/projects/not-found/handbook")
    assert response.status_code == 404
