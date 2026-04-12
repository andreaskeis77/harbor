"""add source snapshot

Revision ID: 20260412_0014
Revises: 20260412_0013
Create Date: 2026-04-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260412_0014"
down_revision = "20260412_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_snapshot",
        sa.Column("source_snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("project_source_id", sa.String(length=36), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("fetch_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("source_snapshot_id"),
        sa.ForeignKeyConstraint(
            ["project_source_id"],
            ["project_source_registry.project_source_id"],
        ),
    )
    op.create_index(
        "ix_source_snapshot_project_source_id",
        "source_snapshot",
        ["project_source_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_source_snapshot_project_source_id",
        table_name="source_snapshot",
    )
    op.drop_table("source_snapshot")
