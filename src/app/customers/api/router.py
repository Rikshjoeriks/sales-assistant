"""FastAPI routes for customer management."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.customers.api.schemas import (
    AnalyticsSummaryResponse,
    CustomerDetailResponse,
    CustomerListResponse,
    CustomerProfileCreate,
    CustomerProfileResponse,
    CustomerProfileSummary,
    FollowUpSummary,
    InteractionCreate,
    InteractionHistoryEntry,
    InteractionHistoryResponse,
    InteractionResponse,
    PaginationModel,
    PersonalityProfileModel,
    ProfileSummaryModel,
)
from src.app.customers.dependencies import (
    get_decision_service,
    get_interaction_repository,
    get_personality_engine,
    get_profile_repository,
    get_search_service,
)
from src.app.customers.repositories.interaction_repository import InteractionRepository
from src.app.customers.repositories.profile_repository import CustomerProfile, CustomerProfileRepository
from src.app.customers.services.decision_service import DecisionInsight, DecisionService
from src.app.customers.services.personality_engine import PersonalityEngine
from src.app.customers.services.search_service import CustomerSearchService


router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.post("", response_model=CustomerProfileResponse, status_code=status.HTTP_201_CREATED)
def create_customer_profile(
    payload: CustomerProfileCreate,
    repository: CustomerProfileRepository = Depends(get_profile_repository),
    personality_engine: PersonalityEngine = Depends(get_personality_engine),
    decision_service: DecisionService = Depends(get_decision_service),
) -> CustomerProfileResponse:
    profile = repository.create_profile(payload.dict(exclude_unset=True))
    personality = personality_engine.evaluate(payload.dict(exclude_unset=True))
    decision = decision_service.evaluate(payload.dict(exclude_unset=True), interactions=[])
    summary = _build_profile_summary(personality, decision)
    repository.record_summary(
        uuid.UUID(str(profile.customer_id)),
        traits=personality.traits,
        summary=summary,
        recommendation_ready=profile.recommendation_ready,
        profile_score=profile.profile_score,
    )
    refreshed = repository.get_profile(profile.customer_id)
    return _to_profile_response(refreshed, personality, summary)


@router.get("", response_model=CustomerListResponse)
def list_customer_profiles(
    personality_type: str | None = Query(None),
    budget_range: str | None = Query(None),
    search: str | None = Query(None),
    sales_stage: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search_service: CustomerSearchService = Depends(get_search_service),
) -> CustomerListResponse:
    page = search_service.search(
        personality_type=personality_type,
        budget_range=budget_range,
        search=search,
        sales_stage=sales_stage,
        limit=limit,
        offset=offset,
    )
    customers = [
        CustomerProfileSummary(
            id=result.customer_id,
            name=result.name,
            personality_type=result.personality_type,
            budget_range=result.budget_range,
            sales_stage=result.sales_stage,
            interaction_count=result.interaction_count,
            last_interaction=None,
            profile_completeness=0.0,
        )
        for result in page.customers
    ]
    pagination = PaginationModel(limit=page.pagination.limit, offset=page.pagination.offset, has_more=page.pagination.has_more)
    return CustomerListResponse(customers=customers, total_count=page.total, pagination=pagination)


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer_profile(
    customer_id: uuid.UUID,
    repository: CustomerProfileRepository = Depends(get_profile_repository),
    interactions: InteractionRepository = Depends(get_interaction_repository),
    personality_engine: PersonalityEngine = Depends(get_personality_engine),
    decision_service: DecisionService = Depends(get_decision_service),
) -> CustomerDetailResponse:
    try:
        profile = repository.get_profile(customer_id)
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="customer_not_found") from exc

    history = interactions.list_for_customer(customer_id)
    analytics = interactions.analytics_for_customer(customer_id)
    personality = personality_engine.evaluate(_profile_to_payload(profile))
    decision = decision_service.evaluate(_profile_to_payload(profile), interactions=[record.__dict__ for record in history])

    summary = profile.summary or _build_profile_summary(personality, decision)
    detail = CustomerDetailResponse(
        id=str(profile.customer_id),
        name=profile.name,
        demographics=profile.demographics,
        personality_profile=PersonalityProfileModel(
            type=personality.type,
            traits=dict(personality.traits),
            communication_style=personality.communication_style,
            confidence=personality.confidence,
        ),
        communication_preferences=profile.communication_preferences,
        decision_factors=profile.decision_factors,
        buying_context=profile.buying_context,
        interaction_history=[
            InteractionHistoryEntry(
                id=str(entry.interaction_id),
                date=entry.occurred_at,
                type=entry.interaction_type,
                duration_minutes=entry.duration_minutes,
                outcome=entry.outcome,
                recommendation_used=None,
            )
            for entry in history
        ],
        recommendations_generated=summary.get("recommendations_generated", 0),
        average_recommendation_effectiveness=summary.get("average_effectiveness", 0.0),
        created_at=profile.created_at,
        last_updated=profile.updated_at,
    )
    detail.interaction_summary = analytics
    return detail


@router.post("/{customer_id}/interactions", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def log_interaction(
    customer_id: uuid.UUID,
    payload: InteractionCreate,
    interactions: InteractionRepository = Depends(get_interaction_repository),
    decision_service: DecisionService = Depends(get_decision_service),
    repository: CustomerProfileRepository = Depends(get_profile_repository),
    personality_engine: PersonalityEngine = Depends(get_personality_engine),
) -> InteractionResponse:
    record = interactions.record(customer_id, payload.dict(exclude_unset=True))
    profile = repository.get_profile(customer_id)
    personality = personality_engine.evaluate(_profile_to_payload(profile))
    decision = decision_service.evaluate(_profile_to_payload(profile), interactions=[record.__dict__])
    summary = _build_profile_summary(personality, decision)
    repository.record_summary(
        customer_id,
        traits=personality.traits,
        summary=summary,
        recommendation_ready=profile.recommendation_ready,
        profile_score=profile.profile_score,
    )
    return InteractionResponse(
        interaction_id=str(record.interaction_id),
        customer_id=str(record.customer_id),
        recorded_at=record.occurred_at,
        profile_updates={
            "sales_stage": record.sales_stage,
            "follow_up_required": payload.follow_up.get("required") if payload.follow_up else False,
        },
    )


@router.get("/{customer_id}/interactions", response_model=InteractionHistoryResponse)
def list_interactions(
    customer_id: uuid.UUID,
    interactions: InteractionRepository = Depends(get_interaction_repository),
) -> InteractionHistoryResponse:
    history = interactions.list_for_customer(customer_id)
    analytics = interactions.analytics_for_customer(customer_id)
    return InteractionHistoryResponse(
        customer_id=str(customer_id),
        interactions=[
            InteractionHistoryEntry(
                id=str(entry.interaction_id),
                date=entry.occurred_at,
                type=entry.interaction_type,
                duration_minutes=entry.duration_minutes,
                outcome=entry.outcome,
                recommendation_used=None,
            )
            for entry in history
        ],
        interaction_summary=analytics,
    )


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary(
    repository: CustomerProfileRepository = Depends(get_profile_repository),
    interactions: InteractionRepository = Depends(get_interaction_repository),
) -> AnalyticsSummaryResponse:
    summary = AnalyticsSummaryResponse(
        total_customers=repository.total_customers(),
        average_profile_score=repository.average_profile_score(),
        personality_distribution=repository.personality_distribution(),
        top_decision_factors=repository.top_decision_factors(),
        recent_follow_ups=[
            FollowUpSummary(
                interaction_id=str(item.interaction_id),
                customer_id=str(item.customer_id),
                follow_up_type=item.follow_up_type,
                follow_up_at=item.follow_up_at,
                notes=item.notes,
            )
            for item in interactions.recent_follow_ups()
        ],
    )
    return summary


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _build_profile_summary(personality: PersonalityEngine | Any, decision: DecisionInsight) -> dict[str, Any]:
    traits = getattr(personality, "traits", {}) if not isinstance(personality, dict) else personality.get("traits", {})
    key_traits = [
        f"{getattr(personality, 'primary_trait', 'steady')}_oriented",
        *decision.primary_factors[:2],
    ]
    summary = {
        "key_traits": [trait for trait in key_traits if trait],
        "optimal_sales_approach": getattr(personality, "communication_style", None) or "consultative",
        "potential_objections": decision.objection_themes or decision.deal_breakers,
        "recommendations_generated": 0,
        "average_effectiveness": 0.0,
    }
    if traits:
        summary["trait_scores"] = dict(traits)
    return summary


def _profile_to_payload(profile: CustomerProfile) -> dict[str, Any]:
    return {
        "name": profile.name,
        "demographics": profile.demographics,
        "personality_assessment": {
            "type": profile.personality_type,
            "confidence": profile.personality_confidence,
        },
        "communication_preferences": profile.communication_preferences,
        "decision_factors": profile.decision_factors,
        "buying_context": profile.buying_context,
        "sales_stage": profile.sales_stage,
        "current_interest": profile.current_interest,
    }


__all__ = ["router"]
