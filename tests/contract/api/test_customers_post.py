"""Contract test for customer profile creation."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_create_customer_profile_contract(async_client) -> None:
    payload = {
        "name": "Test Customer",
        "demographics": {
            "age": 35,
            "profession": "Engineer",
            "location": "Seattle, WA",
            "income_range": "75k_100k",
        },
        "personality_assessment": {
            "type": "D",
            "confidence": 0.82,
            "assessment_method": "conversation_analysis",
        },
        "communication_preferences": {
            "style": "direct",
            "preferred_channels": ["email", "phone"],
            "response_time_expectation": "same_day",
        },
        "decision_factors": {
            "primary": ["performance", "safety", "value"],
            "secondary": ["brand_reputation"],
            "deal_breakers": ["poor_reliability"],
        },
        "buying_context": {
            "budget_range": "40k_60k",
            "timeline": "within_3_months",
            "financing_preference": "lease",
            "trade_in_vehicle": "2018 Honda Civic",
        },
    }

    response = await async_client.post("/api/v1/customers", json=payload)

    assert response.status_code == 201
    body = response.json()
    for key in {"id", "profile_completeness", "personality_type"}:
        assert key in body
