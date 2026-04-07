"""create review queue item registry table

Revision ID: 20260407_0005
Revises: 20260407_0004
Create Date: 2026-04-07
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260407_0005"
down_revision = "20260407_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "review_queue_item_registry",
        sa.Column("review_queue_item_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("queue_kind", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("source_id", sa.String(length=36), nullable=True),
        sa.Column("project_source_id", sa.String(length=36), nullable=True),
        sa.Column("search_campaign_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_registry.project_id"]),
        sa.ForeignKeyConstraint(["source_id"], ["source_registry.source_id"]),
        sa.ForeignKeyConstraint(["project_source_id"], ["project_source_registry.project_source_id"]),
        sa.ForeignKeyConstraint(["search_campaign_id"], ["search_campaign_registry.search_campaign_id"]),
        sa.PrimaryKeyConstraint("review_queue_item_id"),
    )


def downgrade() -> None:
    op.drop_table("review_queue_item_registry")
