"""Edge-case tests for review_queue_registry validation paths.

Covers the uncovered validation branches in create_review_queue_item,
update_review_queue_item_status, promote_search_result_candidate_to_review_queue,
and promote_review_queue_item_to_source.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

# ---------- helpers ----------------------------------------------------------

def _create_project(client: TestClient) -> dict:
    r = client.post(
        "/api/v1/projects",
        json={
            "title": "Edge-case project",
            "short_description": "validation edge tests",
            "project_type": "standard",
        },
    )
    assert r.status_code == 201
    return r.json()


def _create_source(client: TestClient) -> dict:
    r = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "Edge source",
            "canonical_url": "https://example.com/edge-source",
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    )
    assert r.status_code == 201
    return r.json()


def _create_campaign(client: TestClient, project_id: str) -> dict:
    r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns",
        json={
            "title": "Edge campaign",
            "query_text": "edge test query",
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
            "title": "Edge run",
            "run_kind": "manual",
            "status": "planned",
            "query_text_snapshot": "edge test query",
        },
    )
    assert r.status_code == 201
    return r.json()


def _create_candidate(
    client: TestClient,
    project_id: str,
    campaign_id: str,
    run_id: str,
    *,
    url: str = "https://example.com/edge-candidate",
) -> dict:
    r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}/runs/{run_id}/result-candidates",
        json={
            "title": "Edge candidate",
            "url": url,
            "domain": "example.com",
            "snippet": "edge snippet",
            "rank": 1,
            "disposition": "pending",
        },
    )
    assert r.status_code == 201
    return r.json()


def _promote_to_review(
    client: TestClient,
    project_id: str,
    campaign_id: str,
    run_id: str,
    candidate_id: str,
) -> dict:
    r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}"
        f"/runs/{run_id}/result-candidates/{candidate_id}/promote-to-review",
        json={},
    )
    assert r.status_code == 201
    return r.json()


# ---------- create_review_queue_item validation (lines 101-141) ---------------

def test_create_review_item_404_missing_project(client: TestClient) -> None:
    """Line 101: project not found."""
    r = client.post(
        "/api/v1/projects/nonexistent/review-queue-items",
        json={"title": "Should fail"},
    )
    assert r.status_code == 404


def test_create_review_item_404_missing_source(client: TestClient) -> None:
    """Line 106: source_id references a non-existent source."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": "Bad source ref", "source_id": "nonexistent-source"},
    )
    assert r.status_code == 404


def test_create_review_item_404_missing_project_source(client: TestClient) -> None:
    """Line 111: project_source_id references a non-existent project source."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": "Bad ps ref", "project_source_id": "nonexistent-ps"},
    )
    assert r.status_code == 404


def test_create_review_item_404_missing_campaign(client: TestClient) -> None:
    """Line 116: search_campaign_id references a non-existent campaign."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": "Bad campaign ref", "search_campaign_id": "nonexistent-camp"},
    )
    assert r.status_code == 404


def test_create_review_item_404_missing_search_run(client: TestClient) -> None:
    """Lines 119-121: search_run_id references a non-existent run."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": "Bad run ref", "search_run_id": "nonexistent-run"},
    )
    assert r.status_code == 404


def test_create_review_item_404_run_campaign_mismatch(client: TestClient) -> None:
    """Lines 122-126: search_run exists but belongs to a different campaign."""
    project = _create_project(client)
    camp_a = _create_campaign(client, project["project_id"])
    camp_b = _create_campaign(client, project["project_id"])
    run_a = _create_run(client, project["project_id"], camp_a["search_campaign_id"])

    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={
            "title": "Run-campaign mismatch",
            "search_campaign_id": camp_b["search_campaign_id"],
            "search_run_id": run_a["search_run_id"],
        },
    )
    assert r.status_code == 404


def test_create_review_item_404_missing_candidate(client: TestClient) -> None:
    """Lines 129-134: search_result_candidate_id references a non-existent candidate."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={
            "title": "Bad candidate ref",
            "search_result_candidate_id": "nonexistent-cand",
        },
    )
    assert r.status_code == 404


def test_create_review_item_404_candidate_campaign_mismatch(
    client: TestClient,
) -> None:
    """Lines 135-139: candidate exists but belongs to a different campaign."""
    project = _create_project(client)
    camp_a = _create_campaign(client, project["project_id"])
    camp_b = _create_campaign(client, project["project_id"])
    run_a = _create_run(client, project["project_id"], camp_a["search_campaign_id"])
    cand = _create_candidate(
        client,
        project["project_id"],
        camp_a["search_campaign_id"],
        run_a["search_run_id"],
    )

    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={
            "title": "Candidate-campaign mismatch",
            "search_campaign_id": camp_b["search_campaign_id"],
            "search_result_candidate_id": cand["search_result_candidate_id"],
        },
    )
    assert r.status_code == 404


def test_create_review_item_404_candidate_run_mismatch(client: TestClient) -> None:
    """Lines 140-141: candidate exists but belongs to a different run."""
    project = _create_project(client)
    camp = _create_campaign(client, project["project_id"])
    run_a = _create_run(client, project["project_id"], camp["search_campaign_id"])
    run_b = _create_run(client, project["project_id"], camp["search_campaign_id"])
    cand = _create_candidate(
        client,
        project["project_id"],
        camp["search_campaign_id"],
        run_a["search_run_id"],
    )

    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={
            "title": "Candidate-run mismatch",
            "search_run_id": run_b["search_run_id"],
            "search_result_candidate_id": cand["search_result_candidate_id"],
        },
    )
    assert r.status_code == 404


# ---------- update_review_queue_item_status (line 218) -----------------------

def test_update_status_404_missing_item(client: TestClient) -> None:
    """Line 218: review queue item not found for status update."""
    project = _create_project(client)
    r = client.patch(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/nonexistent/status",
        json={"status": "closed"},
    )
    assert r.status_code == 404


# ---------- promote_candidate_to_review validation (lines 240, 244, 252) ------

def test_promote_candidate_404_missing_project(client: TestClient) -> None:
    """Line 240: project not found during candidate promotion."""
    r = client.post(
        "/api/v1/projects/nonexistent/search-campaigns/c/runs/r"
        "/result-candidates/x/promote-to-review",
        json={},
    )
    assert r.status_code == 404


def test_promote_candidate_404_missing_campaign(client: TestClient) -> None:
    """Line 244: campaign not found during candidate promotion."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/nonexistent"
        "/runs/r/result-candidates/x/promote-to-review",
        json={},
    )
    assert r.status_code == 404


def test_promote_candidate_404_missing_run(client: TestClient) -> None:
    """Line 252: search run not found during candidate promotion."""
    project = _create_project(client)
    camp = _create_campaign(client, project["project_id"])
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/search-campaigns/"
        f"{camp['search_campaign_id']}/runs/nonexistent"
        "/result-candidates/x/promote-to-review",
        json={},
    )
    assert r.status_code == 404


# ---------- promote_review_item_to_source validation (lines 305-395) ----------

def test_promote_to_source_404_missing_project(client: TestClient) -> None:
    """Line 305: project not found during source promotion."""
    r = client.post(
        "/api/v1/projects/nonexistent/review-queue-items/x/promote-to-source",
        json={},
    )
    assert r.status_code == 404


def test_promote_to_source_404_missing_item(client: TestClient) -> None:
    """Line 309: review queue item not found during source promotion."""
    project = _create_project(client)
    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/nonexistent/promote-to-source",
        json={},
    )
    assert r.status_code == 404


def test_promote_to_source_409_not_candidate_review(client: TestClient) -> None:
    """Lines 311-315: item is not queue_kind=candidate_review — NotPromotableError."""
    project = _create_project(client)
    # Create a review item with queue_kind=source_review (not candidate_review)
    item_r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": "Not a candidate review", "queue_kind": "source_review"},
    )
    assert item_r.status_code == 201
    item = item_r.json()

    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/"
        f"{item['review_queue_item_id']}/promote-to-source",
        json={},
    )
    assert r.status_code == 409


def test_promote_to_source_409_missing_lineage_fields(client: TestClient) -> None:
    """Lines 320-328: candidate_review item but missing campaign/run/candidate IDs."""
    project = _create_project(client)
    # Create item with queue_kind=candidate_review but no campaign/run/candidate
    item_r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": "Missing lineage", "queue_kind": "candidate_review"},
    )
    assert item_r.status_code == 201
    item = item_r.json()

    r = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/"
        f"{item['review_queue_item_id']}/promote-to-source",
        json={},
    )
    assert r.status_code == 409
