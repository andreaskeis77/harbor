"""add automation task registry

Revision ID: 20260412_0012
Revises: 20260411_0011
Create Date: 2026-04-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260412_0012"
down_revision = "20260411_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "automation_task_registry",
        sa.Column("automation_task_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("task_kind", sa.String(length=64), nullable=False),
        sa.Column("trigger_source", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_registry.project_id"]),
        sa.PrimaryKeyConstraint("automation_task_id"),
    )
    op.create_index(
        "ix_automation_task_registry_project_created",
        "automation_task_registry",
        ["project_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_automation_task_registry_project_created",
        table_name="automation_task_registry",
    )
    op.drop_table("automation_task_registry")
