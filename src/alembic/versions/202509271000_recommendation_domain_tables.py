"""Create recommendations domain tables."""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "202509271000"
down_revision = "202509261300"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sales_contexts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_interest", sa.String(length=255), nullable=False),
        sa.Column("sales_stage", sa.String(length=32), nullable=False),
        sa.Column("customer_concerns_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("context_description", sa.Text(), nullable=False),
        sa.Column("urgency_level", sa.String(length=16), nullable=True),
        sa.Column("competitive_alternatives_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sales_contexts_customer_id", "sales_contexts", ["customer_id"])
    op.create_index("ix_sales_contexts_created_at", "sales_contexts", ["created_at"])

    op.create_table(
        "sales_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("context_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sales_contexts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_text", sa.Text(), nullable=False),
        sa.Column("output_format", sa.String(length=32), nullable=False),
        sa.Column("psychological_principles_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("technical_features_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("communication_techniques_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sales_recommendations_context_id", "sales_recommendations", ["context_id"])
    op.create_index("ix_sales_recommendations_generated_at", "sales_recommendations", ["generated_at"])

    op.create_table(
        "recommendation_source_references",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sales_recommendations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_concepts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reference_type", sa.String(length=64), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("page_reference", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_recommendation_source_references_recommendation_id",
        "recommendation_source_references",
        ["recommendation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_recommendation_source_references_recommendation_id", table_name="recommendation_source_references")
    op.drop_table("recommendation_source_references")
    op.drop_index("ix_sales_recommendations_generated_at", table_name="sales_recommendations")
    op.drop_index("ix_sales_recommendations_context_id", table_name="sales_recommendations")
    op.drop_table("sales_recommendations")
    op.drop_index("ix_sales_contexts_created_at", table_name="sales_contexts")
    op.drop_index("ix_sales_contexts_customer_id", table_name="sales_contexts")
    op.drop_table("sales_contexts")
