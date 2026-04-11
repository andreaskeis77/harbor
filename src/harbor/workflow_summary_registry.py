from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.models import (
    ProjectSourceRecord,
    ReviewQueueItemRecord,
    SearchCampaignRecord,
    SearchResultCandidateRecord,
    SearchRunRecord,
)
from harbor.project_registry import get_project


class WorkflowSummaryCounts(BaseModel):
    search_campaign_count: int
    search_run_count: int
    search_result_candidate_count: int
    candidate_pending_count: int
    candidate_promoted_count: int
    candidate_accepted_count: int
    review_queue_item_count: int
    review_queue_open_count: int
    review_queue_in_review_count: int
    review_queue_completed_count: int
    project_source_count: int


class WorkflowLineageItem(BaseModel):
    search_result_candidate_id: str
    search_campaign_id: str
    search_run_id: str
    candidate_title: str
    candidate_url: str
    candidate_disposition: str
    review_queue_item_id: str | None
    review_queue_status: str | None
    source_id: str | None
    project_source_id: str | None
    project_source_review_status: str | None
    created_at: datetime
    updated_at: datetime


class WorkflowSummaryRead(BaseModel):
    project_id: str
    project_title: str
    counts: WorkflowSummaryCounts
    lineage_items: list[WorkflowLineageItem]


def _scalar_count(session: Session, stmt) -> int:
    return int(session.execute(stmt).scalar_one())


def _latest_candidate_review_items(
    session: Session, project_id: str
) -> dict[str, ReviewQueueItemRecord]:
    stmt = (
        select(ReviewQueueItemRecord)
        .where(ReviewQueueItemRecord.project_id == project_id)
        .where(ReviewQueueItemRecord.queue_kind == "candidate_review")
        .where(ReviewQueueItemRecord.search_result_candidate_id.is_not(None))
        .order_by(
            ReviewQueueItemRecord.created_at.desc(),
            ReviewQueueItemRecord.review_queue_item_id.desc(),
        )
    )
    items = session.execute(stmt).scalars().all()

    latest_by_candidate: dict[str, ReviewQueueItemRecord] = {}
    for item in items:
        candidate_id = item.search_result_candidate_id
        if candidate_id is not None and candidate_id not in latest_by_candidate:
            latest_by_candidate[candidate_id] = item
    return latest_by_candidate


def _build_counts(session: Session, project_id: str) -> WorkflowSummaryCounts:
    return WorkflowSummaryCounts(
        search_campaign_count=_scalar_count(
            session,
            select(func.count(SearchCampaignRecord.search_campaign_id)).where(
                SearchCampaignRecord.project_id == project_id
            ),
        ),
        search_run_count=_scalar_count(
            session,
            select(func.count(SearchRunRecord.search_run_id)).where(
                SearchRunRecord.project_id == project_id
            ),
        ),
        search_result_candidate_count=_scalar_count(
            session,
            select(func.count(SearchResultCandidateRecord.search_result_candidate_id)).where(
                SearchResultCandidateRecord.project_id == project_id
            ),
        ),
        candidate_pending_count=_scalar_count(
            session,
            select(func.count(SearchResultCandidateRecord.search_result_candidate_id))
            .where(SearchResultCandidateRecord.project_id == project_id)
            .where(SearchResultCandidateRecord.disposition == "pending"),
        ),
        candidate_promoted_count=_scalar_count(
            session,
            select(func.count(SearchResultCandidateRecord.search_result_candidate_id))
            .where(SearchResultCandidateRecord.project_id == project_id)
            .where(SearchResultCandidateRecord.disposition == "promoted"),
        ),
        candidate_accepted_count=_scalar_count(
            session,
            select(func.count(SearchResultCandidateRecord.search_result_candidate_id))
            .where(SearchResultCandidateRecord.project_id == project_id)
            .where(SearchResultCandidateRecord.disposition == "accepted"),
        ),
        review_queue_item_count=_scalar_count(
            session,
            select(func.count(ReviewQueueItemRecord.review_queue_item_id)).where(
                ReviewQueueItemRecord.project_id == project_id
            ),
        ),
        review_queue_open_count=_scalar_count(
            session,
            select(func.count(ReviewQueueItemRecord.review_queue_item_id))
            .where(ReviewQueueItemRecord.project_id == project_id)
            .where(ReviewQueueItemRecord.status == "open"),
        ),
        review_queue_in_review_count=_scalar_count(
            session,
            select(func.count(ReviewQueueItemRecord.review_queue_item_id))
            .where(ReviewQueueItemRecord.project_id == project_id)
            .where(ReviewQueueItemRecord.status == "in_review"),
        ),
        review_queue_completed_count=_scalar_count(
            session,
            select(func.count(ReviewQueueItemRecord.review_queue_item_id))
            .where(ReviewQueueItemRecord.project_id == project_id)
            .where(ReviewQueueItemRecord.status == "completed"),
        ),
        project_source_count=_scalar_count(
            session,
            select(func.count(ProjectSourceRecord.project_source_id)).where(
                ProjectSourceRecord.project_id == project_id
            ),
        ),
    )


def get_workflow_summary(session: Session, project_id: str) -> WorkflowSummaryRead:
    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)

    counts = _build_counts(session, project_id)
    latest_review_items = _latest_candidate_review_items(session, project_id)

    project_source_ids = [
        item.project_source_id
        for item in latest_review_items.values()
        if item.project_source_id is not None
    ]
    project_sources_by_id: dict[str, ProjectSourceRecord] = {}
    if project_source_ids:
        stmt = (
            select(ProjectSourceRecord)
            .where(ProjectSourceRecord.project_id == project_id)
            .where(ProjectSourceRecord.project_source_id.in_(project_source_ids))
        )
        project_sources = session.execute(stmt).scalars().all()
        project_sources_by_id = {item.project_source_id: item for item in project_sources}

    candidate_stmt = (
        select(SearchResultCandidateRecord)
        .where(SearchResultCandidateRecord.project_id == project_id)
        .order_by(
            SearchResultCandidateRecord.created_at.desc(),
            SearchResultCandidateRecord.search_result_candidate_id.desc(),
        )
    )
    candidates = session.execute(candidate_stmt).scalars().all()

    lineage_items: list[WorkflowLineageItem] = []
    for candidate in candidates:
        review_item = latest_review_items.get(candidate.search_result_candidate_id)
        project_source = (
            project_sources_by_id.get(review_item.project_source_id)
            if review_item is not None and review_item.project_source_id is not None
            else None
        )
        lineage_items.append(
            WorkflowLineageItem(
                search_result_candidate_id=candidate.search_result_candidate_id,
                search_campaign_id=candidate.search_campaign_id,
                search_run_id=candidate.search_run_id,
                candidate_title=candidate.title,
                candidate_url=candidate.url,
                candidate_disposition=candidate.disposition,
                review_queue_item_id=(
                    review_item.review_queue_item_id if review_item is not None else None
                ),
                review_queue_status=review_item.status if review_item is not None else None,
                source_id=review_item.source_id if review_item is not None else None,
                project_source_id=(
                    review_item.project_source_id if review_item is not None else None
                ),
                project_source_review_status=(
                    project_source.review_status if project_source is not None else None
                ),
                created_at=candidate.created_at,
                updated_at=candidate.updated_at,
            )
        )

    return WorkflowSummaryRead(
        project_id=project.project_id,
        project_title=project.title,
        counts=counts,
        lineage_items=lineage_items,
    )
