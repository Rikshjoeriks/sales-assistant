"""Tests for the recommendation sales context repository."""
from __future__ import annotations

import uuid

import pytest

from src.app.recommendations.repositories.context_repository import (
    RecommendationContextRepository,
    RecommendationRecord,
    SalesContextRecord,
)


@pytest.fixture()
def context_payload() -> dict[str, object]:
    return {
        "customer_id": uuid.uuid4(),
        "product_interest": "2025 Ion Hybrid",
        "sales_stage": "presentation",
        "customer_concerns": ["price", "battery_life"],
        "context_description": "Customer comparing hybrid options for long commute.",
        "urgency_level": "medium",
        "competitive_alternatives": ["Model Y", "Prius Prime"],
    }


@pytest.fixture()
def recommendation_payload() -> dict[str, object]:
    return {
        "recommendation_text": "Highlight safety ratings and extended warranty options.",
        "output_format": "email",
        "psychological_principles": ["authority", "social_proof"],
        "technical_features": ["battery_range", "safety_rating"],
        "communication_techniques": ["storytelling"],
        "confidence_score": 0.84,
        "token_count": 1234,
        "metadata": {"audience": "executive"},
    }


@pytest.fixture()
def source_references() -> list[dict[str, object]]:
    return [
        {
            "source_id": uuid.uuid4(),
            "concept_id": uuid.uuid4(),
            "reference_type": "supporting_evidence",
            "relevance_score": 0.92,
            "page_reference": "Chapter 4",
        }
    ]


def test_create_context_persists_data(db_session, context_payload) -> None:
    repository = RecommendationContextRepository(session=db_session)
    context = repository.create_context(context_payload)

    assert isinstance(context, SalesContextRecord)
    assert context.product_interest == "2025 Ion Hybrid"
    assert context.sales_stage == "presentation"
    assert context.customer_concerns == ["price", "battery_life"]

    fetched = repository.get_context(context.context_id)
    assert fetched.context_description.startswith("Customer comparing")


def test_record_recommendation_links_sources(db_session, context_payload, recommendation_payload, source_references) -> None:
    repository = RecommendationContextRepository(session=db_session)
    context = repository.create_context(context_payload)

    recommendation = repository.record_recommendation(
        context_id=context.context_id,
        payload=recommendation_payload,
        sources=source_references,
    )

    assert isinstance(recommendation, RecommendationRecord)
    assert recommendation.output_format == "email"
    assert recommendation.source_references[0].reference_type == "supporting_evidence"

    stored = repository.list_recommendations(context.context_id)
    assert len(stored) == 1
    assert stored[0].token_count == 1234
    assert stored[0].source_references[0].page_reference == "Chapter 4"
