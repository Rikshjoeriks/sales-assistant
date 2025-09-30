"""SQLAlchemy models backing the customer intelligence domain."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.core.db import Base


class CustomerProfileModel(Base):
    """Persistence model capturing core customer attributes."""

    __tablename__ = "customer_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    profession = Column(String(255), nullable=True)
    personality_type = Column(String(1), nullable=True)
    personality_confidence = Column(Float, nullable=True)
    personality_method = Column(String(64), nullable=True)
    communication_style = Column(String(64), nullable=True)
    budget_range = Column(String(32), nullable=True)
    sales_stage = Column(String(32), nullable=False, default="prospecting")
    current_interest = Column(String(255), nullable=True)
    profile_score = Column(Float, nullable=False, default=0.0)
    recommendation_ready = Column(Boolean, nullable=False, default=False)
    interaction_count = Column(Integer, nullable=False, default=0)
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    demographics_json = Column(JSON, nullable=False, default=dict)
    personality_traits_json = Column(JSON, nullable=False, default=dict)
    communication_preferences_json = Column(JSON, nullable=False, default=dict)
    decision_factors_json = Column(JSON, nullable=False, default=dict)
    buying_context_json = Column(JSON, nullable=False, default=dict)
    summary_json = Column(JSON, nullable=False, default=dict)

    interactions = relationship(
        "CustomerInteractionModel",
        back_populates="customer",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def _copy_dict(self, attribute: str) -> dict[str, Any]:
        value = getattr(self, attribute) or {}
        return dict(value)

    @property
    def demographics(self) -> dict[str, Any]:
        return self._copy_dict("demographics_json")

    @demographics.setter
    def demographics(self, value: dict[str, Any] | None) -> None:
        self.demographics_json = dict(value or {})

    @property
    def personality_traits(self) -> dict[str, float]:
        return self._copy_dict("personality_traits_json")

    @personality_traits.setter
    def personality_traits(self, value: dict[str, float] | None) -> None:
        self.personality_traits_json = dict(value or {})

    @property
    def communication_preferences(self) -> dict[str, Any]:
        return self._copy_dict("communication_preferences_json")

    @communication_preferences.setter
    def communication_preferences(self, value: dict[str, Any] | None) -> None:
        self.communication_preferences_json = dict(value or {})

    @property
    def decision_factors(self) -> dict[str, Any]:
        return self._copy_dict("decision_factors_json")

    @decision_factors.setter
    def decision_factors(self, value: dict[str, Any] | None) -> None:
        self.decision_factors_json = dict(value or {})

    @property
    def buying_context(self) -> dict[str, Any]:
        return self._copy_dict("buying_context_json")

    @buying_context.setter
    def buying_context(self, value: dict[str, Any] | None) -> None:
        self.buying_context_json = dict(value or {})

    @property
    def summary(self) -> dict[str, Any]:
        return self._copy_dict("summary_json")

    @summary.setter
    def summary(self, value: dict[str, Any] | None) -> None:
        self.summary_json = dict(value or {})

    def compute_profile_completeness(self) -> float:
        sections = [
            bool(self.name),
            bool(self.demographics),
            bool(self.personality_type),
            bool(self.communication_preferences),
            bool(self.decision_factors),
            bool(self.buying_context),
        ]
        if not sections:
            return 0.0
        completed = len([section for section in sections if section])
        return round(completed / len(sections), 2)


class CustomerInteractionModel(Base):
    """Interaction history entries mapped to customer profiles."""

    __tablename__ = "customer_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    interaction_type = Column(String(64), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    products_discussed_json = Column(JSON, nullable=False, default=list)
    customer_feedback_json = Column(JSON, nullable=False, default=dict)
    salesperson_notes = Column(Text, nullable=True)
    outcome = Column(String(64), nullable=True)
    follow_up_json = Column(JSON, nullable=False, default=dict)
    recommendation_id = Column(String(64), nullable=True)
    sales_stage = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    customer = relationship("CustomerProfileModel", back_populates="interactions")

    def _copy_dict(self, attribute: str) -> dict[str, Any]:
        value = getattr(self, attribute) or {}
        return dict(value)

    @property
    def products_discussed(self) -> list[str]:
        value = self.products_discussed_json or []
        return list(value)

    @products_discussed.setter
    def products_discussed(self, value: list[str] | None) -> None:
        self.products_discussed_json = list(value or [])

    @property
    def customer_feedback(self) -> dict[str, Any]:
        return self._copy_dict("customer_feedback_json")

    @customer_feedback.setter
    def customer_feedback(self, value: dict[str, Any] | None) -> None:
        self.customer_feedback_json = dict(value or {})

    @property
    def follow_up(self) -> dict[str, Any]:
        return self._copy_dict("follow_up_json")

    @follow_up.setter
    def follow_up(self, value: dict[str, Any] | None) -> None:
        self.follow_up_json = dict(value or {})


__all__ = [
    "CustomerProfileModel",
    "CustomerInteractionModel",
]
