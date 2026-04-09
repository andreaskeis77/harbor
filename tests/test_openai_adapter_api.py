from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from harbor import openai_adapter as openai_adapter_module
from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache
from harbor.persistence import Base
from harbor.persistence.session import build_engine

_OPENAI_ENV_KEYS = (
    "HARBOR_OPENAI_API_KEY",
    "HARBOR_OPENAI_MODEL",
    "HARBOR_OPENAI_TIMEOUT_SECONDS",
)


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()
    settings = HarborSettings()
    app = create_app(settings=settings)
    with TestClient(app) as client:
        yield client
    clear_settings_cache()


@pytest.fixture()
def project_client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_file = tmp_path / "openai_project_dry_run_test.db"
    monkeypatch.setenv(
        "HARBOR_SQLALCHEMY_DATABASE_URL",
        f"sqlite+pysqlite:///{db_file.as_posix()}",
    )
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()

    settings = HarborSettings()
    engine = build_engine(settings)
    assert engine is not None
    Base.metadata.create_all(bind=engine)

    app = create_app(settings=settings)
    with TestClient(app) as client:
        yield client
    clear_settings_cache()


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


def test_openai_runtime_endpoint_defaults(client: TestClient) -> None:
    response = client.get("/api/v1/openai/runtime")
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


def test_openai_probe_not_configured(client: TestClient) -> None:
    response = client.post("/api/v1/openai/probe", json={})
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
    assert response.json()["detail"] == "Project not found."


def test_openai_project_dry_run_logs_project_not_found(
    project_client: TestClient,
) -> None:
    response = project_client.get("/api/v1/openai/projects/not-found/dry-run-logs")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found."


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
