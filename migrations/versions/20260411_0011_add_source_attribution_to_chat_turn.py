"""add source_attribution to chat turn

Revision ID: 20260411_0011
Revises: 20260409_0010
Create Date: 2026-04-11
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260411_0011"
down_revision = "20260409_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "openai_project_chat_turn_registry",
        sa.Column("source_attribution", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("openai_project_chat_turn_registry", "source_attribution")
