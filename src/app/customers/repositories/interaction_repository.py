"""Repository utilities for customer interaction history."""
from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.app.customers.models import CustomerInteractionModel
from src.app.customers.repositories.profile_repository import CustomerProfileRepository


@dataclass(slots=True)
class InteractionRecord:
    interaction_id: uuid.UUID
    customer_id: uuid.UUID
    occurred_at: dt.datetime
    interaction_type: str
    outcome: str | None
    duration_minutes: int | None
    products_discussed: list[str]
    customer_feedback: dict[str, Any]
    salesperson_notes: str | None
    follow_up: dict[str, Any]
    recommendation_id: str | None
    sales_stage: str | None


@dataclass(slots=True)
class FollowUpReminder:
    interaction_id: uuid.UUID
    customer_id: uuid.UUID
    follow_up_type: str | None
    follow_up_at: dt.datetime | None
    notes: str | None


class InteractionRepository:
    """Manage persistence and analytics for customer interactions."""

    def __init__(self, *, session: Session, profile_repository: CustomerProfileRepository | None = None) -> None:
        self._session = session
        self._profiles = profile_repository or CustomerProfileRepository(session=session)

    def record(self, customer_id: uuid.UUID, payload: dict[str, Any]) -> InteractionRecord:
        occurred_at = self._resolve_datetime(payload.get("date"))
        follow_up = payload.get("follow_up") or {}
        model = CustomerInteractionModel(
            customer_id=customer_id,
            occurred_at=occurred_at or dt.datetime.now(tz=dt.timezone.utc),
            interaction_type=payload.get("interaction_type", "unknown"),
            duration_minutes=payload.get("duration_minutes"),
            salesperson_notes=payload.get("salesperson_notes"),
            outcome=payload.get("outcome"),
            recommendation_id=payload.get("recommendation_id"),
            sales_stage=payload.get("sales_stage"),
        )
        model.products_discussed = payload.get("products_discussed")
        model.customer_feedback = payload.get("customer_feedback")
        model.follow_up = follow_up
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        interaction_count = self._interaction_count(customer_id)
        self._profiles.snapshot_interactions(
            customer_id,
            last_interaction=model.occurred_at,
            interaction_count=interaction_count,
            sales_stage=model.sales_stage,
        )

        return self._to_domain(model)

    def list_for_customer(self, customer_id: uuid.UUID, limit: int = 20) -> list[InteractionRecord]:
        statement = (
            select(CustomerInteractionModel)
            .where(CustomerInteractionModel.customer_id == customer_id)
            .order_by(CustomerInteractionModel.occurred_at.desc())
            .limit(limit)
        )
        models = self._session.execute(statement).scalars().all()
        return [self._to_domain(model) for model in models]

    def recent_follow_ups(self, limit: int = 5) -> list[FollowUpReminder]:
        statement = (
            select(CustomerInteractionModel)
            .where(CustomerInteractionModel.follow_up_json != {})
            .order_by(CustomerInteractionModel.occurred_at.desc())
            .limit(limit)
        )
        models = self._session.execute(statement).scalars().all()
        reminders: list[FollowUpReminder] = []
        for model in models:
            follow_up = model.follow_up
            reminders.append(
                FollowUpReminder(
                    interaction_id=model.id,
                    customer_id=model.customer_id,
                    follow_up_type=follow_up.get("type"),
                    follow_up_at=self._resolve_datetime(follow_up.get("date")),
                    notes=follow_up.get("notes"),
                )
            )
        return reminders

    def analytics_for_customer(self, customer_id: uuid.UUID) -> dict[str, Any]:
        statement = select(CustomerInteractionModel).where(CustomerInteractionModel.customer_id == customer_id)
        models = self._session.execute(statement).scalars().all()
        if not models:
            return {
                "total_interactions": 0,
                "average_duration": 0,
                "progression": [],
                "success_indicators": [],
            }

        durations = [model.duration_minutes or 0 for model in models]
        average_duration = sum(durations) / len(durations) if durations else 0
        progression = [model.sales_stage for model in models if model.sales_stage]
        success_indicators = []
        for model in models:
            feedback = model.customer_feedback
            for response in feedback.get("positive_responses", []) or []:
                success_indicators.append(f"positive_response:{response}")
        return {
            "total_interactions": len(models),
            "average_duration": average_duration,
            "progression": progression,
            "success_indicators": success_indicators,
        }

    def _interaction_count(self, customer_id: uuid.UUID) -> int:
        statement = select(func.count(CustomerInteractionModel.id)).where(
            CustomerInteractionModel.customer_id == customer_id
        )
        return int(self._session.execute(statement).scalar_one())

    def _resolve_datetime(self, value: Any) -> dt.datetime | None:
        if value is None:
            return None
        if isinstance(value, dt.datetime):
            return value
        try:
            return dt.datetime.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    def _to_domain(self, model: CustomerInteractionModel) -> InteractionRecord:
        return InteractionRecord(
            interaction_id=model.id,
            customer_id=model.customer_id,
            occurred_at=model.occurred_at,
            interaction_type=model.interaction_type,
            outcome=model.outcome,
            duration_minutes=model.duration_minutes,
            products_discussed=model.products_discussed,
            customer_feedback=model.customer_feedback,
            salesperson_notes=model.salesperson_notes,
            follow_up=model.follow_up,
            recommendation_id=model.recommendation_id,
            sales_stage=model.sales_stage,
        )


__all__ = [
    "InteractionRepository",
    "InteractionRecord",
    "FollowUpReminder",
]
