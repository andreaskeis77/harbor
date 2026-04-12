from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from harbor.exceptions import DuplicateError, InvalidPayloadError, NotFoundError
from harbor.persistence.models import ProjectSourceRecord, SourceRecord
from harbor.project_registry import get_project

ALLOWED_PROJECT_SOURCE_REVIEW_STATUSES: frozenset[str] = frozenset(
    {"candidate", "accepted", "rejected"}
)


class SourceCreate(BaseModel):
    source_type: str = Field(min_length=1, max_length=32)
    title: str | None = Field(default=None, max_length=300)
    canonical_url: str | None = Field(default=None, max_length=1000)
    content_type: str | None = Field(default=None, max_length=100)
    trust_tier: str = Field(default="candidate", min_length=1, max_length=32)


class SourceRead(BaseModel):
    source_id: str
    source_type: str
    title: str | None
    canonical_url: str | None
    content_type: str | None
    trust_tier: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: SourceRecord) -> SourceRead:
        return cls(
            source_id=record.source_id,
            source_type=record.source_type,
            title=record.title,
            canonical_url=record.canonical_url,
            content_type=record.content_type,
            trust_tier=record.trust_tier,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class SourceListResponse(BaseModel):
    items: list[SourceRead]


class ProjectSourceCreate(BaseModel):
    source_id: str
    relevance: str = Field(default="candidate", min_length=1, max_length=32)
    review_status: str = Field(default="candidate", min_length=1, max_length=32)
    note: str | None = None


class ProjectSourceRead(BaseModel):
    project_source_id: str
    project_id: str
    source_id: str
    relevance: str
    review_status: str
    note: str | None
    created_at: datetime
    updated_at: datetime
    source: SourceRead

    @classmethod
    def from_records(
        cls,
        project_source: ProjectSourceRecord,
        source: SourceRecord,
    ) -> ProjectSourceRead:
        return cls(
            project_source_id=project_source.project_source_id,
            project_id=project_source.project_id,
            source_id=project_source.source_id,
            relevance=project_source.relevance,
            review_status=project_source.review_status,
            note=project_source.note,
            created_at=project_source.created_at,
            updated_at=project_source.updated_at,
            source=SourceRead.from_record(source),
        )


class ProjectSourceListResponse(BaseModel):
    items: list[ProjectSourceRead]


class ProjectSourceReviewUpdate(BaseModel):
    review_status: str = Field(min_length=1, max_length=32)
    note: str | None = None


def create_source(session: Session, payload: SourceCreate) -> SourceRecord:
    record = SourceRecord(
        source_type=payload.source_type,
        title=payload.title,
        canonical_url=payload.canonical_url,
        content_type=payload.content_type,
        trust_tier=payload.trust_tier,
    )
    session.add(record)
    try:
        session.flush()
    except IntegrityError as exc:
        raise DuplicateError("Source") from exc
    session.refresh(record)
    return record


def list_sources(session: Session) -> list[SourceRecord]:
    stmt = select(SourceRecord).order_by(
        SourceRecord.created_at.desc(),
        SourceRecord.source_id.desc(),
    )
    return list(session.execute(stmt).scalars().all())


def attach_source_to_project(
    session: Session,
    project_id: str,
    payload: ProjectSourceCreate,
) -> tuple[ProjectSourceRecord, SourceRecord]:
    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)

    source = session.get(SourceRecord, payload.source_id)
    if source is None:
        raise NotFoundError("Source", payload.source_id)

    record = ProjectSourceRecord(
        project_id=project_id,
        source_id=payload.source_id,
        relevance=payload.relevance,
        review_status=payload.review_status,
        note=payload.note,
    )
    session.add(record)
    try:
        session.flush()
    except IntegrityError as exc:
        raise DuplicateError("ProjectSource", "Source already attached to project.") from exc
    session.refresh(record)
    return record, source


def update_project_source_review_status(
    session: Session,
    project_id: str,
    project_source_id: str,
    payload: ProjectSourceReviewUpdate,
) -> tuple[ProjectSourceRecord, SourceRecord]:
    if payload.review_status not in ALLOWED_PROJECT_SOURCE_REVIEW_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_PROJECT_SOURCE_REVIEW_STATUSES))
        raise InvalidPayloadError(
            "ProjectSource",
            f"review_status must be one of: {allowed}",
        )

    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)

    record = session.get(ProjectSourceRecord, project_source_id)
    if record is None or record.project_id != project_id:
        raise NotFoundError("ProjectSource", project_source_id)

    record.review_status = payload.review_status
    if payload.note is not None:
        record.note = payload.note

    session.add(record)
    session.flush()
    session.refresh(record)

    source = session.get(SourceRecord, record.source_id)
    if source is None:
        raise NotFoundError("Source", record.source_id)
    return record, source


def list_project_sources(
    session: Session,
    project_id: str,
) -> list[tuple[ProjectSourceRecord, SourceRecord]]:
    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)

    stmt = (
        select(ProjectSourceRecord, SourceRecord)
        .join(SourceRecord, SourceRecord.source_id == ProjectSourceRecord.source_id)
        .where(ProjectSourceRecord.project_id == project_id)
        .order_by(
            ProjectSourceRecord.created_at.desc(),
            ProjectSourceRecord.project_source_id.desc(),
        )
    )
    return list(session.execute(stmt).all())
