"""Contract test for objection handling endpoint."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_objection_handling_contract(async_client, sample_customer_profile) -> None:
    payload = {
        "customer_profile_id": sample_customer_profile["id"],
        "product_context": "2024 Toyota Camry Hybrid",
        "objection": {
            "type": "price",
            "statement": "This car is too expensive compared to the Honda Accord",
            "context": "Comparing monthly payments across trims",
        },
        "response_style": "consultative",
        "include_competitive_analysis": True,
    }

    response = await async_client.post("/api/v1/recommendations/objection-handling", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "objection_responses" in body
    assert isinstance(body["objection_responses"], list)
    assert "recommended_next_steps" in body
