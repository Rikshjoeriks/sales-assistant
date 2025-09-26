"""Decision service behavioural tests."""
from __future__ import annotations

from datetime import datetime, timezone

from src.app.customers.services.decision_service import DecisionInsight, DecisionService


def _interaction(**kwargs):
    base = {
        "customer_feedback": {
            "primary_concerns": ["price"],
            "positive_responses": ["safety"],
        },
        "outcome": "interested",
        "follow_up": {"required": True, "date": datetime.now(tz=timezone.utc).isoformat()},
        "sales_stage": "presentation",
    }
    base.update(kwargs)
    return base


def test_decision_service_aggregates_profile_and_interactions() -> None:
    service = DecisionService()

    profile = {
        "decision_factors": {
            "primary": ["performance", "safety"],
            "secondary": ["technology"],
            "deal_breakers": ["poor_reliability"],
        },
        "buying_context": {
            "budget_range": "40k_60k",
            "timeline": "within_3_months",
        },
    }

    interactions = [
        _interaction(),
        _interaction(customer_feedback={"primary_concerns": ["monthly_payment"], "positive_responses": ["technology"]}),
        _interaction(outcome="scheduled_test_drive", follow_up={"required": False}),
    ]

    insight = service.evaluate(profile=profile, interactions=interactions)

    assert isinstance(insight, DecisionInsight)
    assert insight.primary_factors[:2] == ["performance", "safety"]
    assert "price" in insight.objection_themes
    assert "monthly_payment" in insight.objection_themes
    assert insight.urgency_level in {"low", "medium", "high"}
    assert insight.follow_up_required is True
    assert insight.success_indicators[0].startswith("positive_response:")