"""Source snapshot registry.

Persists per-fetch results for a project-source: HTTP status, extracted
text, content hash, and optionally an error string. Content fetching
itself is a later bolt (T7.1); this module is the storage/CRUD surface.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.models import ProjectSourceRecord, SourceSnapshotRecord


class SourceSnapshotCreate(BaseModel):
    project_source_id: str = Field(min_length=1, max_length=36)
    http_status: int | None = None
    content_hash: str | None = Field(default=None, max_length=64)
    extracted_text: str | None = None
    fetch_error: str | None = None


class SourceSnapshotRead(BaseModel):
    source_snapshot_id: str
    project_source_id: str
    fetched_at: datetime
    http_status: int | None
    content_hash: str | None
    extracted_text: str | None
    fetch_error: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: SourceSnapshotRecord) -> SourceSnapshotRead:
        return cls(
            source_snapshot_id=record.source_snapshot_id,
            project_source_id=record.project_source_id,
            fetched_at=record.fetched_at,
            http_status=record.http_status,
            content_hash=record.content_hash,
            extracted_text=record.extracted_text,
            fetch_error=record.fetch_error,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class SourceSnapshotListResponse(BaseModel):
    items: list[SourceSnapshotRead]


def create_source_snapshot(
    session: Session,
    payload: SourceSnapshotCreate,
) -> SourceSnapshotRecord:
    project_source = session.get(ProjectSourceRecord, payload.project_source_id)
    if project_source is None:
        raise NotFoundError("ProjectSource", payload.project_source_id)

    record = SourceSnapshotRecord(
        project_source_id=payload.project_source_id,
        http_status=payload.http_status,
        content_hash=payload.content_hash,
        extracted_text=payload.extracted_text,
        fetch_error=payload.fetch_error,
    )
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def get_source_snapshot(
    session: Session,
    source_snapshot_id: str,
) -> SourceSnapshotRecord:
    record = session.get(SourceSnapshotRecord, source_snapshot_id)
    if record is None:
        raise NotFoundError("SourceSnapshot", source_snapshot_id)
    return record


def list_snapshots_for_project_source(
    session: Session,
    project_source_id: str,
) -> list[SourceSnapshotRecord]:
    project_source = session.get(ProjectSourceRecord, project_source_id)
    if project_source is None:
        raise NotFoundError("ProjectSource", project_source_id)
    stmt = (
        select(SourceSnapshotRecord)
        .where(SourceSnapshotRecord.project_source_id == project_source_id)
        .order_by(
            SourceSnapshotRecord.fetched_at.desc(),
            SourceSnapshotRecord.source_snapshot_id.desc(),
        )
    )
    return list(session.execute(stmt).scalars().all())


def get_latest_snapshot(
    session: Session,
    project_source_id: str,
) -> SourceSnapshotRecord | None:
    stmt = (
        select(SourceSnapshotRecord)
        .where(SourceSnapshotRecord.project_source_id == project_source_id)
        .order_by(
            SourceSnapshotRecord.fetched_at.desc(),
            SourceSnapshotRecord.source_snapshot_id.desc(),
        )
        .limit(1)
    )
    return session.execute(stmt).scalar_one_or_none()
