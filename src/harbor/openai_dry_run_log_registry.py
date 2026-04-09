from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.persistence.models import OpenAIProjectDryRunLogRecord
from harbor.project_registry import get_project


class OpenAIProjectDryRunLogRead(BaseModel):
    openai_project_dry_run_log_id: str
    project_id: str
    provider: str
    model: str | None
    status: str
    response_id: str | None
    response_status: str | None
    request_input_text: str
    request_instructions: str | None
    request_instructions_source: str | None
    rendered_input_text: str
    output_text: str | None
    error_type: str | None
    error_message: str | None
    created_at: datetime

    @classmethod
    def from_record(
        cls, record: OpenAIProjectDryRunLogRecord
    ) -> "OpenAIProjectDryRunLogRead":
        return cls(
            openai_project_dry_run_log_id=record.openai_project_dry_run_log_id,
            project_id=record.project_id,
            provider=record.provider,
            model=record.model,
            status=record.status,
            response_id=record.response_id,
            response_status=record.response_status,
            request_input_text=record.request_input_text,
            request_instructions=record.request_instructions,
            request_instructions_source=record.request_instructions_source,
            rendered_input_text=record.rendered_input_text,
            output_text=record.output_text,
            error_type=record.error_type,
            error_message=record.error_message,
            created_at=record.created_at,
        )


class OpenAIProjectDryRunLogListResponse(BaseModel):
    items: list[OpenAIProjectDryRunLogRead]


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def create_openai_project_dry_run_log(
    session: Session,
    project_id: str,
    payload: dict[str, object],
) -> OpenAIProjectDryRunLogRecord:
    if get_project(session, project_id) is None:
        raise KeyError("project_not_found")

    request_payload = payload.get("request")
    if not isinstance(request_payload, dict):
        raise ValueError("invalid_openai_project_dry_run_payload")

    input_text = request_payload.get("input_text")
    rendered_input_text = request_payload.get("rendered_input_text")
    if not isinstance(input_text, str) or not isinstance(rendered_input_text, str):
        raise ValueError("invalid_openai_project_dry_run_payload")

    record = OpenAIProjectDryRunLogRecord(
        project_id=project_id,
        provider=str(payload.get("provider") or "openai"),
        model=_optional_text(payload.get("model")),
        status=str(payload.get("status") or "unknown"),
        response_id=_optional_text(payload.get("response_id")),
        response_status=_optional_text(payload.get("response_status")),
        request_input_text=input_text,
        request_instructions=_optional_text(request_payload.get("instructions")),
        request_instructions_source=_optional_text(
            request_payload.get("instructions_source")
        ),
        rendered_input_text=rendered_input_text,
        output_text=_optional_text(payload.get("output_text")),
        error_type=_optional_text(payload.get("error_type")),
        error_message=_optional_text(payload.get("error_message")),
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_openai_project_dry_run_logs(
    session: Session, project_id: str
) -> list[OpenAIProjectDryRunLogRecord]:
    if get_project(session, project_id) is None:
        raise KeyError("project_not_found")

    stmt = (
        select(OpenAIProjectDryRunLogRecord)
        .where(OpenAIProjectDryRunLogRecord.project_id == project_id)
        .order_by(
            OpenAIProjectDryRunLogRecord.created_at.desc(),
            OpenAIProjectDryRunLogRecord.openai_project_dry_run_log_id.desc(),
        )
    )
    return list(session.execute(stmt).scalars().all())
