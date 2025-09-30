"""SQLAlchemy models for feedback domain (T061)."""
from __future__ import annotations

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.core.db import Base


class RecommendationFeedbackModel(Base):
    __tablename__ = "recommendation_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("sales_recommendations.id", ondelete="CASCADE"), nullable=False)
    interaction_outcome = Column(String(32), nullable=False)
    customer_response = Column(Text, nullable=True)
    salesperson_notes = Column(Text, nullable=True)
    effectiveness_rating = Column(Integer, nullable=True)
    techniques_that_worked = Column(JSON, nullable=False, default=list)
    techniques_that_failed = Column(JSON, nullable=False, default=list)
    follow_up_scheduled = Column(Boolean, nullable=False, default=False)
    additional_notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    recommendation = relationship("src.app.recommendations.models.SalesRecommendationModel", backref="feedback")


__all__ = ["RecommendationFeedbackModel"]
