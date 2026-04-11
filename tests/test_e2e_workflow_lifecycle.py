"""E2E workflow lifecycle test.

Exercises the full Harbor research workflow in a single test:
  Project → Campaign → Run → Candidate → Promote-to-Review → Promote-to-Source

Verifies state transitions, lineage integrity, and disposition updates
at every step of the pipeline.
"""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_full_research_workflow_lifecycle(client: TestClient) -> None:
    # ---- 1. Create project --------------------------------------------------
    project_r = client.post(
        "/api/v1/projects",
        json={
            "title": "Lifecycle E2E Project",
            "short_description": "full workflow test",
            "project_type": "standard",
        },
    )
    assert project_r.status_code == 201
    project = project_r.json()
    project_id = project["project_id"]
    assert project["title"] == "Lifecycle E2E Project"

    # ---- 2. Create search campaign ------------------------------------------
    campaign_r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns",
        json={
            "title": "E2E discovery campaign",
            "query_text": "best dive resorts house reef",
            "campaign_kind": "manual",
            "status": "planned",
            "note": "seed campaign for lifecycle test",
        },
    )
    assert campaign_r.status_code == 201
    campaign = campaign_r.json()
    campaign_id = campaign["search_campaign_id"]
    assert campaign["project_id"] == project_id

    # ---- 3. Create search run -----------------------------------------------
    run_r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}/runs",
        json={
            "title": "E2E run 1",
            "run_kind": "manual",
            "status": "planned",
            "query_text_snapshot": "best dive resorts house reef",
            "note": "first manual run",
        },
    )
    assert run_r.status_code == 201
    run = run_r.json()
    run_id = run["search_run_id"]
    assert run["search_campaign_id"] == campaign_id

    # ---- 4. Create search result candidates ---------------------------------
    cand1_r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}"
        f"/runs/{run_id}/result-candidates",
        json={
            "title": "Coral Bay Dive Resort",
            "url": "https://coralbay.example.com",
            "domain": "coralbay.example.com",
            "snippet": "Pristine house reef with 30+ dive sites.",
            "rank": 1,
            "disposition": "pending",
            "note": "top candidate",
        },
    )
    assert cand1_r.status_code == 201
    cand1 = cand1_r.json()
    cand1_id = cand1["search_result_candidate_id"]
    assert cand1["disposition"] == "pending"

    cand2_r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}"
        f"/runs/{run_id}/result-candidates",
        json={
            "title": "Reef Haven Resort",
            "url": "https://reefhaven.example.com",
            "domain": "reefhaven.example.com",
            "snippet": "Small boutique resort with excellent reef access.",
            "rank": 2,
            "disposition": "pending",
        },
    )
    assert cand2_r.status_code == 201

    # Verify list returns both candidates
    list_r = client.get(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}"
        f"/runs/{run_id}/result-candidates",
    )
    assert list_r.status_code == 200
    assert len(list_r.json()["items"]) == 2

    # ---- 5. Promote candidate 1 to review queue -----------------------------
    promote_review_r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}"
        f"/runs/{run_id}/result-candidates/{cand1_id}/promote-to-review",
        json={"note": "looks promising, send to review"},
    )
    assert promote_review_r.status_code == 201
    review_item = promote_review_r.json()
    review_item_id = review_item["review_queue_item_id"]
    assert review_item["queue_kind"] == "candidate_review"
    assert review_item["status"] == "open"
    assert review_item["search_campaign_id"] == campaign_id
    assert review_item["search_run_id"] == run_id
    assert review_item["search_result_candidate_id"] == cand1_id

    # Verify candidate disposition changed to "promoted"
    cand1_check = client.get(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}"
        f"/runs/{run_id}/result-candidates/{cand1_id}",
    )
    assert cand1_check.status_code == 200
    assert cand1_check.json()["disposition"] == "promoted"

    # Verify duplicate promotion is rejected
    dup_r = client.post(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}"
        f"/runs/{run_id}/result-candidates/{cand1_id}/promote-to-review",
        json={},
    )
    assert dup_r.status_code == 409

    # ---- 6. Update review status --------------------------------------------
    status_r = client.patch(
        f"/api/v1/projects/{project_id}/review-queue-items/{review_item_id}/status",
        json={"status": "in_review", "note": "Operator reviewing now"},
    )
    assert status_r.status_code == 200
    assert status_r.json()["status"] == "in_review"

    # ---- 7. Promote review item to source -----------------------------------
    promote_source_r = client.post(
        f"/api/v1/projects/{project_id}/review-queue-items/{review_item_id}"
        "/promote-to-source",
        json={
            "source_type": "web_page",
            "content_type": "text/html",
            "trust_tier": "verified",
            "relevance": "high",
            "review_status": "accepted",
            "note": "Verified house reef resort — accepted into project sources",
        },
    )
    assert promote_source_r.status_code == 201
    promoted = promote_source_r.json()
    assert promoted["status"] == "completed"
    assert promoted["source_id"] is not None
    assert promoted["project_source_id"] is not None

    # Verify candidate disposition is now "accepted"
    cand1_final = client.get(
        f"/api/v1/projects/{project_id}/search-campaigns/{campaign_id}"
        f"/runs/{run_id}/result-candidates/{cand1_id}",
    )
    assert cand1_final.status_code == 200
    assert cand1_final.json()["disposition"] == "accepted"

    # ---- 8. Verify project sources ------------------------------------------
    sources_r = client.get(f"/api/v1/projects/{project_id}/sources")
    assert sources_r.status_code == 200
    sources = sources_r.json()
    assert len(sources["items"]) == 1
    ps = sources["items"][0]
    assert ps["source"]["canonical_url"] == "https://coralbay.example.com"
    assert ps["source"]["trust_tier"] == "verified"
    assert ps["relevance"] == "high"
    assert ps["review_status"] == "accepted"

    # ---- 9. Verify duplicate source promotion is rejected -------------------
    dup_source_r = client.post(
        f"/api/v1/projects/{project_id}/review-queue-items/{review_item_id}"
        "/promote-to-source",
        json={},
    )
    assert dup_source_r.status_code == 409

    # ---- 10. Verify review queue final state --------------------------------
    queue_r = client.get(f"/api/v1/projects/{project_id}/review-queue-items")
    assert queue_r.status_code == 200
    queue_items = queue_r.json()["items"]
    assert len(queue_items) == 1
    assert queue_items[0]["status"] == "completed"

    # ---- 11. Verify workflow summary has lineage ----------------------------
    summary_r = client.get(f"/api/v1/projects/{project_id}/workflow-summary")
    assert summary_r.status_code == 200
    summary = summary_r.json()
    assert summary["project_id"] == project_id
    counts = summary["counts"]
    assert counts["search_campaign_count"] >= 1
    assert counts["search_run_count"] >= 1
    assert counts["search_result_candidate_count"] >= 2
    assert counts["review_queue_item_count"] >= 1
    assert counts["review_queue_completed_count"] >= 1
    assert counts["project_source_count"] >= 1
    assert counts["candidate_accepted_count"] >= 1
    # Lineage should trace the promoted candidate
    assert len(summary["lineage_items"]) >= 1
    promoted_lineage = [
        li for li in summary["lineage_items"]
        if li["search_result_candidate_id"] == cand1_id
    ]
    assert len(promoted_lineage) == 1
    lineage = promoted_lineage[0]
    assert lineage["candidate_disposition"] == "accepted"
    assert lineage["source_id"] is not None
    assert lineage["project_source_id"] is not None
