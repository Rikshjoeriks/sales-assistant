"""Integration tests covering customer management endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest


@pytest.mark.asyncio
async def test_create_list_and_detail_customer(async_client) -> None:
    payload = {
        "name": "Integration Tester",
        "demographics": {
            "age": 34,
            "profession": "Engineer",
            "location": "Seattle, WA",
            "income_range": "75k_100k",
        },
        "personality_assessment": {
            "type": "D",
            "confidence": 0.81,
            "assessment_method": "conversation_analysis",
        },
        "communication_preferences": {
            "style": "direct",
            "preferred_channels": ["email"],
            "response_time_expectation": "same_day",
        },
        "decision_factors": {
            "primary": ["performance", "safety"],
            "secondary": ["technology"],
            "deal_breakers": ["poor_reliability"],
        },
        "buying_context": {
            "budget_range": "40k_60k",
            "timeline": "within_3_months",
            "financing_preference": "lease",
            "trade_in_vehicle": "2018 Honda Civic",
        },
    }

    create_response = await async_client.post("/api/v1/customers", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["personality_type"] == "D"
    assert created["profile_completeness"] >= 0.7

    list_response = await async_client.get("/api/v1/customers?limit=5&offset=0")
    assert list_response.status_code == 200
    listing = list_response.json()
    assert listing["total_count"] >= 1
    assert listing["customers"][0]["id"] == created["id"]

    detail_response = await async_client.get(f"/api/v1/customers/{created['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["personality_profile"]["type"] == "D"
    assert detail["demographics"]["profession"] == "Engineer"


@pytest.mark.asyncio
async def test_interaction_logging_and_summary(async_client) -> None:
    creation = await async_client.post(
        "/api/v1/customers",
        json={
            "name": "Interaction Tester",
            "demographics": {"location": "Portland, OR"},
            "personality_assessment": {"type": "I"},
            "communication_preferences": {"style": "collaborative"},
            "decision_factors": {"primary": ["technology"]},
            "buying_context": {"budget_range": "35k_45k"},
        },
    )
    customer_id = creation.json()["id"]

    interaction_payload = {
        "interaction_type": "sales_call",
        "date": datetime.now(tz=timezone.utc).isoformat(),
        "duration_minutes": 30,
        "products_discussed": ["2024 Model"],
        "customer_feedback": {
            "interest_level": "medium",
            "primary_concerns": ["price"],
            "positive_responses": ["technology"],
        },
        "salesperson_notes": "Customer wants to compare options.",
        "outcome": "interested",
        "follow_up": {"required": True, "date": datetime.now(tz=timezone.utc).isoformat()},
    }

    post_interaction = await async_client.post(
        f"/api/v1/customers/{customer_id}/interactions",
        json=interaction_payload,
    )
    assert post_interaction.status_code == 201
    interaction_id = post_interaction.json()["interaction_id"]

    list_interactions = await async_client.get(f"/api/v1/customers/{customer_id}/interactions")
    assert list_interactions.status_code == 200
    history = list_interactions.json()
    assert history["customer_id"] == customer_id
    assert history["interactions"][0]["id"] == interaction_id

    analytics_response = await async_client.get("/api/v1/customers/analytics/summary")
    assert analytics_response.status_code == 200
    summary = analytics_response.json()
    assert summary["total_customers"] >= 1
    assert "personality_distribution" in summary
    assert summary["recent_follow_ups"][0]["customer_id"] == customer_id
