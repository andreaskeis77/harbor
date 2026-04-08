"""create search result candidate registry table

Revision ID: 20260408_0007
Revises: 20260407_0006
Create Date: 2026-04-08

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260408_0007"
down_revision = "20260407_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "search_result_candidate_registry",
        sa.Column("search_result_candidate_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("search_campaign_id", sa.String(length=36), nullable=False),
        sa.Column("search_run_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("snippet", sa.Text(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("disposition", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_registry.project_id"]),
        sa.ForeignKeyConstraint(
            ["search_campaign_id"], ["search_campaign_registry.search_campaign_id"]
        ),
        sa.ForeignKeyConstraint(["search_run_id"], ["search_run_registry.search_run_id"]),
        sa.PrimaryKeyConstraint("search_result_candidate_id"),
    )


def downgrade() -> None:
    op.drop_table("search_result_candidate_registry")
