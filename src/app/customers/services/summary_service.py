"""Utilities for building customer profile summaries."""
from __future__ import annotations

from typing import Any

from src.app.customers.repositories.profile_repository import CustomerProfile
from src.app.customers.services.decision_service import DecisionInsight
from src.app.customers.services.personality_engine import PersonalityProfile


def build_profile_summary(personality: PersonalityProfile, decision: DecisionInsight) -> dict[str, Any]:
    """Combine personality and decision insights into a lightweight summary payload."""
    key_traits: list[str] = []
    if personality.primary_trait:
        key_traits.append(f"{personality.primary_trait}_oriented")
    key_traits.extend(decision.primary_factors[:2])

    summary: dict[str, Any] = {
        "key_traits": [trait for trait in key_traits if trait],
        "optimal_sales_approach": personality.communication_style or "consultative",
        "potential_objections": decision.objection_themes or decision.deal_breakers,
        "recommendations_generated": 0,
        "average_effectiveness": 0.0,
        "follow_up_required": decision.follow_up_required,
        "urgency_level": decision.urgency_level,
    }

    trait_scores = dict(personality.traits)
    if trait_scores:
        summary["trait_scores"] = trait_scores

    if decision.success_indicators:
        summary["success_indicators"] = decision.success_indicators

    return summary


def profile_to_evaluation_payload(profile: CustomerProfile) -> dict[str, Any]:
    """Convert a persisted profile into the mapping expected by evaluators."""
    return {
        "name": profile.name,
        "demographics": profile.demographics,
        "personality_assessment": {
            "type": profile.personality_type,
            "confidence": profile.personality_confidence,
            "assessment_method": profile.personality_method,
        },
        "communication_preferences": profile.communication_preferences,
        "decision_factors": profile.decision_factors,
        "buying_context": profile.buying_context,
        "sales_stage": profile.sales_stage,
        "current_interest": profile.current_interest,
    }


__all__ = ["build_profile_summary", "profile_to_evaluation_payload"]
