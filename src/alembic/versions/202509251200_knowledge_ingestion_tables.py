"""Create knowledge ingestion tables."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "202509251200"
down_revision = None
branch_labels = None
depends_on = None


def _is_postgres(connection: sa.engine.Connection) -> bool:
    return connection.dialect.name == "postgresql"


def upgrade() -> None:
    connection = op.get_bind()
    if connection is not None and _is_postgres(connection):
        op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table(
        "knowledge_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column("file_path", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("processing_status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )
    op.create_index(
        "ix_knowledge_sources_type_status",
        "knowledge_sources",
        ["type", "processing_status"],
    )
    op.create_index(
        "ix_knowledge_sources_created_at",
        "knowledge_sources",
        ["created_at"],
    )

    op.create_table(
        "knowledge_concepts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("concept_type", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("keywords_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("page_reference", sa.String(length=128), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
    )
    op.create_index("ix_knowledge_concepts_source", "knowledge_concepts", ["source_id"])
    op.create_index(
        "ix_knowledge_concepts_title",
        "knowledge_concepts",
        ["title"],
    )

    op.create_table(
        "knowledge_vectors",
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_concepts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("embedding", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )


def downgrade() -> None:
    op.drop_table("knowledge_vectors")
    op.drop_index("ix_knowledge_concepts_title", table_name="knowledge_concepts")
    op.drop_index("ix_knowledge_concepts_source", table_name="knowledge_concepts")
    op.drop_table("knowledge_concepts")
    op.drop_index("ix_knowledge_sources_created_at", table_name="knowledge_sources")
    op.drop_index("ix_knowledge_sources_type_status", table_name="knowledge_sources")
    op.drop_table("knowledge_sources")
