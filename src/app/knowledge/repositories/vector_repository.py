"""Vector store repository with in-memory fallback and pgvector-friendly interface."""
from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence


@dataclass(slots=True)
class VectorRecord:
    concept_id: uuid.UUID
    embedding: tuple[float, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SimilarityResult:
    concept_id: uuid.UUID
    score: float
    metadata: dict[str, Any]


class VectorRepository:
    """Repository abstraction for storing and querying embeddings."""

    def __init__(self, *, session: Any | None = None) -> None:
        self._session = session
        # Fallback in-memory cache ensures tests run without Postgres.
        self._cache: dict[uuid.UUID, VectorRecord] = {}

    def upsert(self, records: Sequence[VectorRecord]) -> None:
        if not records:
            return

        for record in records:
            self._cache[record.concept_id] = record

        if self._session:
            self._persist(records)

    async def similarity_search(
        self,
        *,
        query_embedding: Sequence[float],
        limit: int = 5,
        min_score: float = 0.5,
    ) -> list[SimilarityResult]:
        if not query_embedding:
            return []

        results: list[SimilarityResult] = []
        for record in self._cache.values():
            score = self._cosine_similarity(query_embedding, record.embedding)
            if score >= min_score:
                results.append(SimilarityResult(concept_id=record.concept_id, score=score, metadata=record.metadata))

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:limit]

    def _persist(self, records: Sequence[VectorRecord]) -> None:  # pragma: no cover - requires real DB
        if not hasattr(self._session, "add_all"):
            return
        # The real persistence layer will be implemented when pgvector models are available.

    def _cosine_similarity(self, a: Sequence[float], b: Sequence[float]) -> float:
        if len(a) != len(b):
            raise ValueError("Embedding dimensions do not match")

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


__all__ = ["VectorRecord", "SimilarityResult", "VectorRepository"]
