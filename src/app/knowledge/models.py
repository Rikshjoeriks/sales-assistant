"""SQLAlchemy models for knowledge ingestion domain."""
from __future__ import annotations

import uuid

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.core.db import Base


class KnowledgeSourceModel(Base):
    __tablename__ = "knowledge_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=True)
    type = Column(String(64), nullable=False)
    version = Column(String(64), nullable=True)
    file_path = Column(String(512), nullable=False)
    processing_status = Column(String(32), nullable=False, default="queued")
    created_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    extra_metadata = Column(JSON, nullable=False, default=dict)

    concepts = relationship("KnowledgeConceptModel", back_populates="source", cascade="all, delete-orphan")


class KnowledgeConceptModel(Base):
    __tablename__ = "knowledge_concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    concept_type = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    keywords = Column(JSON, nullable=False, default=list)
    page_reference = Column(String(128), nullable=True)
    confidence_score = Column(Float, nullable=False)

    source = relationship("KnowledgeSourceModel", back_populates="concepts")
    vector = relationship("KnowledgeVectorModel", back_populates="concept", uselist=False, cascade="all, delete-orphan")


class KnowledgeVectorModel(Base):
    __tablename__ = "knowledge_vectors"

    concept_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_concepts.id", ondelete="CASCADE"), primary_key=True)
    embedding = Column(JSON, nullable=False)
    extra_metadata = Column(JSON, nullable=False, default=dict)

    concept = relationship("KnowledgeConceptModel", back_populates="vector")


__all__ = [
    "KnowledgeSourceModel",
    "KnowledgeConceptModel",
    "KnowledgeVectorModel",
]
