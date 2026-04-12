from __future__ import annotations

from fastapi.testclient import TestClient


def _create_project(client: TestClient, title: str) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": title,
            "short_description": "Pending actions test project",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_review_item(
    client: TestClient,
    project_id: str,
    *,
    title: str,
    status: str = "open",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/review-queue-items",
        json={
            "title": title,
            "queue_kind": "source_review",
            "status": status,
            "priority": "normal",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_pending_actions_empty_when_no_items(client: TestClient) -> None:
    response = client.get("/api/v1/pending-actions")
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_pending_actions_aggregates_open_items_across_projects(
    client: TestClient,
) -> None:
    project_a = _create_project(client, "Alpha Project")
    project_b = _create_project(client, "Bravo Project")

    open_a = _create_review_item(
        client, project_a["project_id"], title="Review alpha source", status="open"
    )
    _create_review_item(
        client,
        project_a["project_id"],
        title="Already resolved alpha item",
        status="resolved",
    )
    open_b = _create_review_item(
        client, project_b["project_id"], title="Review bravo source", status="open"
    )

    response = client.get("/api/v1/pending-actions")
    assert response.status_code == 200
    items = response.json()["items"]

    # Only the two open items are returned; the resolved one is excluded.
    returned_ids = {item["review_queue_item_id"] for item in items}
    assert returned_ids == {
        open_a["review_queue_item_id"],
        open_b["review_queue_item_id"],
    }

    for item in items:
        assert item["status"] == "open"
        assert item["project_title"] in {"Alpha Project", "Bravo Project"}
        assert item["project_id"] in {
            project_a["project_id"],
            project_b["project_id"],
        }


def test_pending_actions_excludes_non_open_statuses(client: TestClient) -> None:
    project = _create_project(client, "Solo Project")
    _create_review_item(
        client, project["project_id"], title="Closed item", status="resolved"
    )
    _create_review_item(
        client, project["project_id"], title="In-review item", status="in_review"
    )

    response = client.get("/api/v1/pending-actions")
    assert response.status_code == 200
    assert response.json()["items"] == []
