from __future__ import annotations

from fastapi.testclient import TestClient


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


def _attach_candidate_source(client: TestClient, project_id: str) -> dict[str, object]:
    source_response = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "Review workflow source",
            "canonical_url": "https://example.com/review-workflow",
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    )
    assert source_response.status_code == 201
    source = source_response.json()

    attach_response = client.post(
        f"/api/v1/projects/{project_id}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    )
    assert attach_response.status_code == 201
    return attach_response.json()


def test_update_project_source_review_status_accepts_candidate(client: TestClient) -> None:
    project = create_project(client)
    attached = _attach_candidate_source(client, project["project_id"])

    response = client.patch(
        f"/api/v1/projects/{project['project_id']}/sources/"
        f"{attached['project_source_id']}/review-status",
        json={"review_status": "accepted", "note": "Verified"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["review_status"] == "accepted"
    assert body["note"] == "Verified"
    assert body["project_source_id"] == attached["project_source_id"]


def test_update_project_source_review_status_rejects_invalid_status(
    client: TestClient,
) -> None:
    project = create_project(client)
    attached = _attach_candidate_source(client, project["project_id"])

    response = client.patch(
        f"/api/v1/projects/{project['project_id']}/sources/"
        f"{attached['project_source_id']}/review-status",
        json={"review_status": "approved"},
    )
    assert response.status_code == 422


def test_update_project_source_review_status_missing_project_returns_404(
    client: TestClient,
) -> None:
    project = create_project(client)
    attached = _attach_candidate_source(client, project["project_id"])

    response = client.patch(
        f"/api/v1/projects/does-not-exist/sources/"
        f"{attached['project_source_id']}/review-status",
        json={"review_status": "accepted"},
    )
    assert response.status_code == 404


def test_update_project_source_review_status_missing_project_source_returns_404(
    client: TestClient,
) -> None:
    project = create_project(client)

    response = client.patch(
        f"/api/v1/projects/{project['project_id']}/sources/"
        "missing-project-source/review-status",
        json={"review_status": "accepted"},
    )
    assert response.status_code == 404


def test_update_project_source_review_status_rejects_cross_project(
    client: TestClient,
) -> None:
    project_a = create_project(client)
    project_b_response = client.post(
        "/api/v1/projects",
        json={
            "title": "Other project",
            "short_description": "Second project",
            "project_type": "standard",
        },
    )
    assert project_b_response.status_code == 201
    project_b = project_b_response.json()
    attached = _attach_candidate_source(client, project_a["project_id"])

    response = client.patch(
        f"/api/v1/projects/{project_b['project_id']}/sources/"
        f"{attached['project_source_id']}/review-status",
        json={"review_status": "accepted"},
    )
    assert response.status_code == 404


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
