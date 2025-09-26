"""Vector store repository with SQLAlchemy persistence and pgvector-friendly interface."""
from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.knowledge.models import KnowledgeVectorModel


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

    def __init__(self, *, session: Session | None = None) -> None:
        self._session = session
        # Fallback in-memory cache ensures tests run without Postgres.
        self._cache: dict[uuid.UUID, VectorRecord] = {}

    @property
    def session(self) -> Session | None:
        return self._session

    def upsert(self, records: Sequence[VectorRecord]) -> None:
        if not records:
            return

        for record in records:
            self._cache[record.concept_id] = record

        if self._session:
            for record in records:
                model = self._session.get(KnowledgeVectorModel, record.concept_id)
                if not model:
                    model = KnowledgeVectorModel(
                        concept_id=record.concept_id,
                        embedding=[float(value) for value in record.embedding],
                    )
                    self._session.add(model)
                else:
                    model.embedding = [float(value) for value in record.embedding]
                model.metadata_dict = record.metadata
            self._session.commit()

    async def similarity_search(
        self,
        *,
        query_embedding: Sequence[float],
        limit: int = 5,
        min_score: float = 0.5,
    ) -> list[SimilarityResult]:
        if not query_embedding:
            return []

        records = self._load_records()
        results: list[SimilarityResult] = []
        for record in records:
            score = self._cosine_similarity(query_embedding, record.embedding)
            if score >= min_score:
                results.append(SimilarityResult(concept_id=record.concept_id, score=score, metadata=record.metadata))

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:limit]

    def _load_records(self) -> Iterable[VectorRecord]:
        if not self._session:
            return self._cache.values()

        statement = select(KnowledgeVectorModel)
        models = self._session.execute(statement).scalars().all()
        return [
            VectorRecord(
                concept_id=model.concept_id,
                embedding=tuple(float(value) for value in (model.embedding or [])),
                metadata=model.metadata_dict,
            )
            for model in models
        ]

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
