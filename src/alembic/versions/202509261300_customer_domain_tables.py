"""Create customer intelligence tables."""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "202509261300"
down_revision = "202509251200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("profession", sa.String(length=255), nullable=True),
        sa.Column("personality_type", sa.String(length=1), nullable=True),
        sa.Column("personality_confidence", sa.Float(), nullable=True),
        sa.Column("personality_method", sa.String(length=64), nullable=True),
        sa.Column("communication_style", sa.String(length=64), nullable=True),
        sa.Column("budget_range", sa.String(length=32), nullable=True),
        sa.Column("sales_stage", sa.String(length=32), nullable=False, server_default="prospecting"),
        sa.Column("current_interest", sa.String(length=255), nullable=True),
        sa.Column("profile_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("recommendation_ready", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("interaction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_interaction_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("demographics_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("personality_traits_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("communication_preferences_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("decision_factors_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("buying_context_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("summary_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index(
        "ix_customer_profiles_sales_stage",
        "customer_profiles",
        ["sales_stage"],
    )
    op.create_index(
        "ix_customer_profiles_personality_type",
        "customer_profiles",
        ["personality_type"],
    )

    op.create_table(
        "customer_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interaction_type", sa.String(length=64), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("products_discussed_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("customer_feedback_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("salesperson_notes", sa.Text(), nullable=True),
        sa.Column("outcome", sa.String(length=64), nullable=True),
        sa.Column("follow_up_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("recommendation_id", sa.String(length=64), nullable=True),
        sa.Column("sales_stage", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_customer_interactions_customer_id",
        "customer_interactions",
        ["customer_id"],
    )
    op.create_index(
        "ix_customer_interactions_occurred_at",
        "customer_interactions",
        ["occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_customer_interactions_occurred_at", table_name="customer_interactions")
    op.drop_index("ix_customer_interactions_customer_id", table_name="customer_interactions")
    op.drop_table("customer_interactions")
    op.drop_index("ix_customer_profiles_personality_type", table_name="customer_profiles")
    op.drop_index("ix_customer_profiles_sales_stage", table_name="customer_profiles")
    op.drop_table("customer_profiles")
