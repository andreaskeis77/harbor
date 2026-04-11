from __future__ import annotations

from fastapi.testclient import TestClient


def create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Review Queue Project",
            "short_description": "Review queue baseline",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_source(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "Dive source",
            "canonical_url": "https://example.com/review-queue-source",
            "content_type": "text/html",
            "trust_tier": "candidate",
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
            "note": "seed",
        },
    )
    assert response.status_code == 201
    return response.json()


def attach_source(client: TestClient, project_id: str, source_id: str) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/sources",
        json={
            "source_id": source_id,
            "relevance": "high",
            "review_status": "candidate",
            "note": "candidate source",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_list_get_update_review_queue_item(client: TestClient) -> None:
    project = create_project(client)
    source = create_source(client)
    attached = attach_source(client, project["project_id"], source["source_id"])
    campaign = create_campaign(client, project["project_id"])

    create_response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={
            "title": "Review the source",
            "queue_kind": "source_review",
            "status": "open",
            "priority": "high",
            "note": "Needs human review",
            "source_id": source["source_id"],
            "project_source_id": attached["project_source_id"],
            "search_campaign_id": campaign["search_campaign_id"],
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "open"

    list_response = client.get(f"/api/v1/projects/{project['project_id']}/review-queue-items")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed["items"]) == 1

    get_response = client.get(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/{created['review_queue_item_id']}"
    )
    assert get_response.status_code == 200

    patch_response = client.patch(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/{created['review_queue_item_id']}/status",
        json={"status": "in_review", "note": "Started review"},
    )
    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["status"] == "in_review"
    assert patched["note"] == "Started review"


def test_review_queue_404_for_missing_project(client: TestClient) -> None:
    response = client.get("/api/v1/projects/not-found/review-queue-items")
    assert response.status_code == 404
