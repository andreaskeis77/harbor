from __future__ import annotations

from collections.abc import Mapping
from importlib.util import find_spec
from typing import Any, Callable

from harbor.config import HarborSettings, get_settings

ClientFactory = Callable[[HarborSettings], object]

DEFAULT_PROJECT_DRY_RUN_INSTRUCTIONS = (
    "You are assisting a Harbor research operator. Use only the supplied project context "
    "and the explicit operator request. Do not invent missing facts. If context is missing, "
    "say so briefly."
)


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


def _context_value(project_context: Mapping[str, object], key: str) -> str:
    value = project_context.get(key)
    if value is None or value == "":
        return "(none)"
    return str(value)


def build_project_dry_run_input(
    project_context: Mapping[str, object],
    input_text: str,
) -> str:
    return "\n".join(
        [
            "Harbor project context:",
            f"- project_id: {_context_value(project_context, 'project_id')}",
            f"- title: {_context_value(project_context, 'title')}",
            f"- short_description: {_context_value(project_context, 'short_description')}",
            f"- status: {_context_value(project_context, 'status')}",
            f"- project_type: {_context_value(project_context, 'project_type')}",
            f"- blueprint_status: {_context_value(project_context, 'blueprint_status')}",
            "",
            "Operator request:",
            input_text,
        ]
    )


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


def openai_project_dry_run_payload(
    settings: HarborSettings | None = None,
    *,
    project_context: Mapping[str, object],
    input_text: str,
    instructions: str | None = None,
    client_factory: ClientFactory | None = None,
) -> dict[str, object]:
    settings = settings or get_settings()
    effective_instructions = instructions or DEFAULT_PROJECT_DRY_RUN_INSTRUCTIONS
    instructions_source = "custom" if instructions else "default"
    rendered_input_text = build_project_dry_run_input(project_context, input_text)
    payload: dict[str, object] = {
        **openai_runtime_payload(settings),
        "status": "pending",
        "project": dict(project_context),
        "request": {
            "instructions": effective_instructions,
            "instructions_source": instructions_source,
            "input_text": input_text,
            "rendered_input_text": rendered_input_text,
            "store": False,
        },
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

    try:
        client = build_openai_client(settings=settings, client_factory=client_factory)
        response = client.responses.create(
            model=settings.openai_model,
            instructions=effective_instructions,
            input=rendered_input_text,
            store=False,
        )
        payload["status"] = "completed"
        payload["response_id"] = _response_attr(response, "id")
        payload["response_status"] = _response_attr(response, "status")
        payload["output_text"] = _response_output_text(response)
        return payload
    except Exception as exc:  # pragma: no cover - defensive envelope for dry runs
        payload["status"] = "error"
        payload["error_type"] = exc.__class__.__name__
        payload["error_message"] = str(exc)
        return payload
