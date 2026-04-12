"""Automation task observability registry.

Records automation-triggered work with a simple state machine:
    pending -> running -> succeeded | failed

The registry CRUD functions participate in the caller's session. The
``*_observer`` helpers at the bottom open a short-lived side-channel
session so task records survive rollback of the request transaction.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from harbor.exceptions import InvalidPayloadError, NotFoundError
from harbor.persistence.models import AutomationTaskRecord, utcnow
from harbor.persistence.session import DatabaseNotConfiguredError, get_session_factory
from harbor.project_registry import get_project

ALLOWED_TRIGGER_SOURCES: frozenset[str] = frozenset({"manual", "scheduled", "webhook"})
TERMINAL_STATUSES: frozenset[str] = frozenset({"succeeded", "failed"})


class AutomationTaskCreate(BaseModel):
    project_id: str | None = None
    task_kind: str = Field(min_length=1, max_length=64)
    trigger_source: str = Field(min_length=1, max_length=32)


class AutomationTaskRead(BaseModel):
    automation_task_id: str
    project_id: str | None
    task_kind: str
    trigger_source: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    result_summary: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: AutomationTaskRecord) -> AutomationTaskRead:
        return cls(
            automation_task_id=record.automation_task_id,
            project_id=record.project_id,
            task_kind=record.task_kind,
            trigger_source=record.trigger_source,
            status=record.status,
            started_at=record.started_at,
            completed_at=record.completed_at,
            result_summary=record.result_summary,
            error_message=record.error_message,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class AutomationTaskListResponse(BaseModel):
    items: list[AutomationTaskRead]


def create_automation_task(
    session: Session,
    payload: AutomationTaskCreate,
) -> AutomationTaskRecord:
    if payload.trigger_source not in ALLOWED_TRIGGER_SOURCES:
        allowed = ", ".join(sorted(ALLOWED_TRIGGER_SOURCES))
        raise InvalidPayloadError(
            "AutomationTask",
            f"trigger_source must be one of: {allowed}",
        )
    if payload.project_id is not None:
        project = get_project(session, payload.project_id)
        if project is None:
            raise NotFoundError("Project", payload.project_id)

    record = AutomationTaskRecord(
        project_id=payload.project_id,
        task_kind=payload.task_kind,
        trigger_source=payload.trigger_source,
        status="pending",
    )
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def _require_task(session: Session, automation_task_id: str) -> AutomationTaskRecord:
    record = session.get(AutomationTaskRecord, automation_task_id)
    if record is None:
        raise NotFoundError("AutomationTask", automation_task_id)
    return record


def _reject_terminal(record: AutomationTaskRecord) -> None:
    if record.status in TERMINAL_STATUSES:
        raise InvalidPayloadError(
            "AutomationTask",
            f"task is already in terminal status '{record.status}'",
        )


def mark_automation_task_running(
    session: Session,
    automation_task_id: str,
) -> AutomationTaskRecord:
    record = _require_task(session, automation_task_id)
    _reject_terminal(record)
    if record.status != "pending":
        raise InvalidPayloadError(
            "AutomationTask",
            f"cannot transition from '{record.status}' to 'running'",
        )
    record.status = "running"
    record.started_at = utcnow()
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def mark_automation_task_succeeded(
    session: Session,
    automation_task_id: str,
    result_summary: str | None = None,
) -> AutomationTaskRecord:
    record = _require_task(session, automation_task_id)
    _reject_terminal(record)
    record.status = "succeeded"
    record.completed_at = utcnow()
    if record.started_at is None:
        record.started_at = record.completed_at
    if result_summary is not None:
        record.result_summary = result_summary
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def mark_automation_task_failed(
    session: Session,
    automation_task_id: str,
    error_message: str,
) -> AutomationTaskRecord:
    record = _require_task(session, automation_task_id)
    _reject_terminal(record)
    record.status = "failed"
    record.completed_at = utcnow()
    if record.started_at is None:
        record.started_at = record.completed_at
    record.error_message = error_message
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def get_automation_task(
    session: Session,
    automation_task_id: str,
) -> AutomationTaskRecord:
    return _require_task(session, automation_task_id)


def list_automation_tasks_for_project(
    session: Session,
    project_id: str,
) -> list[AutomationTaskRecord]:
    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)
    stmt = (
        select(AutomationTaskRecord)
        .where(AutomationTaskRecord.project_id == project_id)
        .order_by(
            AutomationTaskRecord.created_at.desc(),
            AutomationTaskRecord.automation_task_id.desc(),
        )
    )
    return list(session.execute(stmt).scalars().all())


RECENT_SCHEDULED_TASKS_LIMIT_CAP = 200
RECENT_SCHEDULED_TASKS_LIMIT_DEFAULT = 50


def list_recent_scheduled_tasks(
    session: Session,
    limit: int = RECENT_SCHEDULED_TASKS_LIMIT_DEFAULT,
) -> list[AutomationTaskRecord]:
    capped = max(1, min(limit, RECENT_SCHEDULED_TASKS_LIMIT_CAP))
    stmt = (
        select(AutomationTaskRecord)
        .where(AutomationTaskRecord.trigger_source == "scheduled")
        .order_by(
            AutomationTaskRecord.created_at.desc(),
            AutomationTaskRecord.automation_task_id.desc(),
        )
        .limit(capped)
    )
    return list(session.execute(stmt).scalars().all())


def _resolve_factory(
    session_factory: sessionmaker[Session] | None,
) -> sessionmaker[Session]:
    factory = session_factory or get_session_factory()
    if factory is None:
        raise DatabaseNotConfiguredError
    return factory


def start_automation_task_observer(
    payload: AutomationTaskCreate,
    session_factory: sessionmaker[Session] | None = None,
) -> str:
    """Create a task and mark it running in a side-channel session.

    Why: the returned task id lets the caller record a terminal state from
    outside the request transaction, so a failed request still leaves a
    ``failed`` row behind instead of a rolled-back blank.
    """
    factory = _resolve_factory(session_factory)
    session = factory()
    try:
        record = create_automation_task(session, payload)
        mark_automation_task_running(session, record.automation_task_id)
        task_id = record.automation_task_id
        session.commit()
        return task_id
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def complete_automation_task_observer(
    automation_task_id: str,
    result_summary: str | None = None,
    session_factory: sessionmaker[Session] | None = None,
) -> None:
    factory = _resolve_factory(session_factory)
    session = factory()
    try:
        mark_automation_task_succeeded(
            session,
            automation_task_id,
            result_summary=result_summary,
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def fail_automation_task_observer(
    automation_task_id: str,
    error_message: str,
    session_factory: sessionmaker[Session] | None = None,
) -> None:
    factory = _resolve_factory(session_factory)
    session = factory()
    try:
        mark_automation_task_failed(session, automation_task_id, error_message)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
