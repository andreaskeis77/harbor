from __future__ import annotations

from fastapi.testclient import TestClient

from harbor.pagination import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    resolve_pagination,
)


def test_resolve_pagination_defaults() -> None:
    params = resolve_pagination(None, None)
    assert params.limit == DEFAULT_LIMIT
    assert params.offset == 0


def test_resolve_pagination_caps_limit() -> None:
    assert resolve_pagination(10000, 0).limit == MAX_LIMIT
    assert resolve_pagination(0, 0).limit == 1
    assert resolve_pagination(-5, -5).offset == 0
    assert resolve_pagination(50, 25).offset == 25


def _make_project(client: TestClient) -> dict:
    return client.post(
        "/api/v1/projects",
        json={
            "title": "Pager",
            "short_description": "p",
            "project_type": "standard",
        },
    ).json()


def _seed_automation_tasks(client: TestClient, project_id: str, n: int) -> None:
    # Use the scheduler tick to generate n scheduled tasks across n ticks
    # isn't convenient; instead, create them directly via the registry.
    from sqlalchemy.orm import Session as OrmSession

    from harbor.automation_task_registry import (
        AutomationTaskCreate,
        create_automation_task,
    )
    from harbor.config import get_settings
    from harbor.persistence.session import build_engine

    engine = build_engine(get_settings())
    assert engine is not None
    with OrmSession(engine) as session:
        for i in range(n):
            create_automation_task(
                session,
                AutomationTaskCreate(
                    project_id=project_id,
                    task_kind=f"k{i}",
                    trigger_source="manual",
                ),
            )
        session.commit()


def test_automation_tasks_endpoint_paginates(client: TestClient) -> None:
    project = _make_project(client)
    _seed_automation_tasks(client, project["project_id"], 7)

    # Default (limit=50) returns all 7.
    response = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks"
    ).json()
    assert response["total"] == 7
    assert response["limit"] == DEFAULT_LIMIT
    assert response["offset"] == 0
    assert len(response["items"]) == 7

    # Explicit limit + offset splits the set.
    page_1 = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks?limit=3&offset=0"
    ).json()
    page_2 = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks?limit=3&offset=3"
    ).json()
    page_3 = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks?limit=3&offset=6"
    ).json()
    assert [len(p["items"]) for p in (page_1, page_2, page_3)] == [3, 3, 1]
    assert all(p["total"] == 7 for p in (page_1, page_2, page_3))

    # IDs across pages are disjoint — pagination does not double-count.
    ids = (
        [i["automation_task_id"] for i in page_1["items"]]
        + [i["automation_task_id"] for i in page_2["items"]]
        + [i["automation_task_id"] for i in page_3["items"]]
    )
    assert len(set(ids)) == 7


def test_automation_tasks_endpoint_caps_limit(client: TestClient) -> None:
    project = _make_project(client)
    response = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks?limit=999999"
    ).json()
    assert response["limit"] == MAX_LIMIT


def test_review_queue_endpoint_paginates(client: TestClient) -> None:
    project = _make_project(client)
    # Seed 4 review-queue items via direct persistence.
    from sqlalchemy.orm import Session as OrmSession

    from harbor.config import get_settings
    from harbor.persistence.models import ReviewQueueItemRecord
    from harbor.persistence.session import build_engine

    engine = build_engine(get_settings())
    assert engine is not None
    with OrmSession(engine) as session:
        for i in range(4):
            session.add(
                ReviewQueueItemRecord(
                    project_id=project["project_id"],
                    title=f"rq-{i}",
                )
            )
        session.commit()

    response = client.get(
        f"/api/v1/projects/{project['project_id']}/review-queue-items?limit=2&offset=0"
    ).json()
    assert response["total"] == 4
    assert len(response["items"]) == 2
    assert response["limit"] == 2
    assert response["offset"] == 0
