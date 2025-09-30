"""Repository for feedback persistence (T061)."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, cast

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.app.feedback.models import RecommendationFeedbackModel


@dataclass(slots=True)
class FeedbackRecord:
    feedback_id: uuid.UUID
    recommendation_id: uuid.UUID
    interaction_outcome: str
    effectiveness_rating: int | None
    techniques_that_worked: list[str]
    techniques_that_failed: list[str]
    follow_up_scheduled: bool
    recorded_at: Any


class FeedbackRepository:
    def __init__(self, *, session: Session) -> None:
        self._session = session

    def create(self, *, recommendation_id: uuid.UUID, payload: dict[str, Any]) -> FeedbackRecord:
        model = RecommendationFeedbackModel(
            recommendation_id=recommendation_id,
            interaction_outcome=payload.get("interaction_outcome", "unknown"),
            customer_response=payload.get("customer_response"),
            salesperson_notes=payload.get("salesperson_notes"),
            effectiveness_rating=payload.get("effectiveness_rating"),
            techniques_that_worked=list(payload.get("techniques_that_worked", [])),
            techniques_that_failed=list(payload.get("techniques_that_failed", [])),
            follow_up_scheduled=bool(payload.get("follow_up_scheduled", False)),
            additional_notes=payload.get("additional_notes"),
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return FeedbackRecord(
            feedback_id=cast(uuid.UUID, model.id),
            recommendation_id=cast(uuid.UUID, model.recommendation_id),
            interaction_outcome=cast(str, model.interaction_outcome),
            effectiveness_rating=cast(int | None, model.effectiveness_rating),
            techniques_that_worked=list(cast(list[str] | None, model.techniques_that_worked) or []),
            techniques_that_failed=list(cast(list[str] | None, model.techniques_that_failed) or []),
            follow_up_scheduled=bool(model.follow_up_scheduled),
            recorded_at=model.recorded_at,
        )

    def list_for_recommendations(self, recommendation_ids: list[uuid.UUID]) -> list[FeedbackRecord]:
        if not recommendation_ids:
            return []
        rows = (
            self._session.query(RecommendationFeedbackModel)
            .filter(RecommendationFeedbackModel.recommendation_id.in_(recommendation_ids))
            .all()
        )
        return [
            FeedbackRecord(
                feedback_id=cast(uuid.UUID, row.id),
                recommendation_id=cast(uuid.UUID, row.recommendation_id),
                interaction_outcome=cast(str, row.interaction_outcome),
                effectiveness_rating=cast(int | None, row.effectiveness_rating),
                techniques_that_worked=list(cast(list[str] | None, row.techniques_that_worked) or []),
                techniques_that_failed=list(cast(list[str] | None, row.techniques_that_failed) or []),
                follow_up_scheduled=bool(row.follow_up_scheduled),
                recorded_at=row.recorded_at,
            )
            for row in rows
        ]

    def list_in_period(self, *, start: Any, end: Any) -> list[FeedbackRecord]:
        rows = (
            self._session.query(RecommendationFeedbackModel)
            .filter(
                and_(
                    RecommendationFeedbackModel.recorded_at >= start,
                    RecommendationFeedbackModel.recorded_at <= end,
                )
            )
            .all()
        )
        return [
            FeedbackRecord(
                feedback_id=cast(uuid.UUID, row.id),
                recommendation_id=cast(uuid.UUID, row.recommendation_id),
                interaction_outcome=cast(str, row.interaction_outcome),
                effectiveness_rating=cast(int | None, row.effectiveness_rating),
                techniques_that_worked=list(cast(list[str] | None, row.techniques_that_worked) or []),
                techniques_that_failed=list(cast(list[str] | None, row.techniques_that_failed) or []),
                follow_up_scheduled=bool(row.follow_up_scheduled),
                recorded_at=row.recorded_at,
            )
            for row in rows
        ]


__all__ = ["FeedbackRepository", "FeedbackRecord"]
