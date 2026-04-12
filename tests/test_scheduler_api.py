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


def _attach_candidate_source(
    client: TestClient, project_id: str, url: str
) -> dict:
    source = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "S",
            "canonical_url": url,
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    ).json()
    attached = client.post(
        f"/api/v1/projects/{project_id}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    ).json()
    return attached


def test_scheduler_put_accepts_global_handler_task_kind(client: TestClient) -> None:
    response = client.put(
        "/api/v1/scheduler/schedules/stale_source_sweep",
        json={"interval_seconds": 3600, "enabled": True},
    )
    assert response.status_code == 200
    assert response.json()["task_kind"] == "stale_source_sweep"


def test_scheduler_tick_runs_global_handler_once_with_null_project(
    client: TestClient,
) -> None:
    _create_project(client, "Proj A")
    _create_project(client, "Proj B")

    client.put(
        "/api/v1/scheduler/schedules/stale_source_sweep",
        json={"interval_seconds": 3600, "enabled": True},
    )

    response = client.post("/api/v1/scheduler/tick")
    assert response.status_code == 200
    runs = response.json()["runs"]
    # Global handler runs ONCE per tick regardless of project count.
    assert len(runs) == 1, runs
    assert runs[0]["task_kind"] == "stale_source_sweep"
    assert runs[0]["project_id"] == ""
    assert runs[0]["status"] == "succeeded"
    assert runs[0]["automation_task_id"] is not None


def test_scheduler_tick_global_and_per_project_coexist(client: TestClient) -> None:
    project_a = _create_project(client, "Proj A")
    project_b = _create_project(client, "Proj B")

    client.put(
        "/api/v1/scheduler/schedules/stale_source_sweep",
        json={"interval_seconds": 3600, "enabled": True},
    )
    client.put(
        "/api/v1/scheduler/schedules/snapshot_workflow_summary",
        json={"interval_seconds": 3600, "enabled": True},
    )

    response = client.post("/api/v1/scheduler/tick")
    runs = response.json()["runs"]
    # 1 global + 2 projects * 1 per-project handler = 3 runs
    assert len(runs) == 3, runs

    kinds_seen = {r["task_kind"] for r in runs}
    assert kinds_seen == {"stale_source_sweep", "snapshot_workflow_summary"}

    global_runs = [r for r in runs if r["task_kind"] == "stale_source_sweep"]
    assert len(global_runs) == 1
    assert global_runs[0]["project_id"] == ""

    per_project_runs = [
        r for r in runs if r["task_kind"] == "snapshot_workflow_summary"
    ]
    assert {r["project_id"] for r in per_project_runs} == {
        project_a["project_id"],
        project_b["project_id"],
    }


def test_scheduler_recent_tasks_empty(client: TestClient) -> None:
    response = client.get("/api/v1/scheduler/recent-tasks")
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_scheduler_recent_tasks_returns_newest_first(client: TestClient) -> None:
    _create_project(client, "Proj A")
    _create_project(client, "Proj B")
    client.put(
        "/api/v1/scheduler/schedules/stale_source_sweep",
        json={"interval_seconds": 3600, "enabled": True},
    )
    client.put(
        "/api/v1/scheduler/schedules/snapshot_workflow_summary",
        json={"interval_seconds": 3600, "enabled": True},
    )
    tick = client.post("/api/v1/scheduler/tick").json()
    assert len(tick["runs"]) == 3  # 1 global + 2 per-project

    response = client.get("/api/v1/scheduler/recent-tasks")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 3
    assert all(i["trigger_source"] == "scheduled" for i in items)
    assert all(i["status"] == "succeeded" for i in items)
    # Ordered newest first by created_at (non-increasing).
    timestamps = [i["created_at"] for i in items]
    assert timestamps == sorted(timestamps, reverse=True)
    # Global run has null project_id.
    kinds = {i["task_kind"] for i in items}
    assert kinds == {"stale_source_sweep", "snapshot_workflow_summary"}
    global_items = [i for i in items if i["task_kind"] == "stale_source_sweep"]
    assert len(global_items) == 1
    assert global_items[0]["project_id"] is None


def test_scheduler_recent_tasks_respects_limit_and_cap(client: TestClient) -> None:
    _create_project(client)
    client.put(
        "/api/v1/scheduler/schedules/snapshot_workflow_summary",
        json={"interval_seconds": 1, "enabled": True},
    )
    # Tick several times (interval=1s is effectively immediate after a small wait,
    # but we only care that at least one row exists and limit is honored).
    client.post("/api/v1/scheduler/tick")

    response = client.get("/api/v1/scheduler/recent-tasks?limit=1")
    assert response.status_code == 200
    assert len(response.json()["items"]) <= 1

    # Cap is 200; any huge limit is accepted without error.
    response = client.get("/api/v1/scheduler/recent-tasks?limit=5000")
    assert response.status_code == 200


def test_stale_source_sweep_handler_summarizes_candidate_ages(
    client: TestClient,
) -> None:
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select as sa_select

    from harbor.config import get_settings
    from harbor.persistence.models import ProjectSourceRecord
    from harbor.persistence.session import build_engine
    from harbor.scheduler import _run_stale_source_sweep

    project_a = _create_project(client, "Stale A")
    project_b = _create_project(client, "Stale B")

    # Two candidate sources in project A, one in project B.
    _attach_candidate_source(client, project_a["project_id"], "https://example.com/a1")
    _attach_candidate_source(client, project_a["project_id"], "https://example.com/a2")
    _attach_candidate_source(client, project_b["project_id"], "https://example.com/b1")

    # Backdate the two project-A records to older than the 7-day threshold.
    engine = build_engine(get_settings())
    assert engine is not None
    from sqlalchemy.orm import Session as OrmSession

    with OrmSession(engine) as session:
        records = list(
            session.execute(
                sa_select(ProjectSourceRecord).where(
                    ProjectSourceRecord.project_id == project_a["project_id"],
                )
            )
            .scalars()
            .all()
        )
        assert len(records) == 2
        old_time = datetime.now(UTC) - timedelta(days=30)
        for r in records:
            r.created_at = old_time
        session.commit()

        result_json = _run_stale_source_sweep(session)

    import json as _json

    summary = _json.loads(result_json)
    assert summary["threshold_days"] == 7
    assert summary["total_candidate_count"] == 3
    assert summary["stale_count"] == 2
    assert summary["oldest_age_days"] >= 29
    assert summary["stale_by_project"] == {project_a["project_id"]: 2}
