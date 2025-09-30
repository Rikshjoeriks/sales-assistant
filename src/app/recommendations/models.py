"""SQLAlchemy models for the recommendations domain."""
from __future__ import annotations

import uuid

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.core.db import Base


class SalesContextModel(Base):
    __tablename__ = "sales_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False)
    product_interest = Column(String(255), nullable=False)
    sales_stage = Column(String(32), nullable=False)
    customer_concerns_json = Column(JSON, nullable=False, default=list)
    context_description = Column(Text, nullable=False)
    urgency_level = Column(String(16), nullable=True)
    competitive_alternatives_json = Column(JSON, nullable=False, default=list)
    metadata_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    recommendations = relationship(
        "SalesRecommendationModel",
        back_populates="context",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SalesRecommendationModel(Base):
    __tablename__ = "sales_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    context_id = Column(UUID(as_uuid=True), ForeignKey("sales_contexts.id", ondelete="CASCADE"), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    output_format = Column(String(32), nullable=False)
    psychological_principles_json = Column(JSON, nullable=False, default=list)
    technical_features_json = Column(JSON, nullable=False, default=list)
    communication_techniques_json = Column(JSON, nullable=False, default=list)
    metadata_json = Column(JSON, nullable=False, default=dict)
    confidence_score = Column(Float, nullable=False, default=0.0)
    token_count = Column(Integer, nullable=False, default=0)
    generated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    context = relationship("SalesContextModel", back_populates="recommendations")
    source_references = relationship(
        "RecommendationSourceReferenceModel",
        back_populates="recommendation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class RecommendationSourceReferenceModel(Base):
    __tablename__ = "recommendation_source_references"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sales_recommendations.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id", ondelete="SET NULL"), nullable=True)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_concepts.id", ondelete="SET NULL"), nullable=True)
    reference_type = Column(String(64), nullable=False)
    relevance_score = Column(Float, nullable=True)
    page_reference = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    recommendation = relationship("SalesRecommendationModel", back_populates="source_references")


__all__ = [
    "SalesContextModel",
    "SalesRecommendationModel",
    "RecommendationSourceReferenceModel",
]
