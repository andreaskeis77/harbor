from __future__ import annotations

from fastapi.testclient import TestClient


def test_projects_table_marked_sortable(client: TestClient) -> None:
    html = client.get("/operator/projects").text
    assert 'class="sortable" id="projects-table"' in html
    assert 'data-sort-type="date">Updated' in html


def test_project_detail_tables_marked_sortable(client: TestClient) -> None:
    project = client.post(
        "/api/v1/projects",
        json={
            "title": "Sortable",
            "short_description": "d",
            "project_type": "standard",
        },
    ).json()
    html = client.get(f"/operator/projects/{project['project_id']}").text

    for tid in (
        "automation-tasks-table",
        "candidates-table",
        "review-queue-table",
        "project-sources-table",
    ):
        assert f'id="{tid}"' in html, tid
    # Numeric type used on the candidates rank column.
    assert 'data-sort-type="number">Rank' in html


def test_sortable_module_present_in_operator_js(client: TestClient) -> None:
    js = client.get("/static/operator.js").text
    assert "initSortableTables" in js
    assert "SORTABLE_STORAGE_PREFIX" in js
    assert "applyTableSort" in js


def test_sortable_css_present(client: TestClient) -> None:
    css = client.get("/static/operator.css").text
    assert "table.sortable th.sortable-header" in css
    assert ".sort-asc" in css
    assert ".sort-desc" in css
