"""Persistence layer for sales contexts and generated recommendations."""
from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any, Iterable, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.recommendations.models import (
    RecommendationSourceReferenceModel,
    SalesContextModel,
    SalesRecommendationModel,
)


@dataclass(slots=True)
class SalesContextRecord:
    context_id: uuid.UUID
    customer_id: uuid.UUID
    product_interest: str
    sales_stage: str
    customer_concerns: list[str]
    context_description: str
    urgency_level: str | None
    competitive_alternatives: list[str]
    metadata: dict[str, Any]
    created_at: dt.datetime


@dataclass(slots=True)
class SourceReferenceRecord:
    reference_id: uuid.UUID
    source_id: uuid.UUID | None
    concept_id: uuid.UUID | None
    reference_type: str
    relevance_score: float | None
    page_reference: str | None


@dataclass(slots=True)
class RecommendationRecord:
    recommendation_id: uuid.UUID
    context_id: uuid.UUID
    recommendation_text: str
    output_format: str
    psychological_principles: list[str]
    technical_features: list[str]
    communication_techniques: list[str]
    metadata: dict[str, Any]
    confidence_score: float
    token_count: int
    generated_at: dt.datetime
    source_references: list[SourceReferenceRecord]


class RecommendationContextRepository:
    """Repository for managing sales contexts and generated recommendations."""

    def __init__(self, *, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Context operations
    # ------------------------------------------------------------------
    def create_context(self, payload: dict[str, Any]) -> SalesContextRecord:
        model = SalesContextModel()
        self._apply_context_payload(model, payload)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_context_record(model)

    def get_context(self, context_id: uuid.UUID) -> SalesContextRecord:
        model = self._session.get(SalesContextModel, context_id)
        if not model:
            raise KeyError(f"Sales context {context_id} not found")
        return self._to_context_record(model)

    def list_recent_contexts(self, *, limit: int = 20) -> list[SalesContextRecord]:
        statement = (
            select(SalesContextModel)
            .order_by(SalesContextModel.created_at.desc())
            .limit(limit)
        )
        models = self._session.execute(statement).scalars().all()
        return [self._to_context_record(model) for model in models]

    # ------------------------------------------------------------------
    # Recommendation operations
    # ------------------------------------------------------------------
    def record_recommendation(
        self,
        *,
        context_id: uuid.UUID,
        payload: dict[str, Any],
        sources: Iterable[dict[str, Any]] | None = None,
    ) -> RecommendationRecord:
        context_model = self._session.get(SalesContextModel, context_id)
        if not context_model:
            raise KeyError(f"Sales context {context_id} not found")

        recommendation_model = SalesRecommendationModel(context=context_model)
        self._apply_recommendation_payload(recommendation_model, payload)
        self._session.add(recommendation_model)
        self._session.flush()

        for source in sources or []:
            reference_model = RecommendationSourceReferenceModel(
                recommendation=recommendation_model,
                source_id=source.get("source_id"),
                concept_id=source.get("concept_id"),
                reference_type=source.get("reference_type", "supporting_evidence"),
                relevance_score=source.get("relevance_score"),
                page_reference=source.get("page_reference"),
            )
            self._session.add(reference_model)

        self._session.commit()
        self._session.refresh(recommendation_model)
        return self._to_recommendation_record(recommendation_model)

    def list_recommendations(self, context_id: uuid.UUID) -> list[RecommendationRecord]:
        statement = (
            select(SalesRecommendationModel)
            .where(SalesRecommendationModel.context_id == context_id)
            .order_by(SalesRecommendationModel.generated_at.desc())
        )
        models = self._session.execute(statement).scalars().all()
        return [self._to_recommendation_record(model) for model in models]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _apply_context_payload(self, model: SalesContextModel, payload: dict[str, Any]) -> None:
        model.customer_id = payload["customer_id"]
        model.product_interest = cast(str, payload.get("product_interest"))
        model.sales_stage = cast(str, payload.get("sales_stage", "prospecting"))
        model.customer_concerns_json = list(payload.get("customer_concerns", []))
        model.context_description = cast(str, payload.get("context_description", ""))
        model.urgency_level = cast(str | None, payload.get("urgency_level"))
        model.competitive_alternatives_json = list(payload.get("competitive_alternatives", []))
        model.metadata_json = dict(payload.get("metadata", {}))

    def _apply_recommendation_payload(
        self,
        model: SalesRecommendationModel,
        payload: dict[str, Any],
    ) -> None:
        model.recommendation_text = cast(str, payload.get("recommendation_text", ""))
        model.output_format = cast(str, payload.get("output_format", "summary"))
        model.psychological_principles_json = list(payload.get("psychological_principles", []))
        model.technical_features_json = list(payload.get("technical_features", []))
        model.communication_techniques_json = list(payload.get("communication_techniques", []))
        model.metadata_json = dict(payload.get("metadata", {}))
        model.confidence_score = float(payload.get("confidence_score", 0.0) or 0.0)
        model.token_count = int(payload.get("token_count", 0) or 0)
        generated_at = payload.get("generated_at")
        if isinstance(generated_at, dt.datetime):
            model.generated_at = generated_at

    def _to_context_record(self, model: SalesContextModel) -> SalesContextRecord:
        return SalesContextRecord(
            context_id=cast(uuid.UUID, model.id),
            customer_id=cast(uuid.UUID, model.customer_id),
            product_interest=cast(str, model.product_interest),
            sales_stage=cast(str, model.sales_stage),
            customer_concerns=list(model.customer_concerns_json or []),
            context_description=cast(str, model.context_description),
            urgency_level=cast(str | None, model.urgency_level),
            competitive_alternatives=list(model.competitive_alternatives_json or []),
            metadata=dict(model.metadata_json or {}),
            created_at=cast(dt.datetime, model.created_at),
        )

    def _to_source_reference_record(
        self,
        model: RecommendationSourceReferenceModel,
    ) -> SourceReferenceRecord:
        return SourceReferenceRecord(
            reference_id=cast(uuid.UUID, model.id),
            source_id=cast(uuid.UUID | None, model.source_id),
            concept_id=cast(uuid.UUID | None, model.concept_id),
            reference_type=cast(str, model.reference_type),
            relevance_score=cast(float | None, model.relevance_score),
            page_reference=cast(str | None, model.page_reference),
        )

    def _to_recommendation_record(
        self,
        model: SalesRecommendationModel,
    ) -> RecommendationRecord:
        references = [self._to_source_reference_record(ref) for ref in model.source_references]
        return RecommendationRecord(
            recommendation_id=cast(uuid.UUID, model.id),
            context_id=cast(uuid.UUID, model.context_id),
            recommendation_text=cast(str, model.recommendation_text),
            output_format=cast(str, model.output_format),
            psychological_principles=list(model.psychological_principles_json or []),
            technical_features=list(model.technical_features_json or []),
            communication_techniques=list(model.communication_techniques_json or []),
            metadata=dict(model.metadata_json or {}),
            confidence_score=float(model.confidence_score or 0.0),
            token_count=int(model.token_count or 0),
            generated_at=cast(dt.datetime, model.generated_at),
            source_references=references,
        )


__all__ = [
    "RecommendationContextRepository",
    "RecommendationRecord",
    "SalesContextRecord",
    "SourceReferenceRecord",
]
