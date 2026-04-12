from __future__ import annotations

from fastapi.testclient import TestClient


def test_operator_js_has_fetch_now_wiring(client: TestClient) -> None:
    js = client.get("/static/operator.js").text
    assert 'data-action="source-fetch-now"' in js
    assert "/fetch-now" in js
    assert "Fetch now" in js


def test_operator_js_conditions_fetch_now_on_web_page(client: TestClient) -> None:
    js = client.get("/static/operator.js").text
    # The button should only render when source_type === "web_page" AND canonical_url
    assert 'source_type === "web_page"' in js
    assert "canonical_url" in js
