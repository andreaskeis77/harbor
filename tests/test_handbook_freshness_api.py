from __future__ import annotations

import json

from fastapi.testclient import TestClient


def _create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Handbook Freshness Project",
            "short_description": "Project for handbook freshness tests",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_handbook_freshness_records_succeeded_automation_task(
    client: TestClient,
) -> None:
    project = _create_project(client)

    response = client.post(
        f"/api/v1/projects/{project['project_id']}/check-handbook-freshness",
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["project_id"] == project["project_id"]
    assert "automation_task_id" in payload
    counts = payload["counts"]
    assert counts["handbook_version_count"] == 0
    assert counts["days_since_last_handbook_version"] is None
    assert counts["candidate_project_source_count"] == 0
    assert counts["open_review_queue_count"] == 0

    tasks = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks"
    ).json()["items"]
    assert len(tasks) == 1
    task = tasks[0]
    assert task["task_kind"] == "handbook_freshness_check"
    assert task["trigger_source"] == "manual"
    assert task["status"] == "succeeded"
    assert task["started_at"] is not None
    assert task["completed_at"] is not None
    assert task["error_message"] is None

    parsed = json.loads(task["result_summary"])
    assert parsed["handbook_version_count"] == 0
    assert parsed["days_since_last_handbook_version"] is None


def test_handbook_freshness_reflects_existing_handbook_and_candidates(
    client: TestClient,
) -> None:
    project = _create_project(client)

    # Draft a handbook version — makes handbook_version_count == 1
    draft = client.post(
        f"/api/v1/openai/projects/{project['project_id']}/draft-handbook",
        json={"handbook_markdown": "# H\n\nBody."},
    )
    assert draft.status_code == 200

    response = client.post(
        f"/api/v1/projects/{project['project_id']}/check-handbook-freshness",
    )
    assert response.status_code == 200
    counts = response.json()["counts"]
    assert counts["handbook_version_count"] == 1
    assert counts["days_since_last_handbook_version"] is not None
    assert counts["days_since_last_handbook_version"] >= 0.0


def test_handbook_freshness_unknown_project_returns_404_without_task(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/projects/nonexistent/check-handbook-freshness"
    )
    assert response.status_code == 404


def test_handbook_freshness_backend_failure_records_failed_task(
    client: TestClient,
    monkeypatch,
) -> None:
    project = _create_project(client)

    from harbor.api.routes import handbook_freshness as route
    from harbor.exceptions import InvalidPayloadError

    def _explode(*args, **kwargs):
        raise InvalidPayloadError("HandbookFreshness", "simulated compute failure")

    monkeypatch.setattr(route, "compute_handbook_freshness", _explode)

    response = client.post(
        f"/api/v1/projects/{project['project_id']}/check-handbook-freshness",
    )
    assert response.status_code == 422

    tasks = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks"
    ).json()["items"]
    assert len(tasks) == 1
    task = tasks[0]
    assert task["status"] == "failed"
    assert task["task_kind"] == "handbook_freshness_check"
    assert "simulated compute failure" in (task["error_message"] or "")
    assert task["completed_at"] is not None
