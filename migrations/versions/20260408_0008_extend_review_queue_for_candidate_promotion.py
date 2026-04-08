"""extend review queue for candidate promotion

Revision ID: 20260408_0008
Revises: 20260408_0007
Create Date: 2026-04-08

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260408_0008"
down_revision = "20260408_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("review_queue_item_registry", schema=None) as batch_op:
        batch_op.add_column(sa.Column("search_run_id", sa.String(length=36), nullable=True))
        batch_op.add_column(
            sa.Column("search_result_candidate_id", sa.String(length=36), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_review_queue_item_registry_search_run_id",
            "search_run_registry",
            ["search_run_id"],
            ["search_run_id"],
        )
        batch_op.create_foreign_key(
            "fk_review_queue_item_registry_search_result_candidate_id",
            "search_result_candidate_registry",
            ["search_result_candidate_id"],
            ["search_result_candidate_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("review_queue_item_registry", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_review_queue_item_registry_search_result_candidate_id",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_review_queue_item_registry_search_run_id",
            type_="foreignkey",
        )
        batch_op.drop_column("search_result_candidate_id")
        batch_op.drop_column("search_run_id")
