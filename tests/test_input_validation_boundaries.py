"""Input validation boundary tests — Pydantic constraints at the API edge.

Verifies that FastAPI/Pydantic correctly reject payloads that violate
min_length, max_length, and ge constraints with 422 responses.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

# ---------- helpers ----------------------------------------------------------

def _create_project(client: TestClient) -> dict:
    r = client.post(
        "/api/v1/projects",
        json={
            "title": "Validation Project",
            "short_description": "boundary tests",
            "project_type": "standard",
        },
    )
    assert r.status_code == 201
    return r.json()


def _create_campaign(client: TestClient, project_id: str) -> dict:
    r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns",
        json={
            "title": "Boundary campaign",
            "query_text": "boundary test",
            "campaign_kind": "manual",
            "status": "planned",
        },
    )
    assert r.status_code == 201
    return r.json()


def _create_run(client: TestClient, project_id: str, campaign_id: str) -> dict:
    r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}/runs",
        json={
            "title": "Boundary run",
            "run_kind": "manual",
            "status": "planned",
            "query_text_snapshot": "boundary test",
        },
    )
    assert r.status_code == 201
    return r.json()


# ---------- ProjectCreate constraints ----------------------------------------

def test_project_title_empty_rejected(client: TestClient) -> None:
    r = client.post(
        "/api/v1/projects",
        json={"title": "", "short_description": "x", "project_type": "standard"},
    )
    assert r.status_code == 422


def test_project_title_too_long_rejected(client: TestClient) -> None:
    r = client.post(
        "/api/v1/projects",
        json={"title": "x" * 201, "short_description": "x", "project_type": "standard"},
    )
    assert r.status_code == 422


# ---------- SearchCampaignCreate constraints ---------------------------------

def test_campaign_title_empty_rejected(client: TestClient) -> None:
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns",
        json={"title": "", "query_text": "q", "campaign_kind": "manual", "status": "planned"},
    )
    assert r.status_code == 422


# ---------- SearchRunCreate constraints --------------------------------------

def test_run_title_empty_rejected(client: TestClient) -> None:
    project = _create_project(client)
    camp = _create_campaign(client, project["project_id"])
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/{camp['search_campaign_id']}/runs",
        json={"title": "", "run_kind": "manual", "status": "planned", "query_text_snapshot": "q"},
    )
    assert r.status_code == 422


# ---------- SearchResultCandidateCreate constraints --------------------------

def test_candidate_title_empty_rejected(client: TestClient) -> None:
    project = _create_project(client)
    camp = _create_campaign(client, project["project_id"])
    run = _create_run(client, project["project_id"], camp["search_campaign_id"])
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/"
        f"{camp['search_campaign_id']}/runs/{run['search_run_id']}/result-candidates",
        json={
            "title": "",
            "url": "https://example.com/x",
            "domain": "example.com",
            "rank": 1,
            "disposition": "pending",
        },
    )
    assert r.status_code == 422


def test_candidate_url_empty_rejected(client: TestClient) -> None:
    project = _create_project(client)
    camp = _create_campaign(client, project["project_id"])
    run = _create_run(client, project["project_id"], camp["search_campaign_id"])
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/"
        f"{camp['search_campaign_id']}/runs/{run['search_run_id']}/result-candidates",
        json={
            "title": "Valid title",
            "url": "",
            "domain": "example.com",
            "rank": 1,
            "disposition": "pending",
        },
    )
    assert r.status_code == 422


def test_candidate_rank_zero_rejected(client: TestClient) -> None:
    """ge=1 constraint: rank must be >= 1."""
    project = _create_project(client)
    camp = _create_campaign(client, project["project_id"])
    run = _create_run(client, project["project_id"], camp["search_campaign_id"])
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/"
        f"{camp['search_campaign_id']}/runs/{run['search_run_id']}/result-candidates",
        json={
            "title": "Valid title",
            "url": "https://example.com/x",
            "domain": "example.com",
            "rank": 0,
            "disposition": "pending",
        },
    )
    assert r.status_code == 422


# ---------- ReviewQueueItemCreate constraints --------------------------------

def test_review_item_title_empty_rejected(client: TestClient) -> None:
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": ""},
    )
    assert r.status_code == 422


def test_review_item_title_too_long_rejected(client: TestClient) -> None:
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": "x" * 201},
    )
    assert r.status_code == 422


# ---------- ReviewQueueStatusUpdate constraints ------------------------------

def test_status_update_empty_rejected(client: TestClient) -> None:
    project = _create_project(client)
    r = client.patch(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/any/status",
        json={"status": ""},
    )
    assert r.status_code == 422


# ---------- SourceCreate constraints -----------------------------------------

def test_source_type_empty_rejected(client: TestClient) -> None:
    r = client.post(
        "/api/v1/sources",
        json={
            "source_type": "",
            "title": "Some source",
            "canonical_url": "https://example.com/s",
            "trust_tier": "candidate",
        },
    )
    assert r.status_code == 422


# ---------- ChatTurnCreate / DryRunRequest constraints -----------------------

def test_chat_turn_empty_input_rejected(client: TestClient) -> None:
    """input_text min_length=1."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={"input_text": ""},
    )
    assert r.status_code == 422


def test_chat_turn_input_too_long_rejected(client: TestClient) -> None:
    """input_text max_length=4000."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={"input_text": "x" * 4001},
    )
    assert r.status_code == 422


def test_dry_run_empty_input_rejected(client: TestClient) -> None:
    """DryRunRequest input_text min_length=1."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/openai/projects/{project['project_id']}/dry-run",
        json={"input_text": ""},
    )
    assert r.status_code == 422


# ---------- Handbook constraints ---------------------------------------------

def test_handbook_empty_markdown_rejected(client: TestClient) -> None:
    """handbook_markdown min_length=1."""
    project = _create_project(client)
    r = client.put(
        f"/api/v1/projects/{project['project_id']}/handbook",
        json={"handbook_markdown": ""},
    )
    assert r.status_code == 422
