from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from harbor.persistence.session import get_db_session
from harbor.source_registry import (
    ProjectSourceCreate,
    ProjectSourceListResponse,
    ProjectSourceRead,
    SourceCreate,
    SourceListResponse,
    SourceRead,
    attach_source_to_project,
    create_source,
    list_project_sources,
    list_sources,
)

router = APIRouter(tags=["sources"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post("/sources", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_source_endpoint(payload: SourceCreate, session: DbSession) -> SourceRead:
    record = create_source(session, payload)
    return SourceRead.from_record(record)


@router.get("/sources", response_model=SourceListResponse)
def list_sources_endpoint(session: DbSession) -> SourceListResponse:
    items = [SourceRead.from_record(record) for record in list_sources(session)]
    return SourceListResponse(items=items)


@router.post(
    "/projects/{project_id}/sources",
    response_model=ProjectSourceRead,
    status_code=status.HTTP_201_CREATED,
)
def attach_source_endpoint(
    project_id: str,
    payload: ProjectSourceCreate,
    session: DbSession,
) -> ProjectSourceRead:
    project_source, source = attach_source_to_project(session, project_id, payload)
    return ProjectSourceRead.from_records(project_source, source)


@router.get("/projects/{project_id}/sources", response_model=ProjectSourceListResponse)
def list_project_sources_endpoint(project_id: str, session: DbSession) -> ProjectSourceListResponse:
    items = [
        ProjectSourceRead.from_records(project_source, source)
        for project_source, source in list_project_sources(session, project_id)
    ]
    return ProjectSourceListResponse(items=items)
