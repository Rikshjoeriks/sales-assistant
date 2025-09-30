"""Persistence helpers for customer profiles."""
from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any, cast

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from src.app.customers.models import CustomerProfileModel


@dataclass(slots=True)
class CustomerProfile:
    customer_id: uuid.UUID
    name: str | None
    profession: str | None
    demographics: dict[str, Any]
    personality_type: str | None
    personality_confidence: float | None
    personality_method: str | None
    personality_traits: dict[str, float]
    communication_style: str | None
    communication_preferences: dict[str, Any]
    decision_factors: dict[str, Any]
    buying_context: dict[str, Any]
    profile_score: float
    recommendation_ready: bool
    created_at: dt.datetime
    updated_at: dt.datetime
    interaction_count: int
    last_interaction_at: dt.datetime | None
    sales_stage: str
    budget_range: str | None
    current_interest: str | None
    summary: dict[str, Any]


@dataclass(slots=True)
class CustomerSummary:
    customer_id: uuid.UUID
    name: str | None
    profession: str | None
    personality_type: str | None
    budget_range: str | None
    sales_stage: str
    interaction_count: int
    last_interaction_at: dt.datetime | None
    profile_score: float


class CustomerProfileRepository:
    """Repository providing CRUD and analytics around customer profiles."""

    def __init__(self, *, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------
    def create_profile(self, payload: dict[str, Any]) -> CustomerProfile:
        model = CustomerProfileModel()
        self._apply_payload(model, payload)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    def update_profile(self, customer_id: uuid.UUID, payload: dict[str, Any]) -> CustomerProfile:
        model = self._require_model(customer_id)
        self._apply_payload(model, payload)
        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    def record_summary(
        self,
        customer_id: uuid.UUID,
        *,
        traits: dict[str, float],
        summary: dict[str, Any],
        recommendation_ready: bool,
        profile_score: float,
    ) -> CustomerProfile:
        model = self._require_model(customer_id)
        model.personality_traits = traits
        model.summary = summary
        model.recommendation_ready = recommendation_ready  # type: ignore[assignment]
        model.profile_score = profile_score  # type: ignore[assignment]
        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    def snapshot_interactions(
        self,
        customer_id: uuid.UUID,
        *,
        last_interaction: dt.datetime | None,
        interaction_count: int,
        sales_stage: str | None = None,
        current_interest: str | None = None,
    ) -> None:
        model = self._require_model(customer_id)
        model.last_interaction_at = last_interaction  # type: ignore[assignment]
        model.interaction_count = interaction_count  # type: ignore[assignment]
        if sales_stage:
            model.sales_stage = sales_stage  # type: ignore[assignment]
        if current_interest:
            model.current_interest = current_interest  # type: ignore[assignment]
        self._session.commit()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get_profile(self, customer_id: uuid.UUID) -> CustomerProfile:
        model = self._require_model(customer_id)
        return self._to_domain(model)

    def search_profiles(
        self,
        *,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[CustomerSummary], int]:
        filters = filters or {}
        statement = select(CustomerProfileModel)
        statement = self._apply_filters(statement, filters)
        total = self._session.execute(statement.with_only_columns(func.count())).scalar_one()
        statement = (
            statement.order_by(CustomerProfileModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = self._session.execute(statement).scalars().all()
        return [self._to_summary(model) for model in models], int(total)

    def personality_distribution(self) -> dict[str, int]:
        statement = (
            select(CustomerProfileModel.personality_type, func.count())
            .group_by(CustomerProfileModel.personality_type)
        )
        rows = self._session.execute(statement).all()
        return {str(row[0] or "unknown"): int(row[1]) for row in rows}

    def average_profile_score(self) -> float:
        score = self._session.execute(select(func.avg(CustomerProfileModel.profile_score))).scalar()
        return float(score or 0.0)

    def total_customers(self) -> int:
        return int(self._session.execute(select(func.count(CustomerProfileModel.id))).scalar_one())

    def top_decision_factors(self, limit: int = 5) -> list[str]:
        statement = select(CustomerProfileModel)
        rows = self._session.execute(statement).scalars().all()
        counts: dict[str, int] = {}
        for model in rows:
            data = model.decision_factors or {}
            for group in ("primary", "secondary"):
                for factor in data.get(group, []):
                    counts[factor] = counts.get(factor, 0) + 1
        return sorted(counts, key=lambda item: counts[item], reverse=True)[:limit]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _apply_payload(self, model: CustomerProfileModel, payload: dict[str, Any]) -> None:
        demographics = payload.get("demographics")
        assessment = payload.get("personality_assessment", {}) or {}
        communication = payload.get("communication_preferences")
        decision_factors = payload.get("decision_factors")
        buying_context = payload.get("buying_context")

        model.name = payload.get("name", model.name)
        model.demographics = demographics
        model.profession = (demographics or {}).get("profession", model.profession)
        model.personality_type = assessment.get("type") or model.personality_type
        model.personality_confidence = assessment.get("confidence")  # type: ignore[assignment]
        model.personality_method = assessment.get("assessment_method")  # type: ignore[assignment]
        model.communication_style = (
            communication.get("style") if communication else model.communication_style
        )  # type: ignore[assignment]
        model.communication_preferences = communication
        model.decision_factors = decision_factors
        model.buying_context = buying_context
        model.budget_range = (buying_context or {}).get("budget_range") or model.budget_range  # type: ignore[assignment]
        if "sales_stage" in payload:
            model.sales_stage = payload["sales_stage"]  # type: ignore[assignment]
        model.current_interest = payload.get("current_interest", model.current_interest)  # type: ignore[assignment]
        model.profile_score = model.compute_profile_completeness()  # type: ignore[assignment]
        model.recommendation_ready = bool(model.profile_score >= 0.7)  # type: ignore[assignment]

    def _apply_filters(self, statement, filters: dict[str, Any]):
        conditions: list[Any] = []
        if personality := filters.get("personality_type"):
            conditions.append(CustomerProfileModel.personality_type == personality)
        if budget := filters.get("budget_range"):
            conditions.append(CustomerProfileModel.budget_range == budget)
        if stage := filters.get("sales_stage"):
            conditions.append(CustomerProfileModel.sales_stage == stage)
        if search := filters.get("search"):
            pattern = f"%{search.lower()}%"
            conditions.append(
                or_(
                    func.lower(CustomerProfileModel.name).like(pattern),
                    func.lower(CustomerProfileModel.profession).like(pattern),
                )
            )
        if conditions:
            statement = statement.where(and_(*conditions))
        return statement

    def _require_model(self, customer_id: uuid.UUID) -> CustomerProfileModel:
        model = self._session.get(CustomerProfileModel, customer_id)
        if not model:
            raise KeyError(f"Customer {customer_id} not found")
        return model

    def _to_domain(self, model: CustomerProfileModel) -> CustomerProfile:
        return CustomerProfile(
            customer_id=cast(uuid.UUID, model.id),
            name=cast(str | None, model.name),
            demographics=model.demographics,
            profession=cast(str | None, model.profession),
            personality_type=cast(str | None, model.personality_type),
            personality_confidence=cast(float | None, getattr(model, "personality_confidence", None)),
            personality_method=cast(str | None, getattr(model, "personality_method", None)),
            personality_traits=model.personality_traits,
            communication_style=cast(str | None, getattr(model, "communication_style", None)),
            communication_preferences=model.communication_preferences,
            decision_factors=model.decision_factors,
            buying_context=model.buying_context,
            profile_score=float(getattr(model, "profile_score", 0.0) or 0.0),
            recommendation_ready=bool(getattr(model, "recommendation_ready", False)),
            created_at=cast(dt.datetime, model.created_at),
            updated_at=cast(dt.datetime, model.updated_at),
            interaction_count=int(getattr(model, "interaction_count", 0) or 0),
            last_interaction_at=cast(dt.datetime | None, getattr(model, "last_interaction_at", None)),
            sales_stage=cast(str, model.sales_stage),
            budget_range=cast(str | None, getattr(model, "budget_range", None)),
            current_interest=cast(str | None, getattr(model, "current_interest", None)),
            summary=model.summary,
        )

    def _to_summary(self, model: CustomerProfileModel) -> CustomerSummary:
        return CustomerSummary(
            customer_id=cast(uuid.UUID, model.id),
            name=cast(str | None, model.name),
            profession=cast(str | None, getattr(model, "profession", None)),
            personality_type=cast(str | None, getattr(model, "personality_type", None)),
            budget_range=cast(str | None, getattr(model, "budget_range", None)),
            sales_stage=cast(str, model.sales_stage),
            interaction_count=int(getattr(model, "interaction_count", 0) or 0),
            last_interaction_at=cast(dt.datetime | None, getattr(model, "last_interaction_at", None)),
            profile_score=float(getattr(model, "profile_score", 0.0) or 0.0),
        )


__all__ = [
    "CustomerProfileRepository",
    "CustomerProfile",
    "CustomerSummary",
]
