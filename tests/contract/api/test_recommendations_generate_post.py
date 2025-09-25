"""Contract test for recommendation generation endpoint."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_recommendation_generation_contract(async_client, sample_customer_profile) -> None:
    payload = {
        "customer_profile": sample_customer_profile,
        "sales_context": {
            "product_interest": "2024 Toyota Camry Hybrid",
            "sales_stage": "presentation",
            "customer_concerns": ["fuel_costs", "reliability"],
            "context_description": "Professional commuter evaluating hybrid sedans",
            "competitive_alternatives": ["Honda Accord Hybrid"],
        },
        "output_preferences": {
            "format": "email",
            "tone": "professional",
            "length": "detailed",
            "include_sources": True,
        },
    }

    response = await async_client.post("/api/v1/recommendations/generate", json=payload)

    assert response.status_code == 200
    body = response.json()
    for key in {"id", "recommendation_text", "output_format", "confidence_score"}:
        assert key in body
    assert "applied_principles" in body
