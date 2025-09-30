"""Create feedback domain table (recommendation_feedback)."""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "202509281100"
down_revision = "202509271000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recommendation_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sales_recommendations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interaction_outcome", sa.String(length=32), nullable=False),
        sa.Column("customer_response", sa.Text(), nullable=True),
        sa.Column("salesperson_notes", sa.Text(), nullable=True),
        sa.Column("effectiveness_rating", sa.Integer(), nullable=True),
        sa.Column("techniques_that_worked", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("techniques_that_failed", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("follow_up_scheduled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("additional_notes", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_recommendation_feedback_recommendation_id",
        "recommendation_feedback",
        ["recommendation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_recommendation_feedback_recommendation_id", table_name="recommendation_feedback")
    op.drop_table("recommendation_feedback")
