"""Tests for the profile summary helper service."""
from __future__ import annotations

from src.app.customers.services.decision_service import DecisionInsight
from src.app.customers.services.personality_engine import PersonalityProfile
from src.app.customers.services.summary_service import build_profile_summary


def test_build_profile_summary_merges_personality_and_decision_data() -> None:
    personality = PersonalityProfile(
        type="D",
        confidence=0.82,
        traits={"dominant": 0.7, "steady": 0.1, "influential": 0.1, "conscientious": 0.1},
        communication_style="direct",
        primary_trait="dominant",
    )
    decision = DecisionInsight(
        primary_factors=["performance", "safety"],
        secondary_factors=["value"],
        deal_breakers=["price"],
        objection_themes=["price"],
        urgency_level="high",
        follow_up_required=True,
        success_indicators=["positive_response:technology"],
    )

    summary = build_profile_summary(personality, decision)

    assert summary["optimal_sales_approach"] == "direct"
    assert "dominant_oriented" in summary["key_traits"]
    assert summary["potential_objections"] == ["price"]
    assert summary["urgency_level"] == "high"
    assert summary["follow_up_required"] is True
    assert "trait_scores" in summary and summary["trait_scores"]["dominant"] == 0.7
    assert summary["success_indicators"] == ["positive_response:technology"]
