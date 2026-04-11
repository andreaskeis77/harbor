from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.persistence.models import ProjectRecord

ProjectStatus = Literal["draft", "active_research", "review", "archived"]
ProjectType = Literal["quick", "standard", "deep"]
BlueprintStatus = Literal["not_blueprint", "eligible", "blueprint"]


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    short_description: str | None = None
    status: ProjectStatus = "draft"
    project_type: ProjectType = "standard"
    blueprint_status: BlueprintStatus = "not_blueprint"


class ProjectRead(BaseModel):
    project_id: str
    title: str
    short_description: str | None
    status: str
    project_type: str
    blueprint_status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: ProjectRecord) -> ProjectRead:
        return cls(
            project_id=record.project_id,
            title=record.title,
            short_description=record.short_description,
            status=record.status,
            project_type=record.project_type,
            blueprint_status=record.blueprint_status,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class ProjectListResponse(BaseModel):
    items: list[ProjectRead]


def create_project(session: Session, payload: ProjectCreate) -> ProjectRecord:
    record = ProjectRecord(
        title=payload.title,
        short_description=payload.short_description,
        status=payload.status,
        project_type=payload.project_type,
        blueprint_status=payload.blueprint_status,
    )
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def list_projects(session: Session) -> list[ProjectRecord]:
    stmt = select(ProjectRecord).order_by(
        ProjectRecord.created_at.desc(),
        ProjectRecord.project_id.desc(),
    )
    return list(session.execute(stmt).scalars().all())


def get_project(session: Session, project_id: str) -> ProjectRecord | None:
    stmt = select(ProjectRecord).where(ProjectRecord.project_id == project_id)
    return session.execute(stmt).scalar_one_or_none()
