from __future__ import annotations

from fastapi.testclient import TestClient


def create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Campaign Project",
            "short_description": "Search campaign baseline",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_list_get_search_campaign(client: TestClient) -> None:
    project = create_project(client)
    project_id = project["project_id"]

    create_response = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns",
        json={
            "title": "Initial discovery",
            "query_text": "house reef dive resort",
            "campaign_kind": "manual",
            "status": "planned",
            "note": "Seed search campaign",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Initial discovery"

    list_response = client.get(f"/api/v1/projects/{project_id}/search-campaigns")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed["items"]) == 1
    assert listed["items"][0]["search_campaign_id"] == created["search_campaign_id"]

    get_response = client.get(
        f"/api/v1/projects/{project_id}/search-campaigns/{created['search_campaign_id']}"
    )
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["search_campaign_id"] == created["search_campaign_id"]
    assert fetched["query_text"] == "house reef dive resort"


def test_search_campaign_404_for_missing_project(client: TestClient) -> None:
    response = client.get("/api/v1/projects/not-found/search-campaigns")
    assert response.status_code == 404
