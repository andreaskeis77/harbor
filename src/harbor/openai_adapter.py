from __future__ import annotations

from importlib.util import find_spec
from typing import Any, Callable

from harbor.config import HarborSettings, get_settings

ClientFactory = Callable[[HarborSettings], object]


class OpenAIProbeError(RuntimeError):
    pass


def openai_sdk_available() -> bool:
    return find_spec("openai") is not None


def build_openai_client(
    settings: HarborSettings,
    client_factory: ClientFactory | None = None,
) -> object:
    if client_factory is not None:
        return client_factory(settings)

    if not settings.openai_configured:
        raise OpenAIProbeError("OpenAI API key is not configured.")

    if not openai_sdk_available():
        raise OpenAIProbeError("OpenAI SDK is not installed.")

    from openai import OpenAI

    kwargs: dict[str, Any] = {
        "api_key": settings.openai_api_key,
        "timeout": settings.openai_timeout_seconds,
    }
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return OpenAI(**kwargs)


def openai_runtime_payload(settings: HarborSettings | None = None) -> dict[str, object]:
    settings = settings or get_settings()
    payload = settings.openai_runtime_dict()
    payload["sdk_available"] = openai_sdk_available()
    return payload


def _response_attr(response: object, name: str) -> object | None:
    return getattr(response, name, None)


def _response_output_text(response: object) -> str | None:
    output_text = _response_attr(response, "output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    if hasattr(response, "model_dump"):
        dumped = response.model_dump()
        maybe_output_text = dumped.get("output_text")
        if isinstance(maybe_output_text, str) and maybe_output_text:
            return maybe_output_text

    return None


def openai_probe_payload(
    settings: HarborSettings | None = None,
    *,
    live_call: bool = False,
    input_text: str = "Respond with the single word OK.",
    client_factory: ClientFactory | None = None,
) -> dict[str, object]:
    settings = settings or get_settings()
    payload: dict[str, object] = {
        **openai_runtime_payload(settings),
        "live_call_requested": live_call,
        "live_call_executed": False,
        "response_id": None,
        "response_status": None,
        "output_text": None,
        "error_type": None,
        "error_message": None,
    }

    if not settings.openai_configured:
        payload["status"] = "not_configured"
        return payload

    if not openai_sdk_available() and client_factory is None:
        payload["status"] = "sdk_unavailable"
        return payload

    if not live_call:
        payload["status"] = "ready"
        return payload

    try:
        client = build_openai_client(settings=settings, client_factory=client_factory)
        response = client.responses.create(model=settings.openai_model, input=input_text)
        payload["live_call_executed"] = True
        payload["status"] = "completed"
        payload["response_id"] = _response_attr(response, "id")
        payload["response_status"] = _response_attr(response, "status")
        payload["output_text"] = _response_output_text(response)
        return payload
    except Exception as exc:  # pragma: no cover - defensive envelope for live probes
        payload["live_call_executed"] = True
        payload["status"] = "error"
        payload["error_type"] = exc.__class__.__name__
        payload["error_message"] = str(exc)
        return payload
