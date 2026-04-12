from __future__ import annotations

from fastapi.testclient import TestClient


def test_project_detail_project_sources_table_has_snapshot_column(
    client: TestClient,
) -> None:
    project = client.post(
        "/api/v1/projects",
        json={
            "title": "SnapUI",
            "short_description": "d",
            "project_type": "standard",
        },
    ).json()
    html = client.get(f"/operator/projects/{project['project_id']}").text
    assert 'id="project-sources-table"' in html
    assert "Latest snapshot" in html
    assert 'colspan="8"' in html


def test_operator_js_has_snapshot_loader(client: TestClient) -> None:
    js = client.get("/static/operator.js").text
    assert "loadProjectSourceSnapshot" in js
    assert "project-source-snapshot" in js
    assert "/snapshots/latest" in js
