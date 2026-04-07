"""create source and project-source registries

Revision ID: 20260407_0003
Revises: 20260407_0002
Create Date: 2026-04-07
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260407_0003"
down_revision: str | None = "20260407_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "source_registry",
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("canonical_url", sa.String(length=1000), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("trust_tier", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("source_id"),
        sa.UniqueConstraint("canonical_url", name="uq_source_registry_canonical_url"),
    )

    op.create_table(
        "project_source_registry",
        sa.Column("project_source_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("relevance", sa.String(length=32), nullable=False),
        sa.Column("review_status", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_registry.project_id"]),
        sa.ForeignKeyConstraint(["source_id"], ["source_registry.source_id"]),
        sa.PrimaryKeyConstraint("project_source_id"),
        sa.UniqueConstraint("project_id", "source_id", name="uq_project_source_registry_project_source"),
    )


def downgrade() -> None:
    op.drop_table("project_source_registry")
    op.drop_table("source_registry")
