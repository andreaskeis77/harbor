from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from harbor.persistence.models import HandbookVersionRecord
from harbor.project_registry import ProjectRead, get_project


class HandbookVersionWrite(BaseModel):
    handbook_markdown: str = Field(min_length=1)
    change_note: str | None = None


class HandbookVersionRead(BaseModel):
    handbook_version_id: str
    project_id: str
    version_number: int
    handbook_markdown: str
    change_note: str | None
    created_at: datetime

    @classmethod
    def from_record(cls, record: HandbookVersionRecord) -> "HandbookVersionRead":
        return cls(
            handbook_version_id=record.handbook_version_id,
            project_id=record.project_id,
            version_number=record.version_number,
            handbook_markdown=record.handbook_markdown,
            change_note=record.change_note,
            created_at=record.created_at,
        )


class HandbookCurrentResponse(BaseModel):
    project: ProjectRead
    has_handbook: bool
    current: HandbookVersionRead | None


class HandbookVersionListResponse(BaseModel):
    project: ProjectRead
    items: list[HandbookVersionRead]


def get_current_handbook(session: Session, project_id: str) -> HandbookVersionRecord | None:
    stmt = (
        select(HandbookVersionRecord)
        .where(HandbookVersionRecord.project_id == project_id)
        .order_by(
            HandbookVersionRecord.version_number.desc(),
            HandbookVersionRecord.created_at.desc(),
            HandbookVersionRecord.handbook_version_id.desc(),
        )
    )
    return session.execute(stmt).scalars().first()


def list_handbook_versions(session: Session, project_id: str) -> list[HandbookVersionRecord]:
    stmt = (
        select(HandbookVersionRecord)
        .where(HandbookVersionRecord.project_id == project_id)
        .order_by(
            HandbookVersionRecord.version_number.desc(),
            HandbookVersionRecord.created_at.desc(),
            HandbookVersionRecord.handbook_version_id.desc(),
        )
    )
    return list(session.execute(stmt).scalars().all())


def create_handbook_version(
    session: Session,
    project_id: str,
    payload: HandbookVersionWrite,
) -> HandbookVersionRecord:
    current_max = session.execute(
        select(func.max(HandbookVersionRecord.version_number)).where(
            HandbookVersionRecord.project_id == project_id,
        )
    ).scalar_one()
    next_version = (current_max or 0) + 1

    record = HandbookVersionRecord(
        project_id=project_id,
        version_number=next_version,
        handbook_markdown=payload.handbook_markdown,
        change_note=payload.change_note,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def require_project_or_none(session: Session, project_id: str):
    return get_project(session, project_id)
