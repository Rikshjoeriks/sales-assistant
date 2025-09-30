"""Recommendation context builder service."""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from typing import Any, Sequence

from src.app.customers.repositories.interaction_repository import (
    InteractionRecord,
    InteractionRepository,
)
from src.app.customers.repositories.profile_repository import (
    CustomerProfile,
    CustomerProfileRepository,
)
from src.app.customers.services.decision_service import DecisionInsight, DecisionService
from src.app.customers.services.personality_engine import PersonalityEngine, PersonalityProfile
from src.app.customers.services.summary_service import profile_to_evaluation_payload
from src.app.recommendations.repositories.context_repository import (
    RecommendationContextRepository,
    SalesContextRecord,
)


@dataclass(slots=True)
class RecommendationContext:
    """Aggregated context required for recommendation generation."""

    context: SalesContextRecord
    customer_profile: CustomerProfile
    personality: PersonalityProfile
    decision: DecisionInsight
    interactions: list[InteractionRecord]


class RecommendationContextBuilder:
    """Compose sales context metadata from customer signals and persistence layers."""

    def __init__(
        self,
        *,
        context_repository: RecommendationContextRepository,
        profile_repository: CustomerProfileRepository,
        interaction_repository: InteractionRepository,
        personality_engine: PersonalityEngine,
        decision_service: DecisionService,
    ) -> None:
        self._contexts = context_repository
        self._profiles = profile_repository
        self._interactions = interaction_repository
        self._personality = personality_engine
        self._decision = decision_service

    def create_context(
        self,
        *,
        customer_id: uuid.UUID,
        product_interest: str,
        sales_stage: str,
        context_description: str,
        customer_concerns: Sequence[str] | None = None,
        urgency_level: str | None = None,
        competitive_alternatives: Sequence[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RecommendationContext:
        """Persist a sales context and enrich it with personality & decision insights."""
        context_payload = {
            "customer_id": customer_id,
            "product_interest": product_interest,
            "sales_stage": sales_stage,
            "context_description": context_description,
            "customer_concerns": list(customer_concerns or []),
            "urgency_level": urgency_level,
            "competitive_alternatives": list(competitive_alternatives or []),
            "metadata": dict(metadata or {}),
        }
        context_record = self._contexts.create_context(context_payload)

        profile = self._profiles.get_profile(customer_id)
        interactions = self._interactions.list_for_customer(customer_id)

        evaluation_payload = profile_to_evaluation_payload(profile)
        personality = self._personality.evaluate(evaluation_payload)
        decision = self._decision.evaluate(
            evaluation_payload,
            interactions=[asdict(interaction) for interaction in interactions],
        )

        return RecommendationContext(
            context=context_record,
            customer_profile=profile,
            personality=personality,
            decision=decision,
            interactions=list(interactions),
        )


__all__ = ["RecommendationContext", "RecommendationContextBuilder"]
