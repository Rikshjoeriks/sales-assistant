"""Tests for prompt template manager (T052)."""
from __future__ import annotations

import datetime as dt
import uuid

import pytest

from src.app.customers.repositories.interaction_repository import InteractionRecord
from src.app.customers.repositories.profile_repository import CustomerProfile
from src.app.customers.services.decision_service import DecisionInsight
from src.app.customers.services.personality_engine import PersonalityProfile
from src.app.knowledge.repositories.source_repository import KnowledgeConcept, KnowledgeSource
from src.app.recommendations.repositories.context_repository import SalesContextRecord
from src.app.recommendations.services.context_builder import RecommendationContext
from src.app.recommendations.services.prompt_builder import PromptBuilder
from src.app.recommendations.services.retrieval_service import RetrievalBundle, RetrievedItem


@pytest.fixture()
def sample_context() -> RecommendationContext:
    now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    context = SalesContextRecord(
        context_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        product_interest="2025 Ion Hybrid",
        sales_stage="negotiation",
        customer_concerns=["battery_life", "price"],
        context_description="Customer evaluating hybrid options",
        urgency_level="medium",
        competitive_alternatives=["Model Y"],
        metadata={"campaign": "fall-2025"},
        created_at=now,
    )
    profile = CustomerProfile(
        customer_id=context.customer_id,
        name="Ari Chen",
        profession="Engineer",
        demographics={"age": 37, "location": "CA"},
        personality_type="D",
        personality_confidence=0.86,
        personality_method="heuristic",
        personality_traits={"direct": 0.8},
        communication_style="direct",
        communication_preferences={"style": "direct", "preferred_channels": ["email"]},
        decision_factors={"primary": ["performance", "technology"], "secondary": ["safety"]},
        buying_context={"budget_range": "45k_60k"},
        profile_score=0.9,
        recommendation_ready=True,
        created_at=now,
        updated_at=now,
        interaction_count=3,
        last_interaction_at=now,
        sales_stage="negotiation",
        budget_range="45k_60k",
        current_interest="2025 Ion Hybrid",
        summary={}
    )
    personality = PersonalityProfile(
        type="D",
        confidence=0.86,
        traits={"direct": 0.8},
        communication_style="direct",
        primary_trait="dominant",
    )
    decision = DecisionInsight(
        primary_factors=["performance", "technology"],
        secondary_factors=["safety"],
        deal_breakers=[],
        objection_themes=[],
        urgency_level="medium",
        follow_up_required=True,
        success_indicators=[],
    )
    interactions: list[InteractionRecord] = []
    return RecommendationContext(
        context=context,
        customer_profile=profile,
        personality=personality,
        decision=decision,
        interactions=interactions,
    )


@pytest.fixture()
def sample_retrieval_bundle(sample_context: RecommendationContext) -> RetrievalBundle:
    c1 = KnowledgeConcept(
        concept_id=uuid.uuid4(),
        source_id=uuid.uuid4(),
        title="Battery Performance",
        concept_type="spec",
        content="High-density battery with 500k cycle life. Extended range in mixed driving.",
        keywords=["battery", "range"],
        page_reference="p.12",
        confidence_score=0.92,
    )
    s1 = KnowledgeSource(
        source_id=c1.source_id,
        title="Ion Hybrid Whitepaper",
        author="R&D Team",
        type="pdf",
        version="v1",
        file_path="/docs/ion_hybrid.pdf",
        processing_status="done",
        metadata={},
    )
    c2 = KnowledgeConcept(
        concept_id=uuid.uuid4(),
        source_id=uuid.uuid4(),
        title="Safety Ratings",
        concept_type="review",
        content="NHTSA 5-star rating. IIHS Top Safety Pick.",
        keywords=["safety"],
        page_reference=None,
        confidence_score=0.89,
    )
    s2 = KnowledgeSource(
        source_id=c2.source_id,
        title="NHTSA Summary",
        author=None,
        type="web",
        version=None,
        file_path="https://nhtsa.gov/example",
        processing_status="done",
        metadata={},
    )

    return RetrievalBundle(
        customer_id=sample_context.context.customer_id,
        context_id=sample_context.context.context_id,
        product_interest=sample_context.context.product_interest,
        items=[
            RetrievedItem(concept=c1, source=s1, score=0.91),
            RetrievedItem(concept=c2, source=s2, score=0.84),
        ],
    )


def test_build_basic_prompt_includes_key_sections(sample_context: RecommendationContext, sample_retrieval_bundle: RetrievalBundle):
    builder = PromptBuilder()
    parts = builder.build(context=sample_context, retrieval=sample_retrieval_bundle, tone="consultative", output_format="bullet_points", prompt_token_budget=600)

    # Validate shape
    assert isinstance(parts.system, str) and isinstance(parts.user, str)
    assert len(parts.messages) == 2
    assert parts.messages[0]["role"] == "system"
    assert parts.messages[1]["role"] == "user"

    # Validate content
    assert "2025 Ion Hybrid" in parts.user
    assert "personality: D" in parts.user
    assert "Ion Hybrid Whitepaper" in parts.user  # citation from source title


def test_truncates_retrieved_items_by_budget(sample_context: RecommendationContext, sample_retrieval_bundle: RetrievalBundle):
    builder = PromptBuilder()
    # Tight budget should keep only top item
    parts = builder.build(context=sample_context, retrieval=sample_retrieval_bundle, prompt_token_budget=60)
    # Expect only the first item's title to appear reliably
    assert "Ion Hybrid Whitepaper" in parts.user
    assert "NHTSA Summary" not in parts.user
