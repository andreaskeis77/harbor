from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.session import get_db_session
from harbor.search_campaign_registry import (
    SearchCampaignCreate,
    SearchCampaignListResponse,
    SearchCampaignRead,
    create_search_campaign,
    get_search_campaign,
    list_search_campaigns,
)

router = APIRouter(tags=["search_campaigns"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/projects/{project_id}/search-campaigns",
    response_model=SearchCampaignRead,
    status_code=status.HTTP_201_CREATED,
)
def create_search_campaign_endpoint(
    project_id: str,
    payload: SearchCampaignCreate,
    session: DbSession,
) -> SearchCampaignRead:
    record = create_search_campaign(session, project_id, payload)
    return SearchCampaignRead.from_record(record)


@router.get(
    "/projects/{project_id}/search-campaigns",
    response_model=SearchCampaignListResponse,
)
def list_search_campaigns_endpoint(
    project_id: str,
    session: DbSession,
) -> SearchCampaignListResponse:
    items = [
        SearchCampaignRead.from_record(record)
        for record in list_search_campaigns(session, project_id)
    ]
    return SearchCampaignListResponse(items=items)


@router.get(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}",
    response_model=SearchCampaignRead,
)
def get_search_campaign_endpoint(
    project_id: str,
    search_campaign_id: str,
    session: DbSession,
) -> SearchCampaignRead:
    record = get_search_campaign(session, project_id, search_campaign_id)
    if record is None:
        raise NotFoundError("Search campaign", search_campaign_id)
    return SearchCampaignRead.from_record(record)
