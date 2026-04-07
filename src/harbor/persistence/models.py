from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from harbor.persistence.base import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


def default_project_id() -> str:
    return str(uuid.uuid4())


def default_handbook_version_id() -> str:
    return str(uuid.uuid4())


class ProjectRecord(Base):
    __tablename__ = "project_registry"

    project_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=default_project_id,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    short_description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    project_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="standard",
    )
    blueprint_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="not_blueprint",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )


class HandbookVersionRecord(Base):
    __tablename__ = "handbook_version_registry"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "version_number",
            name="uq_handbook_version_registry_project_version",
        ),
    )

    handbook_version_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=default_handbook_version_id,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_registry.project_id"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    handbook_markdown: Mapped[str] = mapped_column(Text(), nullable=False)
    change_note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )


def default_source_id() -> str:
    return str(uuid.uuid4())


def default_project_source_id() -> str:
    return str(uuid.uuid4())


class SourceRecord(Base):
    __tablename__ = "source_registry"
    __table_args__ = (
        UniqueConstraint(
            "canonical_url",
            name="uq_source_registry_canonical_url",
        ),
    )

    source_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=default_source_id,
    )
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trust_tier: Mapped[str] = mapped_column(String(32), nullable=False, default="candidate")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )


class ProjectSourceRecord(Base):
    __tablename__ = "project_source_registry"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "source_id",
            name="uq_project_source_registry_project_source",
        ),
    )

    project_source_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=default_project_source_id,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_registry.project_id"),
        nullable=False,
    )
    source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("source_registry.source_id"),
        nullable=False,
    )
    relevance: Mapped[str] = mapped_column(String(32), nullable=False, default="candidate")
    review_status: Mapped[str] = mapped_column(String(32), nullable=False, default="candidate")
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )


def default_search_campaign_id() -> str:
    return str(uuid.uuid4())


class SearchCampaignRecord(Base):
    __tablename__ = "search_campaign_registry"

    search_campaign_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=default_search_campaign_id,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_registry.project_id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    query_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    campaign_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )


def default_review_queue_item_id() -> str:
    return str(uuid.uuid4())


class ReviewQueueItemRecord(Base):
    __tablename__ = "review_queue_item_registry"

    review_queue_item_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=default_review_queue_item_id,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_registry.project_id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    queue_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="source_review")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default="normal")
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    source_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("source_registry.source_id"),
        nullable=True,
    )
    project_source_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("project_source_registry.project_source_id"),
        nullable=True,
    )
    search_campaign_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("search_campaign_registry.search_campaign_id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )
