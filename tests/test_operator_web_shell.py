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
    db_file = tmp_path / "operator_web_shell_test.db"
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
            "title": "Operator Web Shell Project",
            "short_description": "Project for operator web shell tests",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_operator_root_redirects_to_projects_page(client: TestClient) -> None:
    response = client.get("/operator", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/operator/projects"


def test_operator_projects_page_contains_shell_and_bootstrap(client: TestClient) -> None:
    response = client.get("/operator/projects")
    assert response.status_code == 200
    assert 'data-operator-shell="projects"' in response.text
    assert 'id="harbor-operator-bootstrap"' in response.text
    assert '"page": "projects"' in response.text
    assert '"apiBase": "/api/v1"' in response.text


def test_operator_project_detail_contains_markers(client: TestClient) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    assert 'data-operator-shell="project-detail"' in response.text
    assert project["project_id"] in response.text
    assert 'data-summary-mount="workflow-summary"' in response.text


def test_operator_project_detail_contains_action_markers(client: TestClient) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    assert 'data-action-status="operator-actions"' in response.text
    assert 'data-operator-action="promote-to-review"' in response.text
    assert 'data-operator-action="promote-to-source"' in response.text
    assert "/promote-to-review" in response.text
    assert "/promote-to-source" in response.text
