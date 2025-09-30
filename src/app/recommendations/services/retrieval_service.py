"""Retrieval service combining sales context with knowledge concepts.

This service bridges the recommendation context with the knowledge system using:
- VectorRepository for similarity over embeddings
- KnowledgeSourceRepository for joining concepts with their sources

It returns a lightweight retrieval bundle for downstream prompt building.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Sequence

from src.app.knowledge.repositories.source_repository import (
    KnowledgeConcept,
    KnowledgeSource,
    KnowledgeSourceRepository,
)
from src.app.knowledge.repositories.vector_repository import SimilarityResult, VectorRepository


@dataclass(slots=True)
class RetrievedItem:
    concept: KnowledgeConcept
    source: KnowledgeSource
    score: float


@dataclass(slots=True)
class RetrievalBundle:
    customer_id: uuid.UUID
    context_id: uuid.UUID
    product_interest: str
    items: list[RetrievedItem]


class RetrievalService:
    """Combine concept similarity scores with source metadata.

    Contract:
    - Inputs: query_embedding (Sequence[float]), optional filters (source_types), limits
    - Output: RetrievalBundle with up to `limit` items sorted by descending score
    - Error modes: empty embeddings -> empty result; mismatched dims handled by VectorRepository
    """

    def __init__(
        self,
        *,
        vector_repository: VectorRepository,
        source_repository: KnowledgeSourceRepository,
    ) -> None:
        self._vectors = vector_repository
        self._sources = source_repository

    async def retrieve(
        self,
        *,
        customer_id: uuid.UUID,
        context_id: uuid.UUID,
        product_interest: str,
        query_embedding: Sequence[float],
        limit: int = 8,
        min_score: float = 0.55,
        source_types: Sequence[str] | None = None,
    ) -> RetrievalBundle:
        if not query_embedding:
            return RetrievalBundle(
                customer_id=customer_id,
                context_id=context_id,
                product_interest=product_interest,
                items=[],
            )

        sim_results: list[SimilarityResult] = await self._vectors.similarity_search(
            query_embedding=query_embedding, limit=limit, min_score=min_score
        )
        concept_ids = [item.concept_id for item in sim_results]
        if not concept_ids:
            return RetrievalBundle(
                customer_id=customer_id,
                context_id=context_id,
                product_interest=product_interest,
                items=[],
            )

        concept_source_rows = self._sources.concepts_with_sources(concept_ids=concept_ids, source_types=source_types)
        score_lookup = {item.concept_id: item.score for item in sim_results}

        items: list[RetrievedItem] = []
        for concept, source in concept_source_rows:
            items.append(
                RetrievedItem(
                    concept=concept,
                    source=source,
                    score=score_lookup.get(concept.concept_id, 0.0),
                )
            )

        # Sort by score descending and enforce limit again (in case join expanded rows)
        items.sort(key=lambda i: i.score, reverse=True)
        if limit and len(items) > limit:
            items = items[:limit]

        return RetrievalBundle(
            customer_id=customer_id,
            context_id=context_id,
            product_interest=product_interest,
            items=items,
        )


__all__ = ["RetrievedItem", "RetrievalBundle", "RetrievalService"]
