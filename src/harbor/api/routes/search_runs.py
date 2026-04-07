from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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


def _translate_key_error(exc: KeyError) -> HTTPException:
    key = str(exc)
    if key == "'project_not_found'":
        return HTTPException(status_code=404, detail="Project not found.")
    if key == "'search_campaign_not_found'":
        return HTTPException(status_code=404, detail="Search campaign not found.")
    return HTTPException(status_code=404, detail="Search run not found.")


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
    try:
        record = create_search_run(session, project_id, search_campaign_id, payload)
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
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
    try:
        items = [
            SearchRunRead.from_record(record)
            for record in list_search_runs(session, project_id, search_campaign_id)
        ]
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
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
        raise HTTPException(status_code=404, detail="Search run not found.")
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
    try:
        record = update_search_run_status(
            session,
            project_id,
            search_campaign_id,
            search_run_id,
            payload,
        )
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
    return SearchRunRead.from_record(record)
