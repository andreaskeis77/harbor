from __future__ import annotations

from fastapi.testclient import TestClient


def _create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Automation Task Project",
            "short_description": "Project for automation task tests",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_list_automation_tasks_empty_for_new_project(client: TestClient) -> None:
    project = _create_project(client)
    response = client.get(f"/api/v1/projects/{project['project_id']}/automation-tasks")
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_list_automation_tasks_unknown_project_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/projects/nonexistent/automation-tasks")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_automation_task_unknown_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/automation-tasks/nonexistent-task")
    assert response.status_code == 404


def test_draft_handbook_records_succeeded_automation_task(client: TestClient) -> None:
    project = _create_project(client)

    draft_response = client.post(
        f"/api/v1/openai/projects/{project['project_id']}/draft-handbook",
        json={
            "handbook_markdown": "# Draft\n\nBody.",
            "change_note": "Chat draft",
        },
    )
    assert draft_response.status_code == 200
    handbook = draft_response.json()

    list_response = client.get(f"/api/v1/projects/{project['project_id']}/automation-tasks")
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) == 1

    task = items[0]
    assert task["project_id"] == project["project_id"]
    assert task["task_kind"] == "draft_handbook"
    assert task["trigger_source"] == "manual"
    assert task["status"] == "succeeded"
    assert task["started_at"] is not None
    assert task["completed_at"] is not None
    assert task["error_message"] is None
    assert handbook["handbook_version_id"] in (task["result_summary"] or "")

    detail_response = client.get(f"/api/v1/automation-tasks/{task['automation_task_id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["automation_task_id"] == task["automation_task_id"]


def test_draft_handbook_failure_rolls_back_task(client: TestClient) -> None:
    response = client.post(
        "/api/v1/openai/projects/nonexistent/draft-handbook",
        json={"handbook_markdown": "Body."},
    )
    assert response.status_code == 404
