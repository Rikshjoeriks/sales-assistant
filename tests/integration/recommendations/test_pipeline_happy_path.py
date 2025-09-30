"""Integration flow expectations for the recommendation pipeline."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_recommendation_pipeline_happy_path(sample_customer_profile, openai_client, db_session) -> None:
    from src.app.recommendations.services.pipeline import RecommendationPipeline

    pipeline = RecommendationPipeline(db_session=db_session, openai_client=openai_client)
    sales_context = {
        "product_interest": "2024 Toyota Camry Hybrid",
        "sales_stage": "presentation",
        "customer_concerns": ["fuel_costs", "reliability"],
        "context_description": "Professional commuter evaluating hybrid sedans",
    }

    result = await pipeline.generate(customer_profile=sample_customer_profile, sales_context=sales_context)
    # Validate minimal contract shape
    assert "recommendation_id" in result
    assert "context_id" in result
    assert "recommendation_text" in result and isinstance(result["recommendation_text"], str)
    assert result["output_format"] in {"summary", "email", "bullet", "script", "presentation"}
