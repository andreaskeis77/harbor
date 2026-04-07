from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.persistence.models import SearchCampaignRecord
from harbor.project_registry import get_project


class SearchCampaignCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    query_text: str | None = None
    campaign_kind: str = "manual"
    status: str = "planned"
    note: str | None = None


class SearchCampaignRead(BaseModel):
    search_campaign_id: str
    project_id: str
    title: str
    query_text: str | None
    campaign_kind: str
    status: str
    note: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: SearchCampaignRecord) -> "SearchCampaignRead":
        return cls(
            search_campaign_id=record.search_campaign_id,
            project_id=record.project_id,
            title=record.title,
            query_text=record.query_text,
            campaign_kind=record.campaign_kind,
            status=record.status,
            note=record.note,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class SearchCampaignListResponse(BaseModel):
    items: list[SearchCampaignRead]


def create_search_campaign(
    session: Session,
    project_id: str,
    payload: SearchCampaignCreate,
) -> SearchCampaignRecord:
    project = get_project(session, project_id)
    if project is None:
        raise KeyError("project_not_found")

    record = SearchCampaignRecord(
        project_id=project_id,
        title=payload.title,
        query_text=payload.query_text,
        campaign_kind=payload.campaign_kind,
        status=payload.status,
        note=payload.note,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_search_campaigns(session: Session, project_id: str) -> list[SearchCampaignRecord]:
    project = get_project(session, project_id)
    if project is None:
        raise KeyError("project_not_found")

    stmt = (
        select(SearchCampaignRecord)
        .where(SearchCampaignRecord.project_id == project_id)
        .order_by(
            SearchCampaignRecord.created_at.desc(),
            SearchCampaignRecord.search_campaign_id.desc(),
        )
    )
    return list(session.execute(stmt).scalars().all())


def get_search_campaign(
    session: Session, project_id: str, search_campaign_id: str
) -> SearchCampaignRecord | None:
    stmt = (
        select(SearchCampaignRecord)
        .where(SearchCampaignRecord.project_id == project_id)
        .where(SearchCampaignRecord.search_campaign_id == search_campaign_id)
    )
    return session.execute(stmt).scalar_one_or_none()
