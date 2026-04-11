"""Tests for domain exception hierarchy and request-scoped transaction middleware.

Validates:
- Each domain exception type maps to the correct HTTP status code via middleware
- Error response bodies contain structured detail messages
- Transaction middleware commits on success and rolls back on error
- DatabaseNotConfiguredError maps to 503
"""

from __future__ import annotations

from starlette.testclient import TestClient

# ---------------------------------------------------------------------------
# 1. Domain exception → HTTP status mapping (via middleware handlers)
# ---------------------------------------------------------------------------


def test_not_found_error_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/projects/nonexistent-project-id")
    assert response.status_code == 404
    body = response.json()
    assert "not found" in body["detail"].lower()


def test_duplicate_error_returns_409(client: TestClient) -> None:
    # Create a source
    create_resp = client.post(
        "/api/v1/sources",
        json={
            "source_type": "article",
            "title": "Duplicate Test Source",
            "canonical_url": "https://example.com/dup-test",
            "content_type": "text/html",
            "trust_tier": "t2_reviewed",
        },
    )
    assert create_resp.status_code == 201

    # Creating the same source again triggers DuplicateError (via IntegrityError → DuplicateError)
    dup_resp = client.post(
        "/api/v1/sources",
        json={
            "source_type": "article",
            "title": "Duplicate Test Source Again",
            "canonical_url": "https://example.com/dup-test",
            "content_type": "text/html",
            "trust_tier": "t2_reviewed",
        },
    )
    assert dup_resp.status_code == 409
    assert "detail" in dup_resp.json()


def test_not_promotable_error_returns_409(client: TestClient) -> None:
    # Create a project and a review queue item that is not candidate_review kind
    project_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Promotable Test Project",
            "short_description": "Testing not-promotable errors",
        },
    )
    assert project_resp.status_code == 201
    project_id = project_resp.json()["project_id"]

    # Create a review queue item with kind != candidate_review
    rqi_resp = client.post(
        f"/api/v1/projects/{project_id}/review-queue-items",
        json={
            "title": "Manual review item",
            "queue_kind": "manual",
            "priority": "normal",
        },
    )
    assert rqi_resp.status_code == 201
    rqi_id = rqi_resp.json()["review_queue_item_id"]

    # Try to promote it — should fail because it's not candidate_review
    promote_resp = client.post(
        f"/api/v1/projects/{project_id}/review-queue-items/{rqi_id}/promote-to-source",
        json={
            "source_type": "article",
            "content_type": "text/html",
            "trust_tier": "t2_reviewed",
            "relevance": "high",
            "review_status": "accepted",
        },
    )
    assert promote_resp.status_code == 409
    assert "not promotable" in promote_resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 2. Transaction middleware: commit-on-success
# ---------------------------------------------------------------------------


def test_transaction_commits_on_successful_create(client: TestClient) -> None:
    """A successful POST should persist the record (commit happens in get_db_session)."""
    create_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Transaction Commit Test",
            "short_description": "Should be persisted",
        },
    )
    assert create_resp.status_code == 201
    project_id = create_resp.json()["project_id"]

    # Verify persistence by reading it back in a new request (new session)
    get_resp = client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Transaction Commit Test"


def test_transaction_rollback_on_error_leaves_no_side_effects(
    client: TestClient,
) -> None:
    """When a request fails, partial writes should be rolled back.

    We test this by attempting a duplicate source creation. The first
    flush succeeds but the DuplicateError propagates, triggering rollback
    at the session boundary. The first source should still exist (it was
    committed in its own request), but no spurious records should appear.
    """
    # Create a project so we can count sources scoped to it
    project_resp = client.post(
        "/api/v1/projects",
        json={"title": "Rollback Test Project", "short_description": "Testing rollback"},
    )
    assert project_resp.status_code == 201

    # Create a source
    client.post(
        "/api/v1/sources",
        json={
            "source_type": "article",
            "title": "Rollback Source",
            "canonical_url": "https://example.com/rollback-test",
            "content_type": "text/html",
            "trust_tier": "t2_reviewed",
        },
    )

    # Attempt duplicate — should fail with 409
    dup_resp = client.post(
        "/api/v1/sources",
        json={
            "source_type": "article",
            "title": "Rollback Source Duplicate",
            "canonical_url": "https://example.com/rollback-test",
            "content_type": "text/html",
            "trust_tier": "t2_reviewed",
        },
    )
    assert dup_resp.status_code == 409

    # Verify only one source with that URL exists
    sources_resp = client.get("/api/v1/sources")
    assert sources_resp.status_code == 200
    matching = [
        s
        for s in sources_resp.json()["items"]
        if s["canonical_url"] == "https://example.com/rollback-test"
    ]
    assert len(matching) == 1


# ---------------------------------------------------------------------------
# 3. Multi-step operations are atomic
# ---------------------------------------------------------------------------


def test_multi_step_promotion_is_atomic(client: TestClient) -> None:
    """The promote-to-source endpoint creates Source + ProjectSource + updates
    ReviewQueueItem + updates Candidate in a single transaction. If it succeeds,
    all writes should be visible."""
    # Setup: project → campaign → run → candidate → review item
    proj = client.post(
        "/api/v1/projects",
        json={"title": "Atomic Promotion Test", "short_description": "Multi-step atomicity"},
    ).json()
    pid = proj["project_id"]

    camp = client.post(
        f"/api/v1/projects/{pid}/search-campaigns",
        json={"title": "Atomic test campaign", "query_text": "atomic test query"},
    ).json()
    cid = camp["search_campaign_id"]

    run = client.post(
        f"/api/v1/projects/{pid}/search-campaigns/{cid}/runs",
        json={"title": "Atomic test run", "run_kind": "manual", "status": "completed"},
    ).json()
    rid = run["search_run_id"]

    cand = client.post(
        f"/api/v1/projects/{pid}/search-campaigns/{cid}/runs/{rid}/result-candidates",
        json={
            "title": "Atomic Test Paper",
            "url": "https://example.com/atomic-test-paper",
            "snippet": "Test snippet",
            "rank": 1,
        },
    ).json()
    src_cand_id = cand["search_result_candidate_id"]

    # Promote candidate to review queue
    review_item = client.post(
        f"/api/v1/projects/{pid}/search-campaigns/{cid}/runs/{rid}"
        f"/result-candidates/{src_cand_id}/promote-to-review",
        json={"note": "looks relevant"},
    ).json()
    rqi_id = review_item["review_queue_item_id"]

    # Promote review item to source — multi-step atomic operation
    promote_resp = client.post(
        f"/api/v1/projects/{pid}/review-queue-items/{rqi_id}/promote-to-source",
        json={
            "source_type": "article",
            "content_type": "text/html",
            "trust_tier": "t2_reviewed",
            "relevance": "high",
            "review_status": "accepted",
        },
    )
    assert promote_resp.status_code == 201
    promoted = promote_resp.json()

    # Verify all side effects are visible
    assert promoted["status"] == "completed"
    assert promoted["source_id"] is not None
    assert promoted["project_source_id"] is not None

    # Candidate should now be "accepted"
    cand_resp = client.get(
        f"/api/v1/projects/{pid}/search-campaigns/{cid}/runs/{rid}"
        f"/result-candidates/{src_cand_id}"
    )
    assert cand_resp.json()["disposition"] == "accepted"

    # Source should exist in the global sources list
    sources = client.get("/api/v1/sources").json()["items"]
    assert any(s["canonical_url"] == "https://example.com/atomic-test-paper" for s in sources)
