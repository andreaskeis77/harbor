from __future__ import annotations

import json

from fastapi.testclient import TestClient


def _create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Snapshot Summary Project",
            "short_description": "Project for snapshot tests",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_snapshot_summary_records_succeeded_automation_task(
    client: TestClient,
) -> None:
    project = _create_project(client)

    response = client.post(
        f"/api/v1/projects/{project['project_id']}/snapshot-summary",
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["project_id"] == project["project_id"]
    assert "automation_task_id" in payload
    assert payload["counts"]["search_campaign_count"] == 0
    assert payload["counts"]["project_source_count"] == 0

    tasks_response = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks"
    )
    assert tasks_response.status_code == 200
    items = tasks_response.json()["items"]
    assert len(items) == 1

    task = items[0]
    assert task["task_kind"] == "snapshot_workflow_summary"
    assert task["trigger_source"] == "manual"
    assert task["status"] == "succeeded"
    assert task["started_at"] is not None
    assert task["completed_at"] is not None
    assert task["error_message"] is None

    # result_summary is compact JSON of the counts payload — parse to prove it.
    parsed = json.loads(task["result_summary"])
    assert parsed["search_campaign_count"] == 0
    assert parsed["project_source_count"] == 0
    assert parsed["review_queue_item_count"] == 0


def test_snapshot_summary_unknown_project_returns_404_without_task(
    client: TestClient,
) -> None:
    response = client.post("/api/v1/projects/nonexistent/snapshot-summary")
    assert response.status_code == 404

    # 404 happens before the observer starts — no orphan task row.
    missing_detail = client.get("/api/v1/automation-tasks/nonexistent-task")
    assert missing_detail.status_code == 404


def test_snapshot_summary_backend_failure_records_failed_task(
    client: TestClient,
    monkeypatch,
) -> None:
    project = _create_project(client)

    from harbor.api.routes import workflow_summary as wf_route
    from harbor.exceptions import InvalidPayloadError

    def _explode(*args, **kwargs):
        raise InvalidPayloadError("WorkflowSummary", "simulated compute failure")

    monkeypatch.setattr(wf_route, "get_workflow_summary", _explode)

    response = client.post(
        f"/api/v1/projects/{project['project_id']}/snapshot-summary",
    )
    assert response.status_code == 422

    tasks_response = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks"
    )
    assert tasks_response.status_code == 200
    items = tasks_response.json()["items"]
    assert len(items) == 1
    task = items[0]
    assert task["status"] == "failed"
    assert task["task_kind"] == "snapshot_workflow_summary"
    assert "simulated compute failure" in (task["error_message"] or "")
    assert task["completed_at"] is not None
