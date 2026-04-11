from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.exceptions import InvalidPayloadError, NotFoundError
from harbor.persistence.models import (
    OpenAIProjectChatSessionRecord,
    OpenAIProjectChatTurnRecord,
)
from harbor.project_registry import get_project


class OpenAIProjectChatSessionRead(BaseModel):
    openai_project_chat_session_id: str
    project_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    turn_count: int
    last_status: str | None
    last_model: str | None
    last_response_id: str | None
    last_input_text: str | None
    last_output_text: str | None

    @classmethod
    def from_record(
        cls,
        record: OpenAIProjectChatSessionRecord,
        *,
        turns: list[OpenAIProjectChatTurnRecord] | None = None,
    ) -> OpenAIProjectChatSessionRead:
        turns = turns or []
        last_turn = turns[-1] if turns else None
        return cls(
            openai_project_chat_session_id=record.openai_project_chat_session_id,
            project_id=record.project_id,
            title=record.title,
            created_at=record.created_at,
            updated_at=record.updated_at,
            turn_count=len(turns),
            last_status=last_turn.status if last_turn else None,
            last_model=last_turn.model if last_turn else None,
            last_response_id=last_turn.response_id if last_turn else None,
            last_input_text=last_turn.request_input_text if last_turn else None,
            last_output_text=(
                (last_turn.output_text or last_turn.error_message) if last_turn else None
            ),
        )


class OpenAIProjectChatTurnRead(BaseModel):
    openai_project_chat_turn_id: str
    openai_project_chat_session_id: str
    project_id: str
    turn_index: int
    provider: str
    model: str | None
    status: str
    response_id: str | None
    response_status: str | None
    request_input_text: str
    rendered_input_text: str
    output_text: str | None
    error_type: str | None
    error_message: str | None
    source_attribution: list[dict[str, str]] | None
    created_at: datetime

    @classmethod
    def from_record(
        cls,
        record: OpenAIProjectChatTurnRecord,
    ) -> OpenAIProjectChatTurnRead:
        source_attribution = None
        if record.source_attribution is not None:
            try:
                source_attribution = json.loads(record.source_attribution)
            except (json.JSONDecodeError, TypeError):
                source_attribution = None
        return cls(
            openai_project_chat_turn_id=record.openai_project_chat_turn_id,
            openai_project_chat_session_id=record.openai_project_chat_session_id,
            project_id=record.project_id,
            turn_index=record.turn_index,
            provider=record.provider,
            model=record.model,
            status=record.status,
            response_id=record.response_id,
            response_status=record.response_status,
            request_input_text=record.request_input_text,
            rendered_input_text=record.rendered_input_text,
            output_text=record.output_text,
            error_type=record.error_type,
            error_message=record.error_message,
            source_attribution=source_attribution,
            created_at=record.created_at,
        )


class OpenAIProjectChatSessionListResponse(BaseModel):
    items: list[OpenAIProjectChatSessionRead]


class OpenAIProjectChatTurnListResponse(BaseModel):
    items: list[OpenAIProjectChatTurnRead]


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _serialize_source_attribution(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return json.dumps(value)
    return None


def _session_title_from_input(input_text: str) -> str:
    compact = " ".join(input_text.split())
    if len(compact) <= 80:
        return compact
    return f"{compact[:77].rstrip()}..."


def create_openai_project_chat_session(
    session: Session,
    project_id: str,
    *,
    title: str,
) -> OpenAIProjectChatSessionRecord:
    if get_project(session, project_id) is None:
        raise NotFoundError("Project", project_id)

    record = OpenAIProjectChatSessionRecord(project_id=project_id, title=title)
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def get_openai_project_chat_session(
    session: Session,
    project_id: str,
    chat_session_id: str,
) -> OpenAIProjectChatSessionRecord | None:
    if get_project(session, project_id) is None:
        raise NotFoundError("Project", project_id)

    stmt = select(OpenAIProjectChatSessionRecord).where(
        OpenAIProjectChatSessionRecord.project_id == project_id,
        OpenAIProjectChatSessionRecord.openai_project_chat_session_id == chat_session_id,
    )
    return session.execute(stmt).scalar_one_or_none()


def list_openai_project_chat_turns(
    session: Session,
    project_id: str,
    chat_session_id: str,
) -> list[OpenAIProjectChatTurnRecord]:
    if get_project(session, project_id) is None:
        raise NotFoundError("Project", project_id)

    stmt = (
        select(OpenAIProjectChatTurnRecord)
        .where(
            OpenAIProjectChatTurnRecord.project_id == project_id,
            OpenAIProjectChatTurnRecord.openai_project_chat_session_id == chat_session_id,
        )
        .order_by(
            OpenAIProjectChatTurnRecord.turn_index.asc(),
            OpenAIProjectChatTurnRecord.created_at.asc(),
        )
    )
    return list(session.execute(stmt).scalars().all())


def list_openai_project_chat_sessions(
    session: Session,
    project_id: str,
) -> list[OpenAIProjectChatSessionRead]:
    if get_project(session, project_id) is None:
        raise NotFoundError("Project", project_id)

    sessions_stmt = (
        select(OpenAIProjectChatSessionRecord)
        .where(OpenAIProjectChatSessionRecord.project_id == project_id)
        .order_by(
            OpenAIProjectChatSessionRecord.updated_at.desc(),
            OpenAIProjectChatSessionRecord.openai_project_chat_session_id.desc(),
        )
    )
    session_records = list(session.execute(sessions_stmt).scalars().all())

    items: list[OpenAIProjectChatSessionRead] = []
    for record in session_records:
        turns = list_openai_project_chat_turns(
            session,
            project_id,
            record.openai_project_chat_session_id,
        )
        items.append(OpenAIProjectChatSessionRead.from_record(record, turns=turns))
    return items


def ensure_openai_project_chat_session(
    session: Session,
    project_id: str,
    *,
    chat_session_id: str | None,
    input_text: str,
) -> OpenAIProjectChatSessionRecord:
    if chat_session_id:
        record = get_openai_project_chat_session(session, project_id, chat_session_id)
        if record is None:
            raise NotFoundError("Chat session", chat_session_id)
        return record

    return create_openai_project_chat_session(
        session,
        project_id,
        title=_session_title_from_input(input_text),
    )


def create_openai_project_chat_turn(
    session: Session,
    project_id: str,
    chat_session_id: str,
    payload: dict[str, object],
) -> OpenAIProjectChatTurnRecord:
    if get_project(session, project_id) is None:
        raise NotFoundError("Project", project_id)

    session_record = get_openai_project_chat_session(session, project_id, chat_session_id)
    if session_record is None:
        raise NotFoundError("Chat session", chat_session_id)

    request_payload = payload.get("request")
    if not isinstance(request_payload, dict):
        raise InvalidPayloadError("Chat turn", "missing or invalid request payload")

    input_text = request_payload.get("input_text")
    rendered_input_text = request_payload.get("rendered_input_text")
    if not isinstance(input_text, str) or not isinstance(rendered_input_text, str):
        raise InvalidPayloadError("Chat turn", "missing or invalid request payload")

    existing_turns = list_openai_project_chat_turns(session, project_id, chat_session_id)
    next_turn_index = len(existing_turns) + 1

    record = OpenAIProjectChatTurnRecord(
        project_id=project_id,
        openai_project_chat_session_id=chat_session_id,
        turn_index=next_turn_index,
        provider=str(payload.get("provider") or "openai"),
        model=_optional_text(payload.get("model")),
        status=str(payload.get("status") or "unknown"),
        response_id=_optional_text(payload.get("response_id")),
        response_status=_optional_text(payload.get("response_status")),
        request_input_text=input_text,
        rendered_input_text=rendered_input_text,
        output_text=_optional_text(payload.get("output_text")),
        error_type=_optional_text(payload.get("error_type")),
        error_message=_optional_text(payload.get("error_message")),
        source_attribution=_serialize_source_attribution(payload.get("source_attribution")),
    )
    session_record.updated_at = datetime.now(UTC)
    session.add(record)
    session.add(session_record)
    session.flush()
    session.refresh(record)
    session.refresh(session_record)
    return record
