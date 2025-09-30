"""Tests for the recommendation context builder."""
from __future__ import annotations

import uuid

from src.app.customers.repositories.interaction_repository import InteractionRepository
from src.app.customers.repositories.profile_repository import CustomerProfileRepository
from src.app.customers.services.decision_service import DecisionService
from src.app.customers.services.personality_engine import PersonalityEngine
from src.app.recommendations.repositories.context_repository import RecommendationContextRepository
from src.app.recommendations.services.context_builder import RecommendationContextBuilder


def _create_customer_profile(profile_repository: CustomerProfileRepository) -> uuid.UUID:
    profile = profile_repository.create_profile(
        {
            "name": "Jordan Patel",
            "demographics": {
                "age": 41,
                "profession": "Systems Engineer",
                "location": "San Jose, CA",
            },
            "personality_assessment": {
                "type": "D",
                "confidence": 0.88,
                "assessment_method": "manual_profile",
            },
            "communication_preferences": {
                "style": "direct",
                "preferred_channels": ["email"],
            },
            "decision_factors": {
                "primary": ["performance", "technology"],
                "secondary": ["safety"],
            },
            "buying_context": {
                "budget_range": "45k_60k",
                "timeline": "within_2_months",
            },
            "sales_stage": "presentation",
            "current_interest": "2025 Ion Hybrid",
        }
    )
    return profile.customer_id


def _record_interactions(
    interaction_repository: InteractionRepository,
    customer_id: uuid.UUID,
) -> None:
    interaction_repository.record(
        customer_id,
        {
            "interaction_type": "spec_review",
            "date": "2025-09-24T15:30:00+00:00",
            "duration_minutes": 45,
            "products_discussed": ["2025 Ion Hybrid"],
            "customer_feedback": {
                "interest_level": "medium",
                "primary_concerns": ["battery_life"],
                "positive_responses": ["safety_ratings"],
            },
            "follow_up": {
                "required": True,
                "type": "email",
                "date": "2025-09-28T09:00:00+00:00",
            },
            "sales_stage": "negotiation",
        },
    )


def test_create_context_enriches_with_customer_signals(db_session) -> None:
    profile_repository = CustomerProfileRepository(session=db_session)
    interaction_repository = InteractionRepository(session=db_session, profile_repository=profile_repository)
    context_repository = RecommendationContextRepository(session=db_session)

    customer_id = _create_customer_profile(profile_repository)
    _record_interactions(interaction_repository, customer_id)

    builder = RecommendationContextBuilder(
        context_repository=context_repository,
        profile_repository=profile_repository,
        interaction_repository=interaction_repository,
        personality_engine=PersonalityEngine(),
        decision_service=DecisionService(),
    )

    result = builder.create_context(
        customer_id=customer_id,
        product_interest="2025 Ion Hybrid",
        sales_stage="negotiation",
        context_description="Customer evaluating hybrid options with focus on safety and battery life.",
        customer_concerns=["battery_life", "price"],
        urgency_level="medium",
        competitive_alternatives=["Model Y", "Prius Prime"],
        metadata={"campaign": "fall-2025"},
    )

    assert result.context.product_interest == "2025 Ion Hybrid"
    assert result.context.customer_concerns == ["battery_life", "price"]
    assert result.context.metadata["campaign"] == "fall-2025"

    assert result.customer_profile.customer_id == customer_id
    assert result.personality.type == "D"
    assert "performance" in result.decision.primary_factors
    assert result.decision.follow_up_required is True
    assert len(result.interactions) == 1


def test_create_context_defaults_lists_to_empty(db_session) -> None:
    profile_repository = CustomerProfileRepository(session=db_session)
    interaction_repository = InteractionRepository(session=db_session, profile_repository=profile_repository)
    context_repository = RecommendationContextRepository(session=db_session)

    customer_id = _create_customer_profile(profile_repository)

    builder = RecommendationContextBuilder(
        context_repository=context_repository,
        profile_repository=profile_repository,
        interaction_repository=interaction_repository,
        personality_engine=PersonalityEngine(),
        decision_service=DecisionService(),
    )

    result = builder.create_context(
        customer_id=customer_id,
        product_interest="2025 Apex Sport",
        sales_stage="prospecting",
        context_description="Initial outreach",
    )

    assert result.context.customer_concerns == []
    assert result.context.competitive_alternatives == []
    assert result.context.metadata == {}
    assert result.decision.primary_factors == ["performance", "technology"]
