from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from importlib.util import find_spec
from typing import Any

from harbor.config import HarborSettings, get_settings

ClientFactory = Callable[[HarborSettings], object]

DEFAULT_PROJECT_DRY_RUN_INSTRUCTIONS = (
    "You are assisting a Harbor research operator. Use only the supplied project context "
    "and the explicit operator request. Do not invent missing facts. If context is missing, "
    "say so briefly."
)

DEFAULT_PROJECT_CHAT_TURN_INSTRUCTIONS = (
    "You are Harbor chat assistant for a research operator. Use the supplied project context "
    "and any provided prior chat turns. Keep the answer compact and do not invent missing facts."
)


MAX_PROJECT_CONTEXT_VALUE_CHARS = 240
MAX_CHAT_HISTORY_TURNS = 6
MAX_CHAT_HISTORY_OPERATOR_CHARS = 240
MAX_CHAT_HISTORY_ASSISTANT_CHARS = 320
MAX_PROJECT_SOURCES_IN_CHAT_CONTEXT = 6
MAX_HANDBOOK_CHARS = 2000
TRUNCATION_SUFFIX = " …[truncated]"

SOURCE_CITATION_INSTRUCTION = (
    " When referencing information from the project sources, cite them by number "
    "(e.g. [1], [2])."
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


def _collapse_whitespace(value: object) -> str:
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text


def _truncate_text(value: object, *, max_chars: int) -> tuple[str, bool]:
    text = _collapse_whitespace(value)
    if len(text) <= max_chars:
        return text, False

    if max_chars <= len(TRUNCATION_SUFFIX):
        return text[:max_chars], True

    clipped = text[: max_chars - len(TRUNCATION_SUFFIX)].rstrip()
    return f"{clipped}{TRUNCATION_SUFFIX}", True


def _context_value(project_context: Mapping[str, object], key: str) -> str:
    value = project_context.get(key)
    if value is None or value == "":
        return "(none)"
    compact, _ = _truncate_text(value, max_chars=MAX_PROJECT_CONTEXT_VALUE_CHARS)
    return compact


def _prepare_prior_chat_turns(
    prior_turns: list[Mapping[str, object]] | None,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    turns = list(prior_turns or [])
    total_count = len(turns)
    included_turns = turns[-MAX_CHAT_HISTORY_TURNS:] if turns else []
    omitted_count = total_count - len(included_turns)
    history_compacted = omitted_count > 0

    prepared: list[dict[str, object]] = []
    start_index = omitted_count + 1
    for offset, turn in enumerate(included_turns):
        operator_text, operator_truncated = _truncate_text(
            turn.get("request_input_text") or "(none)",
            max_chars=MAX_CHAT_HISTORY_OPERATOR_CHARS,
        )
        assistant_source = turn.get("output_text") or turn.get("error_message") or "(no response)"
        assistant_text, assistant_truncated = _truncate_text(
            assistant_source,
            max_chars=MAX_CHAT_HISTORY_ASSISTANT_CHARS,
        )
        history_compacted = history_compacted or operator_truncated or assistant_truncated
        prepared.append(
            {
                "turn_index": start_index + offset,
                "operator_text": operator_text,
                "assistant_text": assistant_text,
            }
        )

    return prepared, {
        "prior_turn_count": total_count,
        "prior_turn_count_included": len(prepared),
        "prior_turn_count_omitted": omitted_count,
        "history_compacted": history_compacted,
    }

def _prepare_project_sources(
    project_sources: list[Mapping[str, object]] | None,
) -> tuple[list[dict[str, str]], dict[str, int]]:
    sources = list(project_sources or [])
    included_sources = sources[:MAX_PROJECT_SOURCES_IN_CHAT_CONTEXT]

    prepared: list[dict[str, str]] = []
    for source in included_sources:
        source_payload = source.get("source")
        source_mapping = source_payload if isinstance(source_payload, Mapping) else {}
        title = _collapse_whitespace(source_mapping.get("title") or "(untitled source)")
        canonical_url = _collapse_whitespace(
            source_mapping.get("canonical_url") or "(no canonical url)"
        )
        note_value = source.get("note")
        note = ""
        if note_value not in (None, ""):
            note = _collapse_whitespace(note_value)
        entry: dict[str, str] = {
            "title": title,
            "canonical_url": canonical_url,
            "note": note,
        }
        source_id = source_mapping.get("source_id")
        if source_id is not None:
            entry["source_id"] = str(source_id)
        project_source_id = source.get("project_source_id")
        if project_source_id is not None:
            entry["project_source_id"] = str(project_source_id)

        relevance = source.get("relevance")
        if relevance is not None:
            entry["relevance"] = str(relevance)
        trust_tier = source_mapping.get("trust_tier")
        if trust_tier is not None:
            entry["trust_tier"] = str(trust_tier)
        review_status = source.get("review_status")
        if review_status is not None:
            entry["review_status"] = str(review_status)

        prepared.append(entry)

    return prepared, {
        "project_source_count_available": len(sources),
        "project_source_count_included": len(prepared),
    }


def _project_sources_lines(project_sources: list[dict[str, str]]) -> list[str]:
    lines = ["Project sources", ""]

    if not project_sources:
        lines.append("(no accepted project sources available)")
        return lines

    for index, source in enumerate(project_sources, start=1):
        lines.append(f"{index}. {source['title']}")
        lines.append(f"   URL: {source['canonical_url']}")
        meta_parts: list[str] = []
        if source.get("relevance"):
            meta_parts.append(f"relevance={source['relevance']}")
        if source.get("trust_tier"):
            meta_parts.append(f"trust={source['trust_tier']}")
        if source.get("review_status"):
            meta_parts.append(f"review={source['review_status']}")
        if meta_parts:
            lines.append(f"   [{', '.join(meta_parts)}]")
        if source["note"]:
            lines.append(f"   Note: {source['note']}")
        if index < len(project_sources):
            lines.append("")

    lines.append("")
    lines.append("Cite sources by number (e.g. [1], [2]) when referencing them.")

    return lines


def _prepare_handbook_context(
    handbook_markdown: str | None,
) -> tuple[str, dict[str, object]]:
    if not handbook_markdown or not handbook_markdown.strip():
        return "", {"handbook_available": False, "handbook_chars": 0, "handbook_truncated": False}

    text = handbook_markdown.strip()
    truncated_text, was_truncated = _truncate_text(text, max_chars=MAX_HANDBOOK_CHARS)
    return truncated_text, {
        "handbook_available": True,
        "handbook_chars": len(text),
        "handbook_truncated": was_truncated,
    }


def _handbook_context_lines(handbook_text: str) -> list[str]:
    lines = ["Project handbook", ""]

    if not handbook_text:
        lines.append("(no handbook available for this project)")
        return lines

    lines.append(handbook_text)
    return lines


def _extract_source_citations(
    output_text: str | None,
    prepared_sources: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Extract cited sources from assistant output text.

    Scans for [N] patterns and maps them back to the prepared source list.
    Returns the subset of sources that were actually cited, preserving order.
    """
    if not output_text or not prepared_sources:
        return []

    cited_indices: set[int] = set()
    for match in re.finditer(r"\[(\d+)]", output_text):
        index = int(match.group(1))
        if 1 <= index <= len(prepared_sources):
            cited_indices.add(index)

    return [
        prepared_sources[i - 1]
        for i in sorted(cited_indices)
    ]


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


def build_project_chat_turn_input(
    project_context: Mapping[str, object],
    input_text: str,
    *,
    prior_turns: list[Mapping[str, object]] | None = None,
    project_sources: list[Mapping[str, object]] | None = None,
    handbook_markdown: str | None = None,
) -> str:
    prepared_turns, history_meta = _prepare_prior_chat_turns(prior_turns)
    prepared_sources, _ = _prepare_project_sources(project_sources)
    handbook_text, _ = _prepare_handbook_context(handbook_markdown)
    lines = [
        "Harbor project context:",
        f"- project_id: {_context_value(project_context, 'project_id')}",
        f"- title: {_context_value(project_context, 'title')}",
        f"- short_description: {_context_value(project_context, 'short_description')}",
        f"- status: {_context_value(project_context, 'status')}",
        f"- project_type: {_context_value(project_context, 'project_type')}",
        f"- blueprint_status: {_context_value(project_context, 'blueprint_status')}",
        "",
        *_handbook_context_lines(handbook_text),
        "",
        *_project_sources_lines(prepared_sources),
        "",
    ]

    if prepared_turns:
        lines.extend(
            [
                "Prior chat turns:",
                f"- total_available: {history_meta['prior_turn_count']}",
                f"- included: {history_meta['prior_turn_count_included']}",
                f"- omitted: {history_meta['prior_turn_count_omitted']}",
            ]
        )
        if history_meta["history_compacted"]:
            lines.append("- note: Earlier or longer turns were compacted.")
        lines.append("")
        for turn in prepared_turns:
            lines.extend(
                [
                    f"Turn {turn['turn_index']}:",
                    f"Operator: {turn['operator_text']}",
                    f"Assistant: {turn['assistant_text']}",
                    "",
                ]
            )

    lines.extend(["Current operator message:", input_text.strip()])
    return "\n".join(lines)


def openai_project_chat_turn_payload(
    settings: HarborSettings | None = None,
    *,
    project_context: Mapping[str, object],
    input_text: str,
    prior_turns: list[Mapping[str, object]] | None = None,
    project_sources: list[Mapping[str, object]] | None = None,
    handbook_markdown: str | None = None,
    instructions: str | None = None,
    client_factory: ClientFactory | None = None,
) -> dict[str, object]:
    settings = settings or get_settings()
    effective_instructions = instructions or DEFAULT_PROJECT_CHAT_TURN_INSTRUCTIONS
    instructions_source = "custom" if instructions else "default"
    _, history_meta = _prepare_prior_chat_turns(prior_turns)
    prepared_sources, source_meta = _prepare_project_sources(project_sources)
    _, handbook_meta = _prepare_handbook_context(handbook_markdown)
    if prepared_sources:
        effective_instructions = effective_instructions + SOURCE_CITATION_INSTRUCTION
    rendered_input_text = build_project_chat_turn_input(
        project_context,
        input_text,
        prior_turns=prior_turns,
        project_sources=project_sources,
        handbook_markdown=handbook_markdown,
    )
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
            **history_meta,
        },
        "request_metadata": {**source_meta, **handbook_meta},
        "source_attribution": prepared_sources,
        "cited_sources": [],
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
        output_text = _response_output_text(response)
        payload["output_text"] = output_text
        payload["cited_sources"] = _extract_source_citations(output_text, prepared_sources)
        return payload
    except Exception as exc:  # pragma: no cover - defensive envelope for chat turns
        payload["status"] = "error"
        payload["error_type"] = exc.__class__.__name__
        payload["error_message"] = str(exc)
        return payload


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
