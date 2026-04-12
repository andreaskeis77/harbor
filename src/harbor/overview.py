from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from harbor.persistence.models import (
    AutomationTaskRecord,
    HandbookVersionRecord,
    OpenAIProjectChatTurnRecord,
    ProjectRecord,
    ProjectSourceRecord,
    ReviewQueueItemRecord,
)

PROJECTS_SUMMARY_LIMIT = 20
RECENT_TASKS_LIMIT = 10
OPEN_REVIEW_STATUSES: tuple[str, ...] = ("open", "pending")


class OverviewTotals(BaseModel):
    projects: int
    project_sources: int
    review_queue_items: int
    handbook_versions: int
    automation_tasks: int
    chat_turns: int
    open_review_queue_items: int


class OverviewRecentTask(BaseModel):
    automation_task_id: str
    project_id: str | None
    task_kind: str
    status: str
    trigger_source: str
    created_at: str
    completed_at: str | None


class OverviewProjectSummary(BaseModel):
    project_id: str
    title: str
    updated_at: str
    source_count: int
    open_review_count: int
    latest_handbook_version_number: int | None


class OverviewResponse(BaseModel):
    totals: OverviewTotals
    recent_automation_tasks: list[OverviewRecentTask]
    projects_summary: list[OverviewProjectSummary]


def _count(session: Session, model) -> int:
    return int(session.execute(select(func.count()).select_from(model)).scalar_one())


def build_overview(session: Session) -> OverviewResponse:
    open_review_count = int(
        session.execute(
            select(func.count()).select_from(ReviewQueueItemRecord).where(
                ReviewQueueItemRecord.status.in_(OPEN_REVIEW_STATUSES),
            )
        ).scalar_one()
    )

    totals = OverviewTotals(
        projects=_count(session, ProjectRecord),
        project_sources=_count(session, ProjectSourceRecord),
        review_queue_items=_count(session, ReviewQueueItemRecord),
        handbook_versions=_count(session, HandbookVersionRecord),
        automation_tasks=_count(session, AutomationTaskRecord),
        chat_turns=_count(session, OpenAIProjectChatTurnRecord),
        open_review_queue_items=open_review_count,
    )

    recent = (
        session.execute(
            select(AutomationTaskRecord)
            .order_by(AutomationTaskRecord.created_at.desc())
            .limit(RECENT_TASKS_LIMIT)
        )
        .scalars()
        .all()
    )
    recent_tasks = [
        OverviewRecentTask(
            automation_task_id=t.automation_task_id,
            project_id=t.project_id,
            task_kind=t.task_kind,
            status=t.status,
            trigger_source=t.trigger_source,
            created_at=t.created_at.isoformat(),
            completed_at=t.completed_at.isoformat() if t.completed_at else None,
        )
        for t in recent
    ]

    projects = (
        session.execute(
            select(ProjectRecord)
            .order_by(ProjectRecord.updated_at.desc())
            .limit(PROJECTS_SUMMARY_LIMIT)
        )
        .scalars()
        .all()
    )
    project_ids = [p.project_id for p in projects]

    source_counts: dict[str, int] = {}
    open_review_counts: dict[str, int] = {}
    latest_handbook_version: dict[str, int] = {}

    if project_ids:
        for pid, cnt in session.execute(
            select(
                ProjectSourceRecord.project_id,
                func.count(ProjectSourceRecord.project_source_id),
            )
            .where(ProjectSourceRecord.project_id.in_(project_ids))
            .group_by(ProjectSourceRecord.project_id)
        ).all():
            source_counts[pid] = int(cnt)

        for pid, cnt in session.execute(
            select(
                ReviewQueueItemRecord.project_id,
                func.count(ReviewQueueItemRecord.review_queue_item_id),
            )
            .where(
                ReviewQueueItemRecord.project_id.in_(project_ids),
                ReviewQueueItemRecord.status.in_(OPEN_REVIEW_STATUSES),
            )
            .group_by(ReviewQueueItemRecord.project_id)
        ).all():
            open_review_counts[pid] = int(cnt)

        for pid, version in session.execute(
            select(
                HandbookVersionRecord.project_id,
                func.max(HandbookVersionRecord.version_number),
            )
            .where(HandbookVersionRecord.project_id.in_(project_ids))
            .group_by(HandbookVersionRecord.project_id)
        ).all():
            latest_handbook_version[pid] = int(version)

    projects_summary = [
        OverviewProjectSummary(
            project_id=p.project_id,
            title=p.title,
            updated_at=p.updated_at.isoformat(),
            source_count=source_counts.get(p.project_id, 0),
            open_review_count=open_review_counts.get(p.project_id, 0),
            latest_handbook_version_number=latest_handbook_version.get(p.project_id),
        )
        for p in projects
    ]

    return OverviewResponse(
        totals=totals,
        recent_automation_tasks=recent_tasks,
        projects_summary=projects_summary,
    )
