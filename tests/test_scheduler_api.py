from __future__ import annotations

from fastapi.testclient import TestClient


def _create_project(client: TestClient, title: str = "Scheduler Test Project") -> dict:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": title,
            "short_description": "Scheduler test",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_scheduler_list_starts_empty(client: TestClient) -> None:
    response = client.get("/api/v1/scheduler/schedules")
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_scheduler_put_creates_then_updates_schedule(client: TestClient) -> None:
    create = client.put(
        "/api/v1/scheduler/schedules/snapshot_workflow_summary",
        json={"interval_seconds": 3600, "enabled": True},
    )
    assert create.status_code == 200
    payload = create.json()
    assert payload["task_kind"] == "snapshot_workflow_summary"
    assert payload["interval_seconds"] == 3600
    assert payload["enabled"] is True
    assert payload["last_run_at"] is None
    assert payload["next_run_at"] is None

    update = client.put(
        "/api/v1/scheduler/schedules/snapshot_workflow_summary",
        json={"interval_seconds": 7200, "enabled": False},
    )
    assert update.status_code == 200
    updated = update.json()
    assert updated["interval_seconds"] == 7200
    assert updated["enabled"] is False
    assert updated["automation_schedule_id"] == payload["automation_schedule_id"]

    listed = client.get("/api/v1/scheduler/schedules").json()
    assert len(listed["items"]) == 1


def test_scheduler_put_rejects_unknown_task_kind(client: TestClient) -> None:
    response = client.put(
        "/api/v1/scheduler/schedules/does_not_exist",
        json={"interval_seconds": 60, "enabled": True},
    )
    assert response.status_code == 422


def test_scheduler_patch_updates_enabled(client: TestClient) -> None:
    client.put(
        "/api/v1/scheduler/schedules/handbook_freshness_check",
        json={"interval_seconds": 300, "enabled": True},
    )
    response = client.patch(
        "/api/v1/scheduler/schedules/handbook_freshness_check",
        json={"enabled": False},
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is False
    assert response.json()["interval_seconds"] == 300


def test_scheduler_patch_unknown_task_kind_404(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/scheduler/schedules/snapshot_workflow_summary",
        json={"enabled": False},
    )
    assert response.status_code == 404


def test_scheduler_tick_without_schedules_is_noop(client: TestClient) -> None:
    response = client.post("/api/v1/scheduler/tick")
    assert response.status_code == 200
    assert response.json()["runs"] == []


def test_scheduler_tick_runs_enabled_handlers_against_all_projects(
    client: TestClient,
) -> None:
    project_a = _create_project(client, "Proj A")
    project_b = _create_project(client, "Proj B")

    client.put(
        "/api/v1/scheduler/schedules/snapshot_workflow_summary",
        json={"interval_seconds": 3600, "enabled": True},
    )
    client.put(
        "/api/v1/scheduler/schedules/handbook_freshness_check",
        json={"interval_seconds": 3600, "enabled": True},
    )

    response = client.post("/api/v1/scheduler/tick")
    assert response.status_code == 200
    runs = response.json()["runs"]

    # 2 schedules * 2 projects = 4 runs, all succeeded
    assert len(runs) == 4, runs
    assert all(r["status"] == "succeeded" for r in runs), runs
    kinds = {r["task_kind"] for r in runs}
    assert kinds == {"snapshot_workflow_summary", "handbook_freshness_check"}
    projects_seen = {r["project_id"] for r in runs}
    assert projects_seen == {project_a["project_id"], project_b["project_id"]}

    # Each run produced a persisted automation task
    tasks_a = client.get(
        f"/api/v1/projects/{project_a['project_id']}/automation-tasks"
    ).json()["items"]
    assert len(tasks_a) == 2
    assert all(t["status"] == "succeeded" for t in tasks_a)
    assert all(t["trigger_source"] == "scheduled" for t in tasks_a)

    # last_run_at / next_run_at updated on the schedule records
    listed = client.get("/api/v1/scheduler/schedules").json()["items"]
    assert all(s["last_run_at"] is not None for s in listed)
    assert all(s["next_run_at"] is not None for s in listed)


def test_scheduler_tick_skips_disabled_and_not_due_schedules(
    client: TestClient,
) -> None:
    _create_project(client)

    client.put(
        "/api/v1/scheduler/schedules/snapshot_workflow_summary",
        json={"interval_seconds": 3600, "enabled": False},
    )
    response = client.post("/api/v1/scheduler/tick")
    assert response.status_code == 200
    assert response.json()["runs"] == []

    # Enable then run — next_run_at should block the second tick.
    client.patch(
        "/api/v1/scheduler/schedules/snapshot_workflow_summary",
        json={"enabled": True},
    )
    first = client.post("/api/v1/scheduler/tick").json()
    assert len(first["runs"]) == 1

    second = client.post("/api/v1/scheduler/tick").json()
    # interval was 3600s; second tick is within that window — skipped.
    assert second["runs"] == []


def test_scheduler_tick_records_per_project_failures_and_continues(
    client: TestClient,
    monkeypatch,
) -> None:
    project_a = _create_project(client, "Fail A")
    project_b = _create_project(client, "Good B")

    client.put(
        "/api/v1/scheduler/schedules/handbook_freshness_check",
        json={"interval_seconds": 3600, "enabled": True},
    )

    from harbor import scheduler as sched

    original = sched._run_handbook_freshness_check

    def _maybe_fail(session, project_id):
        if project_id == project_a["project_id"]:
            raise RuntimeError("simulated handler failure")
        return original(session, project_id)

    monkeypatch.setitem(
        sched.SCHEDULE_HANDLERS,
        "handbook_freshness_check",
        _maybe_fail,
    )

    response = client.post("/api/v1/scheduler/tick")
    assert response.status_code == 200
    runs = response.json()["runs"]
    assert len(runs) == 2

    by_project = {r["project_id"]: r for r in runs}
    assert by_project[project_a["project_id"]]["status"] == "failed"
    assert "simulated handler failure" in by_project[project_a["project_id"]]["error"]
    assert by_project[project_b["project_id"]]["status"] == "succeeded"

    # Failure persisted via observer side-channel.
    tasks_a = client.get(
        f"/api/v1/projects/{project_a['project_id']}/automation-tasks"
    ).json()["items"]
    assert len(tasks_a) == 1
    assert tasks_a[0]["status"] == "failed"
    assert tasks_a[0]["trigger_source"] == "scheduled"
