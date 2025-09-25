"""Integration flow expectations for the recommendation pipeline."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_recommendation_pipeline_happy_path(sample_customer_profile, openai_client, db_session) -> None:
    from src.app.recommendations.services.pipeline import RecommendationPipeline  # noqa: WPS433

    pipeline = RecommendationPipeline(db_session=db_session, openai_client=openai_client)
    sales_context = {
        "product_interest": "2024 Toyota Camry Hybrid",
        "sales_stage": "presentation",
        "customer_concerns": ["fuel_costs", "reliability"],
        "context_description": "Professional commuter evaluating hybrid sedans",
    }

    with pytest.raises(NotImplementedError):
        await pipeline.generate(customer_profile=sample_customer_profile, sales_context=sales_context)
