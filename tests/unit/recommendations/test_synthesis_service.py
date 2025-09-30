"""Tests for recommendation synthesis service (T054)."""
from __future__ import annotations

import datetime as dt
import uuid

import pytest

from src.app.customers.repositories.profile_repository import CustomerProfile
from src.app.customers.services.decision_service import DecisionInsight
from src.app.customers.services.personality_engine import PersonalityProfile
from src.app.recommendations.repositories.context_repository import RecommendationRecord, SalesContextRecord
from src.app.recommendations.services.context_builder import RecommendationContext
from src.app.recommendations.services.prompt_builder import PromptParts
from src.app.recommendations.services.retrieval_service import RetrievalBundle, RetrievedItem
from src.app.knowledge.repositories.source_repository import KnowledgeConcept, KnowledgeSource
from src.app.recommendations.services.synthesis_service import RecommendationSynthesisService


class _PromptSpy:
    def __init__(self) -> None:
        self.last_args = None

    def build(self, *, context, retrieval, tone="consultative", output_format="summary", prompt_token_budget=800):  # type: ignore[no-untyped-def]
        self.last_args = {
            "context_id": context.context.context_id,
            "retrieval_count": len(retrieval.items),
            "tone": tone,
            "output_format": output_format,
        }
        return PromptParts(system="sys", user="usr", messages=[{"role": "system", "content": "sys"}, {"role": "user", "content": "usr"}])


class _ChatSpy:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.last_kwargs = None

    async def chat(self, *, messages, temperature=0.3, timeout=None):  # type: ignore[no-untyped-def]
        self.last_kwargs = {"messages": messages, "temperature": temperature, "timeout": timeout}
        return self.response_text


class _RepoSpy:
    def __init__(self) -> None:
        self.call = None

    def record_recommendation(self, *, context_id, payload, sources):  # type: ignore[no-untyped-def]
        self.call = {"context_id": context_id, "payload": payload, "sources": sources}
        # Return a minimal RecommendationRecord-like object
        now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
        return RecommendationRecord(
            recommendation_id=uuid.uuid4(),
            context_id=context_id,
            recommendation_text=payload.get("recommendation_text", ""),
            output_format=payload.get("output_format", "summary"),
            psychological_principles=payload.get("psychological_principles", []),
            technical_features=payload.get("technical_features", []),
            communication_techniques=payload.get("communication_techniques", []),
            metadata=payload.get("metadata", {}),
            confidence_score=float(payload.get("confidence_score", 0.0) or 0.0),
            token_count=int(payload.get("token_count", 0) or 0),
            generated_at=now,
            source_references=[],
        )


@pytest.fixture()
def sample_context() -> RecommendationContext:
    now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    context = SalesContextRecord(
        context_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        product_interest="2025 Ion Hybrid",
        sales_stage="presentation",
        customer_concerns=["battery_life"],
        context_description="Focus on safety and efficiency",
        urgency_level="medium",
        competitive_alternatives=["Model Y"],
        metadata={},
        created_at=now,
    )
    profile = CustomerProfile(
        customer_id=context.customer_id,
        name="Pat Q",
        profession="Engineer",
        demographics={},
        personality_type="D",
        personality_confidence=0.9,
        personality_method="heuristic",
        personality_traits={},
        communication_style="direct",
        communication_preferences={},
        decision_factors={"primary": ["performance"], "secondary": ["safety"]},
        buying_context={},
        profile_score=0.9,
        recommendation_ready=True,
        created_at=now,
        updated_at=now,
        interaction_count=0,
        last_interaction_at=None,
        sales_stage="presentation",
        budget_range=None,
        current_interest="2025 Ion Hybrid",
        summary={},
    )
    personality = PersonalityProfile(
        type="D",
        confidence=0.9,
        traits={"dominant": 0.7},
        communication_style="direct",
        primary_trait="dominant",
    )
    decision = DecisionInsight(
        primary_factors=["performance"],
        secondary_factors=["safety"],
        deal_breakers=[],
        objection_themes=[],
        urgency_level="medium",
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
        title="Battery Performance",
        concept_type="spec",
        content="High-density battery with long cycle life.",
        keywords=["battery"],
        page_reference="p.12",
        confidence_score=0.92,
    )
    s1 = KnowledgeSource(
        source_id=c1.source_id,
        title="Ion Hybrid Whitepaper",
        author="R&D",
        type="pdf",
        version="v1",
        file_path="/docs/ion.pdf",
        processing_status="done",
        metadata={},
    )
    c2 = KnowledgeConcept(
        concept_id=uuid.uuid4(),
        source_id=uuid.uuid4(),
        title="Safety Ratings",
        concept_type="review",
        content="NHTSA 5-star rating.",
        keywords=["safety"],
        page_reference=None,
        confidence_score=0.88,
    )
    s2 = KnowledgeSource(
        source_id=c2.source_id,
        title="NHTSA Summary",
        author=None,
        type="web",
        version=None,
        file_path="https://nhtsa.gov/x",
        processing_status="done",
        metadata={},
    )

    return RetrievalBundle(
        customer_id=sample_context.context.customer_id,
        context_id=sample_context.context.context_id,
        product_interest=sample_context.context.product_interest,
        items=[
            RetrievedItem(concept=c1, source=s1, score=0.91),
            RetrievedItem(concept=c2, source=s2, score=0.82),
        ],
    )


@pytest.mark.anyio
async def test_synthesize_calls_client_and_records_sources(sample_context: RecommendationContext, sample_retrieval: RetrievalBundle):
    prompts = _PromptSpy()
    chat = _ChatSpy(response_text="Recommended text")
    repo = _RepoSpy()

    service = RecommendationSynthesisService(context_repository=repo, prompt_builder=prompts, chat_client=chat)

    result = await service.synthesize(context=sample_context, retrieval=sample_retrieval, output_format="bullet_points", temperature=0.4)

    # Verify chat client received two messages and correct temperature
    assert chat.last_kwargs is not None
    assert len(chat.last_kwargs["messages"]) == 2
    assert chat.last_kwargs["temperature"] == 0.4

    # Verify repository recorded recommendation with sources derived from retrieval
    assert repo.call is not None
    sources = repo.call["sources"]
    assert len(sources) == len(sample_retrieval.items)
    # Ensure mapping includes concept_id/source_id and relevance score
    assert sources[0]["concept_id"] == sample_retrieval.items[0].concept.concept_id
    assert sources[0]["source_id"] == sample_retrieval.items[0].source.source_id
    assert sources[0]["reference_type"] == "supporting_evidence"
    assert sources[0]["relevance_score"] == sample_retrieval.items[0].score
    assert sources[0]["page_reference"] == sample_retrieval.items[0].concept.page_reference

    # Basic shape of result
    assert result.recommendation_text == "Recommended text"
    assert result.output_format == "bullet_points"
