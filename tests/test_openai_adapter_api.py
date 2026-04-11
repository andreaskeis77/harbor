from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from harbor import openai_adapter as openai_adapter_module
from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache

_OPENAI_ENV_KEYS = (
    "HARBOR_OPENAI_API_KEY",
    "HARBOR_OPENAI_MODEL",
    "HARBOR_OPENAI_TIMEOUT_SECONDS",
)


@pytest.fixture()
def no_db_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Client without database — for testing OpenAI config/probe endpoints only."""
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()
    settings = HarborSettings()
    app = create_app(settings=settings)
    with TestClient(app) as tc:
        yield tc
    clear_settings_cache()


@pytest.fixture()
def project_client(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Re-use the shared DB client with OpenAI env keys cleared."""
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()
    return client


def _create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Scuba Research",
            "short_description": "Hotels with house reef",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_source(
    client: TestClient,
    *,
    title: str,
    canonical_url: str,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": title,
            "canonical_url": canonical_url,
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_openai_runtime_endpoint_defaults(no_db_client: TestClient) -> None:
    response = no_db_client.get("/api/v1/openai/runtime")
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "openai"
    assert payload["configured"] is False
    assert payload["model"] == "gpt-5"
    assert isinstance(payload["sdk_available"], bool)


def test_openai_runtime_endpoint_with_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HARBOR_OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HARBOR_OPENAI_MODEL", "gpt-5")
    monkeypatch.setenv("HARBOR_OPENAI_TIMEOUT_SECONDS", "45")
    clear_settings_cache()
    settings = HarborSettings()
    app = create_app(settings=settings)

    with TestClient(app) as client:
        response = client.get("/api/v1/openai/runtime")

    assert response.status_code == 200
    payload = response.json()
    assert payload["configured"] is True
    assert payload["api_key_present"] is True
    assert payload["model"] == "gpt-5"
    assert payload["timeout_seconds"] == 45.0

    monkeypatch.delenv("HARBOR_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_MODEL", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_TIMEOUT_SECONDS", raising=False)
    clear_settings_cache()


def test_openai_probe_not_configured(no_db_client: TestClient) -> None:
    response = no_db_client.post("/api/v1/openai/probe", json={})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "not_configured"
    assert payload["live_call_executed"] is False


class _FakeOpenAIResponse:
    def __init__(self) -> None:
        self.id = "resp_test_openai_adapter"
        self.status = "completed"
        self.output_text = "OK"


class _FakeOpenAIResponses:
    def create(self, *, model: str, input: str) -> _FakeOpenAIResponse:
        assert model == "gpt-5"
        assert input == "Respond with OK."
        return _FakeOpenAIResponse()


class _FakeOpenAIClient:
    def __init__(self) -> None:
        self.responses = _FakeOpenAIResponses()


class _FakeProjectDryRunResponse:
    def __init__(self) -> None:
        self.id = "resp_test_project_dry_run"
        self.status = "completed"
        self.output_text = "PROJECT OK"


class _FakeProjectDryRunResponses:
    def create(
        self,
        *,
        model: str,
        instructions: str,
        input: str,
        store: bool,
    ) -> _FakeProjectDryRunResponse:
        assert model == "gpt-5"
        assert instructions == "Return a compact research note."
        assert "Harbor project context:" in input
        assert "- title: Scuba Research" in input
        assert "Operator request:" in input
        assert "Summarize the project focus." in input
        assert store is False
        return _FakeProjectDryRunResponse()


class _FakeProjectDryRunClient:
    def __init__(self) -> None:
        self.responses = _FakeProjectDryRunResponses()


class _FakeChatTurnResponse:
    def __init__(self, response_id: str, output_text: str) -> None:
        self.id = response_id
        self.status = "completed"
        self.output_text = output_text


class _FakeChatTurnResponses:
    def __init__(self) -> None:
        self.calls = 0

    def create(
        self,
        *,
        model: str,
        instructions: str,
        input: str,
        store: bool,
    ) -> _FakeChatTurnResponse:
        assert model == "gpt-5"
        assert store is False
        self.calls += 1

        if self.calls == 1:
            assert instructions
            assert "Harbor project context:" in input
            assert "Prior chat turns:" not in input
            assert "Current operator message:\nHello Harbor." in input
            return _FakeChatTurnResponse("resp_test_chat_turn_1", "CHAT ONE")

        assert "Prior chat turns:" in input
        assert "- total_available: 1" in input
        assert "- included: 1" in input
        assert "Turn 1:" in input
        assert "Operator: Hello Harbor." in input
        assert "Assistant: CHAT ONE" in input
        assert "Current operator message:\nGive me the next step." in input
        return _FakeChatTurnResponse("resp_test_chat_turn_2", "CHAT TWO")


class _FakeChatTurnClient:
    def __init__(self) -> None:
        self.responses = _FakeChatTurnResponses()


def test_build_project_chat_turn_input_limits_and_compacts_prior_turns() -> None:
    project_context = {
        "project_id": "project-1",
        "title": "Scuba Research",
        "short_description": "Hotels with house reef",
        "status": "draft",
        "project_type": "standard",
        "blueprint_status": "not_blueprint",
    }
    prior_turns = [
        {
            "request_input_text": f"Question turn {index} " + ("x" * 400),
            "output_text": f"Answer turn {index} " + ("y" * 500),
        }
        for index in range(1, 9)
    ]

    rendered = openai_adapter_module.build_project_chat_turn_input(
        project_context,
        "Give me the next step.",
        prior_turns=prior_turns,
    )

    assert "Harbor project context:" in rendered
    assert "Prior chat turns:" in rendered
    assert "- total_available: 8" in rendered
    assert "- included: 6" in rendered
    assert "- omitted: 2" in rendered
    assert "- note: Earlier or longer turns were compacted." in rendered
    assert "Question turn 1" not in rendered
    assert "Question turn 2" not in rendered
    assert "Question turn 3" in rendered
    assert "Question turn 8" in rendered
    assert "…[truncated]" in rendered
    assert "Current operator message:\nGive me the next step." in rendered


def test_openai_project_chat_turn_payload_limits_project_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()

    project_context = {
        "project_id": "project-1",
        "title": "Scuba Research",
        "short_description": "Hotels with house reef",
        "status": "draft",
        "project_type": "standard",
        "blueprint_status": "not_blueprint",
    }
    project_sources = [
        {
            "note": f"Source note {index}",
            "source": {
                "title": f"Accepted Source {index}",
                "canonical_url": f"https://example.com/accepted-source-{index}",
            },
        }
        for index in range(1, 9)
    ]

    payload = openai_adapter_module.openai_project_chat_turn_payload(
        HarborSettings(),
        project_context=project_context,
        input_text="Summarize the accepted project sources.",
        project_sources=project_sources,
        instructions="Stay concise.",
    )

    assert payload["status"] == "not_configured"
    assert payload["request_metadata"]["project_source_count_available"] == 8
    assert payload["request_metadata"]["project_source_count_included"] == 6

    rendered_input_text = payload["request"]["rendered_input_text"]
    assert "Harbor project context:" in rendered_input_text
    assert "Project sources" in rendered_input_text
    assert "Accepted Source 1" in rendered_input_text
    assert "Accepted Source 6" in rendered_input_text
    assert "Accepted Source 7" not in rendered_input_text
    assert "Accepted Source 8" not in rendered_input_text
    assert "Source note 1" in rendered_input_text
    # T5.0A: Without relevance/trust_tier/review_status, no metadata bracket line
    assert "[relevance=" not in rendered_input_text
    # T5.0B: Citation instruction present (sources exist), cited_sources empty (not_configured)
    assert "Cite sources by number" in rendered_input_text
    assert "cite them by number" in payload["request"]["instructions"].lower()
    assert payload["cited_sources"] == []
    assert (
        "Current operator message:\nSummarize the accepted project sources."
        in rendered_input_text
    )

    clear_settings_cache()


def test_openai_probe_live_call_with_fake_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HARBOR_OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HARBOR_OPENAI_MODEL", "gpt-5")
    clear_settings_cache()

    monkeypatch.setattr(openai_adapter_module, "openai_sdk_available", lambda: True)
    monkeypatch.setattr(
        openai_adapter_module,
        "build_openai_client",
        lambda settings, client_factory=None: _FakeOpenAIClient(),
    )

    settings = HarborSettings()
    app = create_app(settings=settings)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/openai/probe",
            json={"live_call": True, "input_text": "Respond with OK."},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["live_call_executed"] is True
    assert payload["response_id"] == "resp_test_openai_adapter"
    assert payload["output_text"] == "OK"

    monkeypatch.delenv("HARBOR_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_MODEL", raising=False)
    clear_settings_cache()


def test_openai_project_dry_run_project_not_found(project_client: TestClient) -> None:
    response = project_client.post(
        "/api/v1/openai/projects/not-found/dry-run",
        json={"input_text": "Summarize the project focus."},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 'not-found' not found."


def test_openai_project_dry_run_logs_project_not_found(
    project_client: TestClient,
) -> None:
    response = project_client.get("/api/v1/openai/projects/not-found/dry-run-logs")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 'not-found' not found."


def test_openai_project_dry_run_not_configured(project_client: TestClient) -> None:
    project = _create_project(project_client)

    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/dry-run",
        json={
            "input_text": "Summarize the project focus.",
            "persist": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "not_configured"
    assert payload["project"]["project_id"] == project["project_id"]
    assert payload["request"]["instructions_source"] == "default"
    assert payload["request"]["store"] is False
    assert "Harbor project context:" in payload["request"]["rendered_input_text"]
    assert payload["persisted"] is True
    assert payload["log"]["status"] == "not_configured"

    logs_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/dry-run-logs"
    )
    assert logs_response.status_code == 200
    logs_payload = logs_response.json()
    assert len(logs_payload["items"]) == 1
    assert logs_payload["items"][0]["request_input_text"] == "Summarize the project focus."


def test_openai_project_dry_run_with_fake_client(
    project_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _create_project(project_client)
    monkeypatch.setenv("HARBOR_OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HARBOR_OPENAI_MODEL", "gpt-5")
    clear_settings_cache()

    monkeypatch.setattr(openai_adapter_module, "openai_sdk_available", lambda: True)
    monkeypatch.setattr(
        openai_adapter_module,
        "build_openai_client",
        lambda settings, client_factory=None: _FakeProjectDryRunClient(),
    )

    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/dry-run",
        json={
            "instructions": "Return a compact research note.",
            "input_text": "Summarize the project focus.",
            "persist": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["project"]["project_id"] == project["project_id"]
    assert payload["request"]["instructions_source"] == "custom"
    assert payload["response_id"] == "resp_test_project_dry_run"
    assert payload["output_text"] == "PROJECT OK"
    assert payload["persisted"] is True
    assert payload["log"]["response_id"] == "resp_test_project_dry_run"

    logs_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/dry-run-logs"
    )
    assert logs_response.status_code == 200
    logs_payload = logs_response.json()
    assert len(logs_payload["items"]) == 1
    assert logs_payload["items"][0]["status"] == "completed"

    monkeypatch.delenv("HARBOR_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_MODEL", raising=False)
    clear_settings_cache()


def test_openai_project_chat_sessions_project_not_found(
    project_client: TestClient,
) -> None:
    response = project_client.get("/api/v1/openai/projects/not-found/chat-sessions")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 'not-found' not found."


def test_openai_project_chat_turn_not_configured(
    project_client: TestClient,
) -> None:
    project = _create_project(project_client)

    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={"input_text": "Hello Harbor."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "not_configured"
    assert payload["session"]["project_id"] == project["project_id"]
    assert payload["turn"]["request_input_text"] == "Hello Harbor."
    assert payload["request_metadata"]["project_source_count_available"] == 0
    assert payload["request_metadata"]["project_source_count_included"] == 0
    assert "Project sources" in payload["request"]["rendered_input_text"]
    assert "(no accepted project sources available)" in payload["request"]["rendered_input_text"]
    # T5.0B: No citation instruction when no sources
    assert "Cite sources by number" not in payload["request"]["rendered_input_text"]
    assert "cite them by number" not in payload["request"]["instructions"].lower()
    assert payload["cited_sources"] == []
    # T5.1A: No handbook → placeholder in rendered text
    assert payload["request_metadata"]["handbook_available"] is False
    assert "(no handbook available for this project)" in payload["request"]["rendered_input_text"]

    sessions_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions"
    )
    assert sessions_response.status_code == 200
    sessions_payload = sessions_response.json()
    assert len(sessions_payload["items"]) == 1

    session_id = sessions_payload["items"][0]["openai_project_chat_session_id"]
    turns_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions/{session_id}/turns"
    )
    assert turns_response.status_code == 200
    turns_payload = turns_response.json()
    assert len(turns_payload["items"]) == 1
    assert turns_payload["items"][0]["status"] == "not_configured"


def test_openai_project_chat_turn_includes_accepted_project_sources(
    project_client: TestClient,
) -> None:
    project = _create_project(project_client)
    source_one = _create_source(
        project_client,
        title="Accepted Source One",
        canonical_url="https://example.com/accepted-source-one",
    )
    source_two = _create_source(
        project_client,
        title="Accepted Source Two",
        canonical_url="https://example.com/accepted-source-two",
    )
    source_three = _create_source(
        project_client,
        title="Candidate Source",
        canonical_url="https://example.com/candidate-source",
    )

    attach_source_one_response = project_client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source_one["source_id"],
            "relevance": "primary",
            "review_status": "accepted",
            "note": "Primary source note.",
        },
    )
    assert attach_source_one_response.status_code == 201

    attach_source_two_response = project_client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source_two["source_id"],
            "relevance": "supporting",
            "review_status": "accepted",
        },
    )
    assert attach_source_two_response.status_code == 201

    attach_source_three_response = project_client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source_three["source_id"],
            "relevance": "supporting",
            "review_status": "candidate",
            "note": "Candidate sources should stay out of chat grounding.",
        },
    )
    assert attach_source_three_response.status_code == 201

    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={
            "input_text": "Summarize the accepted project sources.",
            "instructions": "Stay concise.",
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "not_configured"
    assert payload["request_metadata"]["project_source_count_available"] == 2
    assert payload["request_metadata"]["project_source_count_included"] == 2
    # T5.0B: Citation instruction appended when sources are present
    assert payload["request"]["instructions"].startswith("Stay concise.")
    assert "cite them by number" in payload["request"]["instructions"].lower()
    # cited_sources empty because not_configured (no LLM call)
    assert payload["cited_sources"] == []

    rendered_input_text = payload["request"]["rendered_input_text"]
    assert "Harbor project context:" in rendered_input_text
    assert "Project sources" in rendered_input_text
    assert "Accepted Source One" in rendered_input_text
    assert "Accepted Source Two" in rendered_input_text
    assert "https://example.com/accepted-source-one" in rendered_input_text
    assert "https://example.com/accepted-source-two" in rendered_input_text
    assert "Primary source note." in rendered_input_text
    assert "Candidate Source" not in rendered_input_text
    # T5.1A: No handbook for this project → placeholder
    assert "(no handbook available for this project)" in rendered_input_text
    assert payload["request_metadata"]["handbook_available"] is False
    assert (
        "Current operator message:\nSummarize the accepted project sources."
        in rendered_input_text
    )
    assert rendered_input_text.index("Harbor project context:") < rendered_input_text.index(
        "Project sources"
    )
    assert rendered_input_text.index("Project sources") < rendered_input_text.index(
        "Current operator message:"
    )
    assert payload["turn"]["rendered_input_text"] == rendered_input_text

    # T5.0B: Citation instruction rendered in source section
    assert "Cite sources by number" in rendered_input_text

    # T5.0A: Verify enriched source metadata in rendered prompt
    assert "relevance=primary" in rendered_input_text
    assert "trust=candidate" in rendered_input_text
    assert "review=accepted" in rendered_input_text
    assert "relevance=supporting" in rendered_input_text

    # Verify source_attribution is returned in payload and persisted turn
    source_attr = payload["source_attribution"]
    assert isinstance(source_attr, list)
    assert len(source_attr) == 2
    attr_titles = {s["title"] for s in source_attr}
    assert attr_titles == {"Accepted Source One", "Accepted Source Two"}
    for entry in source_attr:
        assert "source_id" in entry
        assert "project_source_id" in entry
        assert "canonical_url" in entry
    source_one_attr = next(s for s in source_attr if s["title"] == "Accepted Source One")
    assert source_one_attr["canonical_url"] == "https://example.com/accepted-source-one"
    assert source_one_attr["note"] == "Primary source note."

    # T5.0A: Verify enriched metadata fields in source_attribution
    assert source_one_attr["relevance"] == "primary"
    assert source_one_attr["trust_tier"] == "candidate"
    assert source_one_attr["review_status"] == "accepted"
    source_two_attr = next(s for s in source_attr if s["title"] == "Accepted Source Two")
    assert source_two_attr["relevance"] == "supporting"
    assert source_two_attr["trust_tier"] == "candidate"
    assert source_two_attr["review_status"] == "accepted"

    # Verify source_attribution is persisted on the turn record
    turn_attr = payload["turn"]["source_attribution"]
    assert isinstance(turn_attr, list)
    assert len(turn_attr) == 2
    turn_titles = {s["title"] for s in turn_attr}
    assert turn_titles == {"Accepted Source One", "Accepted Source Two"}


def test_project_sources_lines_renders_enriched_metadata() -> None:
    prepared_sources = [
        {
            "title": "Source Alpha",
            "canonical_url": "https://example.com/alpha",
            "note": "Important source.",
            "relevance": "primary",
            "trust_tier": "verified",
            "review_status": "accepted",
        },
        {
            "title": "Source Beta",
            "canonical_url": "https://example.com/beta",
            "note": "",
            "relevance": "supporting",
            "trust_tier": "candidate",
            "review_status": "accepted",
        },
    ]
    lines = openai_adapter_module._project_sources_lines(prepared_sources)
    rendered = "\n".join(lines)

    assert "1. Source Alpha" in rendered
    assert "URL: https://example.com/alpha" in rendered
    assert "[relevance=primary, trust=verified, review=accepted]" in rendered
    assert "Note: Important source." in rendered

    assert "2. Source Beta" in rendered
    assert "URL: https://example.com/beta" in rendered
    assert "[relevance=supporting, trust=candidate, review=accepted]" in rendered
    # No note for Source Beta (empty string)
    beta_section = rendered[rendered.index("2. Source Beta"):]
    assert "Note:" not in beta_section

    # T5.0B: Citation instruction at end of sources section
    assert "Cite sources by number" in rendered


def test_prepare_project_sources_extracts_enriched_fields() -> None:
    project_sources = [
        {
            "relevance": "primary",
            "review_status": "accepted",
            "note": "A note",
            "source": {
                "title": "Test Source",
                "canonical_url": "https://example.com/test",
                "source_id": "src-1",
                "trust_tier": "verified",
            },
            "project_source_id": "ps-1",
        },
    ]
    prepared, meta = openai_adapter_module._prepare_project_sources(project_sources)
    assert len(prepared) == 1
    entry = prepared[0]
    assert entry["relevance"] == "primary"
    assert entry["trust_tier"] == "verified"
    assert entry["review_status"] == "accepted"
    assert entry["source_id"] == "src-1"
    assert entry["project_source_id"] == "ps-1"
    assert meta["project_source_count_available"] == 1
    assert meta["project_source_count_included"] == 1


def test_prepare_handbook_context_with_content() -> None:
    text, meta = openai_adapter_module._prepare_handbook_context(
        "# Research Notes\n\nThis is a handbook entry about coral reef research."
    )
    assert text == "# Research Notes This is a handbook entry about coral reef research."
    assert meta["handbook_available"] is True
    assert meta["handbook_chars"] > 0
    assert meta["handbook_truncated"] is False


def test_prepare_handbook_context_empty() -> None:
    text, meta = openai_adapter_module._prepare_handbook_context(None)
    assert text == ""
    assert meta["handbook_available"] is False

    text2, meta2 = openai_adapter_module._prepare_handbook_context("")
    assert text2 == ""
    assert meta2["handbook_available"] is False

    text3, meta3 = openai_adapter_module._prepare_handbook_context("   ")
    assert text3 == ""
    assert meta3["handbook_available"] is False


def test_prepare_handbook_context_truncation() -> None:
    long_text = "x" * 3000
    text, meta = openai_adapter_module._prepare_handbook_context(long_text)
    assert meta["handbook_truncated"] is True
    assert len(text) <= openai_adapter_module.MAX_HANDBOOK_CHARS
    assert text.endswith("…[truncated]")


def test_handbook_context_lines_with_content() -> None:
    lines = openai_adapter_module._handbook_context_lines("Some handbook content here.")
    rendered = "\n".join(lines)
    assert "Project handbook" in rendered
    assert "Some handbook content here." in rendered


def test_handbook_context_lines_empty() -> None:
    lines = openai_adapter_module._handbook_context_lines("")
    rendered = "\n".join(lines)
    assert "Project handbook" in rendered
    assert "(no handbook available for this project)" in rendered


def test_openai_project_chat_turn_with_handbook(
    project_client: TestClient,
) -> None:
    project = _create_project(project_client)

    # Create a handbook for the project
    handbook_response = project_client.put(
        f"/api/v1/projects/{project['project_id']}/handbook",
        json={
            "handbook_markdown": "# Reef Guide\n\nBest reefs are in the Maldives and Red Sea.",
        },
    )
    assert handbook_response.status_code == 200

    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={"input_text": "What are the best reefs?"},
    )
    assert response.status_code == 200
    payload = response.json()

    rendered = payload["request"]["rendered_input_text"]
    assert "Project handbook" in rendered
    assert "Reef Guide" in rendered
    assert "Maldives and Red Sea" in rendered
    assert payload["request_metadata"]["handbook_available"] is True
    assert payload["request_metadata"]["handbook_truncated"] is False

    # Verify ordering: handbook before sources before operator message
    assert rendered.index("Project handbook") < rendered.index("Project sources")
    assert rendered.index("Project sources") < rendered.index("Current operator message:")


def test_extract_source_citations_basic() -> None:
    sources = [
        {"title": "Alpha", "canonical_url": "https://a.com"},
        {"title": "Beta", "canonical_url": "https://b.com"},
        {"title": "Gamma", "canonical_url": "https://c.com"},
    ]
    # Cites [1] and [3] but not [2]
    output = "According to [1], the reef is excellent. See also [3] for details."
    cited = openai_adapter_module._extract_source_citations(output, sources)
    assert len(cited) == 2
    assert cited[0]["title"] == "Alpha"
    assert cited[1]["title"] == "Gamma"


def test_extract_source_citations_no_matches() -> None:
    sources = [{"title": "Alpha", "canonical_url": "https://a.com"}]
    output = "No citations here at all."
    cited = openai_adapter_module._extract_source_citations(output, sources)
    assert cited == []


def test_extract_source_citations_out_of_range() -> None:
    sources = [{"title": "Alpha", "canonical_url": "https://a.com"}]
    output = "Reference [0] and [2] are out of range, only [1] is valid."
    cited = openai_adapter_module._extract_source_citations(output, sources)
    assert len(cited) == 1
    assert cited[0]["title"] == "Alpha"


def test_extract_source_citations_empty_inputs() -> None:
    assert openai_adapter_module._extract_source_citations(None, []) == []
    assert openai_adapter_module._extract_source_citations("text [1]", []) == []
    assert openai_adapter_module._extract_source_citations(
        None, [{"title": "X"}]
    ) == []


def test_openai_project_chat_turn_no_sources_attribution(
    project_client: TestClient,
) -> None:
    project = _create_project(project_client)
    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={"input_text": "What do you know?"},
    )
    assert response.status_code == 200
    payload = response.json()

    # No sources attached — attribution and cited_sources should be empty
    assert payload["source_attribution"] == []
    assert payload["cited_sources"] == []
    assert payload["turn"]["source_attribution"] == []


def test_openai_project_chat_turn_with_fake_client(
    project_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _create_project(project_client)
    monkeypatch.setenv("HARBOR_OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HARBOR_OPENAI_MODEL", "gpt-5")
    clear_settings_cache()

    monkeypatch.setattr(openai_adapter_module, "openai_sdk_available", lambda: True)
    fake_client = _FakeChatTurnClient()
    monkeypatch.setattr(
        openai_adapter_module,
        "build_openai_client",
        lambda settings, client_factory=None: fake_client,
    )

    first_response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={"input_text": "Hello Harbor."},
    )
    assert first_response.status_code == 200
    first_payload = first_response.json()
    assert first_payload["status"] == "completed"
    assert first_payload["turn"]["turn_index"] == 1
    assert first_payload["output_text"] == "CHAT ONE"

    session_id = first_payload["session"]["openai_project_chat_session_id"]
    second_response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={
            "chat_session_id": session_id,
            "input_text": "Give me the next step.",
        },
    )
    assert second_response.status_code == 200
    second_payload = second_response.json()
    assert second_payload["status"] == "completed"
    assert second_payload["turn"]["turn_index"] == 2
    assert second_payload["request"]["prior_turn_count"] == 1
    assert second_payload["request"]["prior_turn_count_included"] == 1
    assert second_payload["request"]["prior_turn_count_omitted"] == 0
    assert second_payload["request"]["history_compacted"] is False
    assert second_payload["output_text"] == "CHAT TWO"

    sessions_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions"
    )
    assert sessions_response.status_code == 200
    sessions_payload = sessions_response.json()
    assert len(sessions_payload["items"]) == 1
    assert sessions_payload["items"][0]["turn_count"] == 2

    turns_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions/{session_id}/turns"
    )
    assert turns_response.status_code == 200
    turns_payload = turns_response.json()
    assert len(turns_payload["items"]) == 2
    assert turns_payload["items"][1]["response_id"] == "resp_test_chat_turn_2"

    missing_session_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions/not-found/turns"
    )
    assert missing_session_response.status_code == 404
    assert missing_session_response.json()["detail"] == "Chat session 'not-found' not found."

    monkeypatch.delenv("HARBOR_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_MODEL", raising=False)
    clear_settings_cache()
