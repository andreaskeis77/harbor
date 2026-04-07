"""create project registry table

Revision ID: 20260407_0001
Revises: None
Create Date: 2026-04-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260407_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_registry",
        sa.Column("project_id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("short_description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("project_type", sa.String(length=32), nullable=False),
        sa.Column("blueprint_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_project_registry_title", "project_registry", ["title"], unique=False)
    op.create_index("ix_project_registry_status", "project_registry", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_project_registry_status", table_name="project_registry")
    op.drop_index("ix_project_registry_title", table_name="project_registry")
    op.drop_table("project_registry")
