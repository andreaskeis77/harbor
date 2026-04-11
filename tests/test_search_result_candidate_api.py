from __future__ import annotations

from fastapi.testclient import TestClient


def create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Candidate Project",
            "short_description": "Search result candidate baseline",
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
            "note": "Seed search campaign",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_run(client: TestClient, project_id: str, search_campaign_id: str) -> dict[str, object]:
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


def test_create_list_get_and_patch_search_result_candidate(
    client: TestClient,
) -> None:
    project = create_project(client)
    campaign = create_campaign(client, project["project_id"])
    search_run = create_run(client, project["project_id"], campaign["search_campaign_id"])

    create_response = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates",
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
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Example Dive Resort"
    assert created["disposition"] == "pending"

    list_response = client.get(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates"
    )
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed["items"]) == 1

    patch_response = client.patch(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates/{created['search_result_candidate_id']}/disposition",
        json={"disposition": "accepted", "note": "promote candidate"},
    )
    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["disposition"] == "accepted"
    assert patched["note"] == "promote candidate"

    get_response = client.get(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/{search_run['search_run_id']}/result-candidates/{created['search_result_candidate_id']}"
    )
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["search_result_candidate_id"] == created["search_result_candidate_id"]
    assert fetched["url"] == "https://example.com/dive-resort"


def test_search_result_candidate_404_for_missing_run(client: TestClient) -> None:
    project = create_project(client)
    campaign = create_campaign(client, project["project_id"])

    response = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{campaign['search_campaign_id']}/runs/not-found/result-candidates",
        json={
            "title": "Example Dive Resort",
            "url": "https://example.com/dive-resort",
        },
    )
    assert response.status_code == 404
