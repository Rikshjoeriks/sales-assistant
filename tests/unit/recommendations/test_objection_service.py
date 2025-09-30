"""Tests for objection handling service (T055)."""
from __future__ import annotations

import datetime as dt
import uuid

import pytest

from src.app.customers.repositories.profile_repository import CustomerProfile
from src.app.customers.services.decision_service import DecisionInsight
from src.app.customers.services.personality_engine import PersonalityProfile
from src.app.knowledge.repositories.source_repository import KnowledgeConcept, KnowledgeSource
from src.app.recommendations.repositories.context_repository import RecommendationRecord, SalesContextRecord
from src.app.recommendations.services.context_builder import RecommendationContext
from src.app.recommendations.services.prompt_builder import PromptBuilder
from src.app.recommendations.services.retrieval_service import RetrievalBundle, RetrievedItem
from src.app.recommendations.services.objection_service import ObjectionService


class _ChatSpy:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.last_kwargs = None

    async def chat(self, *, messages, temperature=0.4, timeout=None):  # type: ignore[no-untyped-def]
        self.last_kwargs = {"messages": messages, "temperature": temperature, "timeout": timeout}
        return self.response_text


@pytest.fixture()
def sample_context() -> RecommendationContext:
    now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    context = SalesContextRecord(
        context_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        product_interest="2025 Ion Hybrid",
        sales_stage="negotiation",
        customer_concerns=["price", "battery_life"],
        context_description="Discuss pricing and warranty",
        urgency_level="high",
        competitive_alternatives=["Model Y"],
        metadata={},
        created_at=now,
    )
    profile = CustomerProfile(
        customer_id=context.customer_id,
        name="Pat Q",
        profession="Engineer",
        demographics={},
        personality_type="C",
        personality_confidence=0.8,
        personality_method="heuristic",
        personality_traits={},
        communication_style="analytical",
        communication_preferences={},
        decision_factors={"primary": ["total_cost"], "secondary": ["safety"]},
        buying_context={},
        profile_score=0.85,
        recommendation_ready=True,
        created_at=now,
        updated_at=now,
        interaction_count=0,
        last_interaction_at=None,
        sales_stage="negotiation",
        budget_range=None,
        current_interest="2025 Ion Hybrid",
        summary={},
    )
    personality = PersonalityProfile(
        type="C",
        confidence=0.8,
        traits={"conscientious": 0.7},
        communication_style="analytical",
        primary_trait="conscientious",
    )
    decision = DecisionInsight(
        primary_factors=["total_cost"],
        secondary_factors=["safety"],
        deal_breakers=["over_budget"],
        objection_themes=["price", "battery_degradation"],
        urgency_level="high",
        follow_up_required=True,
        success_indicators=[],
    )
    return RecommendationContext(
        context=context,
        customer_profile=profile,
        personality=personality,
        decision=decision,
        interactions=[],
    )


@pytest.fixture()
def sample_retrieval(sample_context: RecommendationContext) -> RetrievalBundle:
    c1 = KnowledgeConcept(
        concept_id=uuid.uuid4(),
        source_id=uuid.uuid4(),
        title="Battery Warranty",
        concept_type="policy",
        content="Battery warranty covers 8 years or 100,000 miles.",
        keywords=["warranty", "battery"],
        page_reference="p.7",
        confidence_score=0.9,
    )
    s1 = KnowledgeSource(
        source_id=c1.source_id,
        title="Warranty Guide",
        author="Support",
        type="pdf",
        version="v3",
        file_path="/docs/warranty.pdf",
        processing_status="done",
        metadata={},
    )
    return RetrievalBundle(
        customer_id=sample_context.context.customer_id,
        context_id=sample_context.context.context_id,
        product_interest=sample_context.context.product_interest,
        items=[RetrievedItem(concept=c1, source=s1, score=0.89)],
    )


@pytest.mark.anyio
async def test_generate_builds_objection_prompt_and_calls_client(sample_context: RecommendationContext, sample_retrieval: RetrievalBundle):
    chat = _ChatSpy(response_text="Objection handling plan")
    builder = PromptBuilder()
    service = ObjectionService(prompt_builder=builder, chat_client=chat)

    result = await service.generate(context=sample_context, retrieval=sample_retrieval, temperature=0.5)

    # It should call the chat client with at least 3 messages (system + user + objections augmentation)
    assert chat.last_kwargs is not None
    msgs = chat.last_kwargs["messages"]
    assert isinstance(msgs, list)
    assert len(msgs) >= 3

    # The final user message should include objection themes and customer concerns
    joined = "\n".join(m.get("content", "") for m in msgs if isinstance(m, dict))
    assert "price" in joined.lower()
    assert "battery" in joined.lower()
    assert "objection" in joined.lower()

    # It should pass through the temperature
    assert chat.last_kwargs["temperature"] == 0.5

    # And return the chat text
    assert result == "Objection handling plan"
