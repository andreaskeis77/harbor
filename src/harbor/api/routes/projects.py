from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.session import get_db_session
from harbor.project_registry import (
    ProjectCreate,
    ProjectListResponse,
    ProjectRead,
    create_project,
    get_project,
    list_projects,
)

router = APIRouter(tags=["projects"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(payload: ProjectCreate, session: DbSession) -> ProjectRead:
    record = create_project(session, payload)
    return ProjectRead.from_record(record)


@router.get("/projects", response_model=ProjectListResponse)
def list_projects_endpoint(session: DbSession) -> ProjectListResponse:
    items = [ProjectRead.from_record(record) for record in list_projects(session)]
    return ProjectListResponse(items=items)


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project_endpoint(project_id: str, session: DbSession) -> ProjectRead:
    record = get_project(session, project_id)
    if record is None:
        raise NotFoundError("Project", project_id)
    return ProjectRead.from_record(record)
