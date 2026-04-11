from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.session import get_db_session
from harbor.search_run_registry import (
    SearchRunCreate,
    SearchRunListResponse,
    SearchRunRead,
    SearchRunStatusUpdate,
    create_search_run,
    get_search_run,
    list_search_runs,
    update_search_run_status,
)

router = APIRouter(tags=["search_runs"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}/runs",
    response_model=SearchRunRead,
    status_code=status.HTTP_201_CREATED,
)
def create_search_run_endpoint(
    project_id: str,
    search_campaign_id: str,
    payload: SearchRunCreate,
    session: DbSession,
) -> SearchRunRead:
    record = create_search_run(session, project_id, search_campaign_id, payload)
    return SearchRunRead.from_record(record)


@router.get(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}/runs",
    response_model=SearchRunListResponse,
)
def list_search_runs_endpoint(
    project_id: str,
    search_campaign_id: str,
    session: DbSession,
) -> SearchRunListResponse:
    items = [
        SearchRunRead.from_record(record)
        for record in list_search_runs(session, project_id, search_campaign_id)
    ]
    return SearchRunListResponse(items=items)


@router.get(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}",
    response_model=SearchRunRead,
)
def get_search_run_endpoint(
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    session: DbSession,
) -> SearchRunRead:
    record = get_search_run(session, project_id, search_campaign_id, search_run_id)
    if record is None:
        raise NotFoundError("Search run", search_run_id)
    return SearchRunRead.from_record(record)


@router.patch(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/status",
    response_model=SearchRunRead,
)
def update_search_run_status_endpoint(
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    payload: SearchRunStatusUpdate,
    session: DbSession,
) -> SearchRunRead:
    record = update_search_run_status(
        session,
        project_id,
        search_campaign_id,
        search_run_id,
        payload,
    )
    return SearchRunRead.from_record(record)
