"""create search campaign registry table

Revision ID: 20260407_0004
Revises: 20260407_0003
Create Date: 2026-04-07
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260407_0004"
down_revision = "20260407_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "search_campaign_registry",
        sa.Column("search_campaign_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=True),
        sa.Column("campaign_kind", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_registry.project_id"]),
        sa.PrimaryKeyConstraint("search_campaign_id"),
    )


def downgrade() -> None:
    op.drop_table("search_campaign_registry")
