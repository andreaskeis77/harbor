from __future__ import annotations

from fastapi.testclient import TestClient


def _create_project(client: TestClient) -> dict:
    return client.post(
        "/api/v1/projects",
        json={
            "title": "Bulk",
            "short_description": "b",
            "project_type": "standard",
        },
    ).json()


def _create_item(client: TestClient, project_id: str, title: str) -> dict:
    return client.post(
        f"/api/v1/projects/{project_id}/review-queue-items",
        json={"title": title},
    ).json()


def test_bulk_status_updates_multiple_items(client: TestClient) -> None:
    project = _create_project(client)
    ids = [
        _create_item(client, project["project_id"], f"rq-{i}")["review_queue_item_id"]
        for i in range(3)
    ]

    response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/bulk-status",
        json={
            "review_queue_item_ids": ids,
            "status": "rejected",
            "note": "batch reject",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["updated"]) == 3
    assert body["failed"] == []
    assert {u["status"] for u in body["updated"]} == {"rejected"}
    assert all(u["note"] == "batch reject" for u in body["updated"])


def test_bulk_status_reports_unknown_items_without_blocking_rest(
    client: TestClient,
) -> None:
    project = _create_project(client)
    good_id = _create_item(client, project["project_id"], "rq-good")[
        "review_queue_item_id"
    ]

    response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/bulk-status",
        json={
            "review_queue_item_ids": [good_id, "nope-1", "nope-2"],
            "status": "archived",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert [u["review_queue_item_id"] for u in body["updated"]] == [good_id]
    failed_ids = {f["review_queue_item_id"]: f["error"] for f in body["failed"]}
    assert failed_ids == {"nope-1": "not_found", "nope-2": "not_found"}


def test_bulk_status_rejects_empty_id_list(client: TestClient) -> None:
    project = _create_project(client)
    response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/bulk-status",
        json={"review_queue_item_ids": [], "status": "rejected"},
    )
    assert response.status_code == 422


def test_bulk_status_unknown_project_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/projects/nope/review-queue-items/bulk-status",
        json={"review_queue_item_ids": ["x"], "status": "rejected"},
    )
    assert response.status_code == 404


def test_bulk_status_deduplicates_input_ids(client: TestClient) -> None:
    project = _create_project(client)
    rid = _create_item(client, project["project_id"], "rq-dup")[
        "review_queue_item_id"
    ]
    response = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/bulk-status",
        json={
            "review_queue_item_ids": [rid, rid, rid],
            "status": "rejected",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["updated"]) == 1
    assert body["failed"] == []
