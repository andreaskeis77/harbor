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
