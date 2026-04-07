from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from harbor.persistence.base import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


def default_project_id() -> str:
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
