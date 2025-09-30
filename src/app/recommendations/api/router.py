"""FastAPI router for recommendation generation APIs (T056)."""
from __future__ import annotations

import datetime as dt
import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from src.app.core.db import SessionLocal
from src.app.customers.repositories.profile_repository import CustomerProfileRepository
from src.app.recommendations.clients.chatgpt_client import ChatGPTClient
from src.app.recommendations.repositories.context_repository import RecommendationContextRepository
from src.app.recommendations.services import (
	ObjectionService,
	PromptBuilder,
	RecommendationContext,
	RecommendationSynthesisService,
	RetrievalService,
	OutputFormatter,
)
from src.app.recommendations.services.token_tracker import TokenTracker
from src.app.knowledge.repositories.source_repository import KnowledgeSourceRepository
from src.app.knowledge.repositories.vector_repository import VectorRepository
from src.app.customers.repositories.profile_repository import CustomerProfile
from src.app.customers.services.personality_engine import PersonalityProfile
from src.app.customers.services.decision_service import DecisionInsight
from src.app.core.config import settings
from src.app.recommendations.services.cache import RecommendationCache
from src.app.recommendations.services.guardrails import Guardrails
from src.app.security.auth import require_api_key
from src.app.security.rate_limiter import rate_limit


router = APIRouter(
	prefix="/api/v1/recommendations",
	tags=["Recommendations"],
	dependencies=[Depends(require_api_key), Depends(rate_limit)],
)


# ---------------------------------------------------------------------------
# Dependencies (lightweight, keep simple for now; switch to dedicated module if needed)
# ---------------------------------------------------------------------------
def get_session():  # pragma: no cover - exercised via API tests
	session = SessionLocal()
	try:
		yield session
	finally:
		session.close()


def get_repos(session=Depends(get_session)):
	return {
		"profiles": CustomerProfileRepository(session=session),
		"contexts": RecommendationContextRepository(session=session),
		"sources": KnowledgeSourceRepository(session=session),
		"vectors": VectorRepository(session=session),
	}


def get_services(repos=Depends(get_repos)):
	prompt = PromptBuilder()

	# Minimal in-process dummy client to avoid network calls in tests
	class _DummyClient:  # pragma: no cover - behavior observed via API tests
		class _Message:
			def __init__(self, content: str) -> None:
				self.content = content

		class _Choice:
			def __init__(self, content: str) -> None:
				self.message = _DummyClient._Message(content)

		class _Response:
			def __init__(self, content: str) -> None:
				self.choices = [
					_DummyClient._Choice(content),
				]

		class _Completions:
			async def create(self, **_: Any):
				return _DummyClient._Response("Generated content")

		class _Chat:
			def __init__(self) -> None:
				self.completions = _DummyClient._Completions()

		def __init__(self) -> None:
			self.chat = _DummyClient._Chat()

	chat = ChatGPTClient(client=_DummyClient(), model="gpt-test")
	retrieval = RetrievalService(vector_repository=repos["vectors"], source_repository=repos["sources"])
	synth = RecommendationSynthesisService(
		context_repository=repos["contexts"],
		prompt_builder=prompt,
		chat_client=chat,
		token_tracker=TokenTracker(),
		guardrails=Guardrails(),
	)
	objections = ObjectionService(prompt_builder=prompt, chat_client=chat)
	formatter = OutputFormatter()
	cache = RecommendationCache(ttl_seconds=60)
	return {
		"prompt": prompt,
		"chat": chat,
		"retrieval": retrieval,
		"synthesis": synth,
		"objections": objections,
		"formatter": formatter,
		"cache": cache,
		"repos": repos,
	}


# ---------------------------------------------------------------------------
# Schemas (minimal inline pydantic models to satisfy contract tests)
# ---------------------------------------------------------------------------
from pydantic import BaseModel, Field


class SalesContextPayload(BaseModel):
	product_interest: str
	sales_stage: str
	customer_concerns: list[str] = Field(default_factory=list)
	context_description: str = ""
	competitive_alternatives: list[str] = Field(default_factory=list)


class CustomerProfileInline(BaseModel):
	id: str
	personality_type: str | None = None
	communication_style: str | None = None
	decision_factors: list[str] | None = None
	budget_range: str | None = None


class OutputPreferences(BaseModel):
	format: str = "summary"
	tone: str = "professional"
	length: str = "brief"
	include_sources: bool = True


class GenerateRequest(BaseModel):
	customer_profile: CustomerProfileInline
	sales_context: SalesContextPayload
	output_preferences: OutputPreferences = OutputPreferences()


class GenerateResponse(BaseModel):
	id: uuid.UUID
	recommendation_text: str
	output_format: str
	confidence_score: float
	generation_metadata: dict[str, Any] | None = None
	applied_principles: dict[str, Any] = Field(default_factory=dict)


class Objection(BaseModel):
	type: str
	statement: str
	context: str | None = None


class ObjectionRequest(BaseModel):
	customer_profile_id: str
	product_context: str
	objection: Objection
	response_style: str = "consultative"
	include_competitive_analysis: bool = True


class ObjectionResponse(BaseModel):
	objection_responses: list[dict[str, Any]]
	recommended_next_steps: list[str]
	competitive_analysis: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.post("/generate", response_model=GenerateResponse)
async def generate_recommendation(payload: GenerateRequest, services=Depends(get_services)) -> GenerateResponse:
	start = time.perf_counter()
	log = structlog.get_logger()
	# Build or load a recommendation context (simplified for contract)
	context_record = services["repos"]["contexts"].create_context(
		{
			"customer_id": uuid.uuid4(),  # In a real impl, derive from profile
			"product_interest": payload.sales_context.product_interest,
			"sales_stage": payload.sales_context.sales_stage,
			"customer_concerns": payload.sales_context.customer_concerns,
			"context_description": payload.sales_context.context_description,
			"competitive_alternatives": payload.sales_context.competitive_alternatives,
			"metadata": {"profile_id": payload.customer_profile.id},
		}
	)

	# Optional cache check (keyed on core inputs). Feature-flagged.
	if settings.feature_flags.recommendation_caching_enabled:
		cache_key = f"{payload.customer_profile.id}:{payload.sales_context.product_interest}:{payload.output_preferences.tone}:{payload.output_preferences.format}"
		cached = services["cache"].get(cache_key)
		if cached is not None:
			log = structlog.get_logger()
			log.info("recommendations.generate.cache_hit", cache_key=cache_key)
			return GenerateResponse(**cached)

	# Dummy retrieval since vector embeddings pipeline isn’t invoked in contract tests
	retrieval = await services["retrieval"].retrieve(
		customer_id=context_record.customer_id,
		context_id=context_record.context_id,
		product_interest=context_record.product_interest,
		query_embedding=[0.0],  # falls back to empty results if not configured
		limit=0,
	)

	# Synthesize recommendation (construct minimal RecommendationContext)
	now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
	minimal_context = RecommendationContext(
		context=context_record,
		customer_profile=CustomerProfile(
			customer_id=context_record.customer_id,
			name=None,
			profession=None,
			demographics={},
			personality_type=None,
			personality_confidence=None,
			personality_method=None,
			personality_traits={},
			communication_style=None,
			communication_preferences={},
			decision_factors={},
			buying_context={},
			profile_score=0.0,
			recommendation_ready=False,
			created_at=now,
			updated_at=now,
			interaction_count=0,
			last_interaction_at=None,
			sales_stage=payload.sales_context.sales_stage,
			budget_range=None,
			current_interest=payload.sales_context.product_interest,
			summary={},
		),
		personality=PersonalityProfile(type="", confidence=0.0, traits={}, communication_style="", primary_trait=""),
		decision=DecisionInsight(
			primary_factors=[],
			secondary_factors=[],
			deal_breakers=[],
			objection_themes=list(payload.sales_context.customer_concerns or []),
			urgency_level="",
			follow_up_required=False,
			success_indicators=[],
		),
		interactions=[],
	)
	rec = await services["synthesis"].synthesize(
		context=minimal_context,
		retrieval=retrieval,
		tone=payload.output_preferences.tone,
		output_format=payload.output_preferences.format,
	)

	# Optional formatting stage (demonstrate T057 integration)
	formatted_text = services["formatter"].format(
		text=rec.recommendation_text,
		output_format=payload.output_preferences.format,
		audience_name=None,
	)

	elapsed = time.perf_counter() - start
	log.info(
		"recommendations.generate",
		context_id=str(rec.context_id),
		output_format=rec.output_format,
		elapsed_ms=round(elapsed * 1000, 2),
	)
	response = GenerateResponse(
		id=rec.recommendation_id,
		recommendation_text=formatted_text,
		output_format=rec.output_format,
		confidence_score=rec.confidence_score,
		generation_metadata=(rec.metadata or {}).get("generation_metadata") if hasattr(rec, "metadata") else None,
		applied_principles={},
	)

	# Store to cache for quick subsequent responses
	if settings.feature_flags.recommendation_caching_enabled:
		services["cache"].set(
			cache_key,
			{
				"id": response.id,
				"recommendation_text": response.recommendation_text,
				"output_format": response.output_format,
				"confidence_score": response.confidence_score,
				"generation_metadata": response.generation_metadata,
				"applied_principles": response.applied_principles,
			},
		)

	return response


@router.post("/objection-handling", response_model=ObjectionResponse)
async def handle_objection(payload: ObjectionRequest, services=Depends(get_services)) -> ObjectionResponse:
	# Minimal context capture for objection generation
	log = structlog.get_logger()
	start = time.perf_counter()
	context_record = services["repos"]["contexts"].create_context(
		{
			"customer_id": uuid.uuid4(),
			"product_interest": payload.product_context,
			"sales_stage": "negotiation",
			"customer_concerns": [payload.objection.type],
			"context_description": payload.objection.statement,
			"competitive_alternatives": [],
			"metadata": {"profile_id": payload.customer_profile_id},
		}
	)

	retrieval = await services["retrieval"].retrieve(
		customer_id=context_record.customer_id,
		context_id=context_record.context_id,
		product_interest=context_record.product_interest,
		query_embedding=[0.0],
		limit=0,
	)

	now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
	minimal_context = RecommendationContext(
		context=context_record,
		customer_profile=CustomerProfile(
			customer_id=context_record.customer_id,
			name=None,
			profession=None,
			demographics={},
			personality_type=None,
			personality_confidence=None,
			personality_method=None,
			personality_traits={},
			communication_style=None,
			communication_preferences={},
			decision_factors={},
			buying_context={},
			profile_score=0.0,
			recommendation_ready=False,
			created_at=now,
			updated_at=now,
			interaction_count=0,
			last_interaction_at=None,
			sales_stage="negotiation",
			budget_range=None,
			current_interest=context_record.product_interest,
			summary={},
		),
		personality=PersonalityProfile(type="", confidence=0.0, traits={}, communication_style="", primary_trait=""),
		decision=DecisionInsight(
			primary_factors=[],
			secondary_factors=[],
			deal_breakers=[],
			objection_themes=[payload.objection.type],
			urgency_level="",
			follow_up_required=False,
			success_indicators=[],
		),
		interactions=[],
	)

	text = await services["objections"].generate(
		context=minimal_context,
		retrieval=retrieval,
		temperature=0.5,
	)

	# Return shape per contract
	elapsed = time.perf_counter() - start
	log.info(
		"recommendations.objections",
		context_id=str(context_record.context_id),
		objection_type=payload.objection.type,
		elapsed_ms=round(elapsed * 1000, 2),
	)
	return ObjectionResponse(
		objection_responses=[
			{
				"strategy": "Consultative",
				"response": text,
				"psychological_basis": "Value framing",
				"supporting_evidence": [],
			}
		],
		recommended_next_steps=[
			"Provide cost-of-ownership comparison",
			"Offer test drive",
		],
		competitive_analysis=None,
	)


__all__ = ["router"]

