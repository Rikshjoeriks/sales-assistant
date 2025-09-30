"""Feedback service layer (T062-T063): validate and persist feedback."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from src.app.feedback.repositories import FeedbackRepository, FeedbackRecord


class FeedbackPayload(BaseModel):
    interaction_outcome: str
    customer_response: str | None = None
    salesperson_notes: str | None = None
    effectiveness_rating: int | None = None
    techniques_that_worked: list[str] = Field(default_factory=list)
    techniques_that_failed: list[str] = Field(default_factory=list)
    follow_up_scheduled: bool = False
    additional_notes: str | None = None


@dataclass(slots=True)
class FeedbackResponse:
    feedback_id: uuid.UUID
    recommendation_id: uuid.UUID
    recorded_at: Any
    learning_impact: dict[str, Any]


class FeedbackService:
    def __init__(self, *, repository: FeedbackRepository) -> None:
        self._repo = repository

    def record(self, *, recommendation_id: uuid.UUID, payload: FeedbackPayload) -> FeedbackResponse:
        rec: FeedbackRecord = self._repo.create(recommendation_id=recommendation_id, payload=payload.model_dump())
        # Minimal placeholder for analytics/learning impact. Extend later.
        learning = {
            "concepts_reinforced": [],
            "model_updates": "Feedback incorporated into learning system",
        }
        return FeedbackResponse(
            feedback_id=rec.feedback_id,
            recommendation_id=rec.recommendation_id,
            recorded_at=rec.recorded_at,
            learning_impact=learning,
        )


__all__ = [
    "FeedbackService",
    "FeedbackPayload",
    "FeedbackResponse",
]
