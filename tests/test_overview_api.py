from __future__ import annotations

from fastapi.testclient import TestClient


def _create_project(client: TestClient, title: str = "Ovw") -> dict:
    return client.post(
        "/api/v1/projects",
        json={
            "title": title,
            "short_description": "desc",
            "project_type": "standard",
        },
    ).json()


def test_overview_empty_database(client: TestClient) -> None:
    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["totals"]["projects"] == 0
    assert payload["totals"]["open_review_queue_items"] == 0
    assert payload["projects_summary"] == []
    assert payload["recent_automation_tasks"] == []


def test_overview_counts_reflect_seeded_entities(client: TestClient) -> None:
    project = _create_project(client, "Seeded")
    client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": "open-1"},
    )
    rq2 = client.post(
        f"/api/v1/projects/{project['project_id']}/review-queue-items",
        json={"title": "will-close"},
    ).json()
    client.patch(
        f"/api/v1/projects/{project['project_id']}/review-queue-items/{rq2['review_queue_item_id']}/status",
        json={"status": "rejected"},
    )
    client.post(
        f"/api/v1/openai/projects/{project['project_id']}/draft-handbook",
        json={"handbook_markdown": "# Hi"},
    )

    payload = client.get("/api/v1/overview").json()
    totals = payload["totals"]
    assert totals["projects"] == 1
    assert totals["review_queue_items"] == 2
    # Only the still-open one counts toward open_review_queue_items.
    assert totals["open_review_queue_items"] == 1
    assert totals["handbook_versions"] == 1
    assert totals["automation_tasks"] >= 1

    summary = payload["projects_summary"]
    assert len(summary) == 1
    row = summary[0]
    assert row["project_id"] == project["project_id"]
    assert row["open_review_count"] == 1
    assert row["latest_handbook_version_number"] == 1


def test_overview_projects_summary_capped(client: TestClient) -> None:
    for i in range(25):
        _create_project(client, f"P{i}")
    payload = client.get("/api/v1/overview").json()
    assert payload["totals"]["projects"] == 25
    assert len(payload["projects_summary"]) == 20


def test_operator_overview_page_served(client: TestClient) -> None:
    response = client.get("/operator/overview")
    assert response.status_code == 200
    html = response.text
    assert 'data-operator-shell="overview"' in html
    assert 'id="overview-projects-table"' in html
    assert 'id="overview-tasks-table"' in html
