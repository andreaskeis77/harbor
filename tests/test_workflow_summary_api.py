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
    db_file = tmp_path / "workflow_summary_test.db"
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
            "title": "Workflow Summary Project",
            "short_description": "Project for workflow summary",
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
    title: str,
    note: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs",
        json={
            "title": title,
            "run_kind": "manual",
            "status": "planned",
            "query_text_snapshot": "house reef dive resort",
            "note": note,
        },
    )
    assert response.status_code == 201
    return response.json()


def create_candidate(
    client: TestClient,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    title: str,
    url: str,
    rank: int,
    note: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/"
        f"{search_run_id}/result-candidates",
        json={
            "title": title,
            "url": url,
            "domain": "example.com",
            "snippet": "Direct house reef and beginner-friendly diving.",
            "rank": rank,
            "disposition": "pending",
            "note": note,
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
        f"/api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/"
        f"{search_run_id}/result-candidates/{search_result_candidate_id}/promote-to-review",
        json={"note": "send to review queue"},
    )
    assert response.status_code == 201
    return response.json()


def promote_review_item_to_source(
    client: TestClient,
    project_id: str,
    review_queue_item_id: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/review-queue-items/{review_queue_item_id}/"
        "promote-to-source",
        json={"note": "accepted into project sources"},
    )
    assert response.status_code == 201
    return response.json()


def test_workflow_summary_counts_and_lineage(client: TestClient) -> None:
    project = create_project(client)
    campaign = create_campaign(client, project["project_id"])

    first_run = create_run(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        "Run 1",
        "first run",
    )
    first_candidate = create_candidate(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        first_run["search_run_id"],
        "Example Dive Resort A",
        "https://example.com/dive-resort-a",
        1,
        "first candidate",
    )
    first_review_item = promote_candidate_to_review(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        first_run["search_run_id"],
        first_candidate["search_result_candidate_id"],
    )
    promote_review_item_to_source(
        client,
        project["project_id"],
        first_review_item["review_queue_item_id"],
    )

    second_run = create_run(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        "Run 2",
        "second run",
    )
    second_candidate = create_candidate(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        second_run["search_run_id"],
        "Example Dive Resort B",
        "https://example.com/dive-resort-b",
        1,
        "second candidate",
    )
    second_review_item = promote_candidate_to_review(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        second_run["search_run_id"],
        second_candidate["search_result_candidate_id"],
    )

    third_candidate = create_candidate(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        second_run["search_run_id"],
        "Example Dive Resort C",
        "https://example.com/dive-resort-c",
        2,
        "third candidate",
    )

    response = client.get(f"/api/v1/projects/{project['project_id']}/workflow-summary")
    assert response.status_code == 200
    summary = response.json()

    assert summary["project_id"] == project["project_id"]
    assert summary["project_title"] == "Workflow Summary Project"
    assert summary["counts"] == {
        "search_campaign_count": 1,
        "search_run_count": 2,
        "search_result_candidate_count": 3,
        "candidate_pending_count": 1,
        "candidate_promoted_count": 1,
        "candidate_accepted_count": 1,
        "review_queue_item_count": 2,
        "review_queue_open_count": 1,
        "review_queue_in_review_count": 0,
        "review_queue_completed_count": 1,
        "project_source_count": 1,
    }

    lineage_by_candidate = {
        item["search_result_candidate_id"]: item for item in summary["lineage_items"]
    }
    assert len(lineage_by_candidate) == 3

    first_item = lineage_by_candidate[first_candidate["search_result_candidate_id"]]
    assert first_item["candidate_disposition"] == "accepted"
    assert first_item["review_queue_item_id"] == first_review_item["review_queue_item_id"]
    assert first_item["review_queue_status"] == "completed"
    assert first_item["source_id"] is not None
    assert first_item["project_source_id"] is not None
    assert first_item["project_source_review_status"] == "accepted"

    second_item = lineage_by_candidate[second_candidate["search_result_candidate_id"]]
    assert second_item["candidate_disposition"] == "promoted"
    assert second_item["review_queue_item_id"] == second_review_item["review_queue_item_id"]
    assert second_item["review_queue_status"] == "open"
    assert second_item["source_id"] is None
    assert second_item["project_source_id"] is None
    assert second_item["project_source_review_status"] is None

    third_item = lineage_by_candidate[third_candidate["search_result_candidate_id"]]
    assert third_item["candidate_disposition"] == "pending"
    assert third_item["review_queue_item_id"] is None
    assert third_item["review_queue_status"] is None
    assert third_item["source_id"] is None
    assert third_item["project_source_id"] is None
    assert third_item["project_source_review_status"] is None


def test_workflow_summary_404_for_missing_project(client: TestClient) -> None:
    response = client.get("/api/v1/projects/not-found/workflow-summary")
    assert response.status_code == 404
