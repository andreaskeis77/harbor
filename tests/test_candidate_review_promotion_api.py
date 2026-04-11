from __future__ import annotations

from fastapi.testclient import TestClient


def create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Candidate Review Promotion Project",
            "short_description": "Promote candidate to review queue",
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


def test_promote_candidate_to_review_queue(client: TestClient) -> None:
    project = create_project(client)
    campaign = create_campaign(client, project["project_id"])
    search_run = create_run(client, project["project_id"], campaign["search_campaign_id"])
    candidate = create_candidate(
        client,
        project["project_id"],
        campaign["search_campaign_id"],
        search_run["search_run_id"],
    )

    promote_response = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates/{candidate['search_result_candidate_id']}/promote-to-review",
        json={"note": "send to review queue"},
    )
    assert promote_response.status_code == 201
    promoted = promote_response.json()
    assert promoted["queue_kind"] == "candidate_review"
    assert promoted["status"] == "open"
    assert promoted["priority"] == "normal"
    assert promoted["search_campaign_id"] == campaign["search_campaign_id"]
    assert promoted["search_run_id"] == search_run["search_run_id"]
    assert promoted["search_result_candidate_id"] == candidate["search_result_candidate_id"]

    queue_response = client.get(f"/api/v1/projects/{project['project_id']}/review-queue-items")
    assert queue_response.status_code == 200
    queue_items = queue_response.json()
    assert len(queue_items["items"]) == 1

    candidate_response = client.get(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates/{candidate['search_result_candidate_id']}"
    )
    assert candidate_response.status_code == 200
    fetched_candidate = candidate_response.json()
    assert fetched_candidate["disposition"] == "promoted"


def test_promote_candidate_404_for_missing_candidate(client: TestClient) -> None:
    project = create_project(client)
    campaign = create_campaign(client, project["project_id"])
    search_run = create_run(client, project["project_id"], campaign["search_campaign_id"])

    response = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates/not-found/promote-to-review",
        json={"note": "send to review queue"},
    )
    assert response.status_code == 404


def test_promote_candidate_to_review_queue_twice_returns_409(
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

    first_response = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates/{candidate['search_result_candidate_id']}/promote-to-review",
        json={"note": "send to review queue"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates/{candidate['search_result_candidate_id']}/promote-to-review",
        json={"note": "send to review queue"},
    )
    assert second_response.status_code == 409
