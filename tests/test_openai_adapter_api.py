from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from harbor import openai_adapter as openai_adapter_module
from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache


@pytest.fixture()
def client() -> TestClient:
    clear_settings_cache()
    settings = HarborSettings()
    app = create_app(settings=settings)
    with TestClient(app) as client:
        yield client
    clear_settings_cache()


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
