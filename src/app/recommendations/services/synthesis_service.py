"""Recommendation synthesis service (T054).

Composes prompt from context + retrieval, calls chat client, and records
the generated recommendation with source attributions via repository.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from src.app.recommendations.clients.chatgpt_client import ChatGPTClient
from src.app.recommendations.repositories.context_repository import (
    RecommendationContextRepository,
    RecommendationRecord,
)
from src.app.recommendations.services.context_builder import RecommendationContext
from src.app.recommendations.services.prompt_builder import PromptBuilder
from src.app.recommendations.services.retrieval_service import RetrievalBundle
from src.app.recommendations.services.token_tracker import TokenTracker
from src.app.recommendations.services.guardrails import Guardrails


@dataclass(slots=True)
class RecommendationSynthesisService:
    context_repository: RecommendationContextRepository
    prompt_builder: PromptBuilder
    chat_client: ChatGPTClient
    token_tracker: TokenTracker | None = None
    guardrails: Guardrails | None = None

    async def synthesize(
        self,
        *,
        context: RecommendationContext,
        retrieval: RetrievalBundle,
        tone: str = "consultative",
        output_format: str = "summary",
        temperature: float = 0.3,
        prompt_token_budget: int = 800,
        timeout: float | None = None,
    ) -> RecommendationRecord:
        # Build prompt
        parts = self.prompt_builder.build(
            context=context,
            retrieval=retrieval,
            tone=tone,
            output_format=output_format,
            prompt_token_budget=prompt_token_budget,
        )

        # Call chat client
        text = await self.chat_client.chat(messages=parts.messages, temperature=temperature, timeout=timeout)
        if self.guardrails is not None:
            text = self.guardrails.filter_text(text)

        # Token + cost estimation (heuristic)
        token_meta = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "estimated_cost_usd": 0.0}
        if self.token_tracker is not None:
            est = self.token_tracker.estimate_tokens(
                prompt_text="\n".join([m["content"] for m in parts.messages if isinstance(m, dict) and m.get("content")]),
                completion_text=text,
            )
            token_meta = {
                **est,
                "estimated_cost_usd": self.token_tracker.estimate_cost(
                    prompt_tokens=est["prompt_tokens"], completion_tokens=est["completion_tokens"]
                ),
            }

        # Map retrieval to source references for persistence
        sources: list[dict[str, Any]] = []
        for item in retrieval.items:
            sources.append(
                {
                    "source_id": item.source.source_id,
                    "concept_id": item.concept.concept_id,
                    "reference_type": "supporting_evidence",
                    "relevance_score": item.score,
                    "page_reference": item.concept.page_reference,
                }
            )

        # Record recommendation
        payload = {
            "recommendation_text": text,
            "output_format": output_format,
            # Reserved fields for future analysis/formatting hooks
            "psychological_principles": [],
            "technical_features": [],
            "communication_techniques": [],
            "metadata": {"tone": tone, "generation_metadata": token_meta},
            "confidence_score": 0.0,
            "token_count": int(token_meta.get("total_tokens", 0)),
        }

        record = self.context_repository.record_recommendation(
            context_id=context.context.context_id,
            payload=payload,
            sources=sources,
        )
        return record


__all__ = ["RecommendationSynthesisService"]
