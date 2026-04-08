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
    db_file = tmp_path / "review_queue_source_promotion_test.db"
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
            "title": "Review Queue Source Promotion Project",
            "short_description": "Promote queue item to source",
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
            "note": "Seed campaign",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_run(
    client: TestClient,
    project_id: str,
    search_campaign_id: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs",
        json={
            "title": "Run 1",
            "run_kind": "manual",
            "status": "planned",
            "query_text_snapshot": "house reef dive resort",
            "note": "first run",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_candidate(
    client: TestClient,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates",
        json={
            "title": "Example Dive Resort",
            "url": "https://example.com/dive-resort",
            "domain": "example.com",
            "snippet": "Direct house reef and beginner-friendly diving.",
            "rank": 1,
            "disposition": "pending",
            "note": "first candidate",
        },
    )
    assert response.status_code == 201
    return response.json()


def promote_candidate_to_review(
    client: TestClient,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    search_result_candidate_id: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates/{search_result_candidate_id}/promote-to-review",
        json={"note": "send to review queue"},
    )
    assert response.status_code == 201
    return response.json()


def test_promote_review_queue_item_to_source(client: TestClient) -> None:
    project = create_project(client)
    campaign = create_campaign(client, project["project_id"])
    search_run = create_run(client, project["project_id"], campaign["search_campaign_id"])
    candidate = create_candidate(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        search_run["search_run_id"],
    )
    review_item = promote_candidate_to_review(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        search_run["search_run_id"],
        candidate["search_result_candidate_id"],
    )

    promote_response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/{review_item['review_queue_item_id']}/promote-to-source",
        json={"note": "accepted into project sources"},
    )
    assert promote_response.status_code == 201
    promoted = promote_response.json()
    assert promoted["status"] == "completed"
    assert promoted["source_id"] is not None
    assert promoted["project_source_id"] is not None

    project_sources_response = client.get(f"/api/v1/projects/{project['project_id']}/sources")
    assert project_sources_response.status_code == 200
    project_sources = project_sources_response.json()
    assert len(project_sources["items"]) == 1
    assert (
        project_sources["items"][0]["source"]["canonical_url"] == "https://example.com/dive-resort"
    )
    assert project_sources["items"][0]["review_status"] == "accepted"

    candidate_response = client.get(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates/{candidate['search_result_candidate_id']}"
    )
    assert candidate_response.status_code == 200
    fetched_candidate = candidate_response.json()
    assert fetched_candidate["disposition"] == "accepted"


def test_promote_review_queue_item_to_source_twice_returns_409(
    client: TestClient,
) -> None:
    project = create_project(client)
    campaign = create_campaign(client, project["project_id"])
    search_run = create_run(client, project["project_id"], campaign["search_campaign_id"])
    candidate = create_candidate(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        search_run["search_run_id"],
    )
    review_item = promote_candidate_to_review(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        search_run["search_run_id"],
        candidate["search_result_candidate_id"],
    )

    first_response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/{review_item['review_queue_item_id']}/promote-to-source",
        json={"note": "accepted into project sources"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/{review_item['review_queue_item_id']}/promote-to-source",
        json={"note": "accepted into project sources"},
    )
    assert second_response.status_code == 409


def test_promote_second_review_queue_item_for_same_url_returns_409(
    client: TestClient,
) -> None:
    project = create_project(client)
    campaign = create_campaign(client, project["project_id"])

    first_run = create_run(client, project["project_id"], campaign["search_campaign_id"])
    first_candidate = create_candidate(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        first_run["search_run_id"],
    )
    first_review_item = promote_candidate_to_review(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        first_run["search_run_id"],
        first_candidate["search_result_candidate_id"],
    )

    second_run = create_run(client, project["project_id"], campaign["search_campaign_id"])
    second_candidate = create_candidate(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        second_run["search_run_id"],
    )
    second_review_item = promote_candidate_to_review(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        second_run["search_run_id"],
        second_candidate["search_result_candidate_id"],
    )

    first_response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/{first_review_item['review_queue_item_id']}/promote-to-source",
        json={"note": "accepted into project sources"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/{second_review_item['review_queue_item_id']}/promote-to-source",
        json={"note": "accepted into project sources"},
    )
    assert second_response.status_code == 409
