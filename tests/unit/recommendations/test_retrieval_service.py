"""Unit tests for RetrievalService."""
from __future__ import annotations

import uuid

import pytest

from src.app.knowledge.repositories.source_repository import (
    KnowledgeConcept,
    KnowledgeSource,
    KnowledgeSourceRepository,
)
from src.app.knowledge.repositories.vector_repository import (
    SimilarityResult,
    VectorRepository,
)
from src.app.recommendations.services.retrieval_service import RetrievalService


class DummyVectorRepository(VectorRepository):
    def __init__(self) -> None:
        super().__init__(session=None)
        self._responses: list[SimilarityResult] = []

    async def similarity_search(self, *, query_embedding, limit=5, min_score=0.5):
        # Return the preloaded responses to simulate vector search
        return self._responses[:limit]


class DummySourceRepository(KnowledgeSourceRepository):
    def __init__(self) -> None:
        # Avoid calling parent __init__ to skip Session requirement
        self._rows: list[tuple[KnowledgeConcept, KnowledgeSource]] = []

    def concepts_with_sources(self, *, concept_ids, source_types=None):  # type: ignore[override]
        # Filter by requested concept_ids only
        wanted = set(concept_ids)
        rows = [row for row in self._rows if row[0].concept_id in wanted]
        return rows


@pytest.mark.anyio
async def test_retrieve_returns_sorted_items_and_respects_limit():
    vec = DummyVectorRepository()
    src = DummySourceRepository()
    service = RetrievalService(vector_repository=vec, source_repository=src)

    # Prepare vector results
    c1, c2, c3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    vec._responses = [
        SimilarityResult(concept_id=c1, score=0.91, metadata={}),
        SimilarityResult(concept_id=c2, score=0.88, metadata={}),
        SimilarityResult(concept_id=c3, score=0.72, metadata={}),
    ]

    # Prepare concept/source rows
    def concept(cid, title):
        return KnowledgeConcept(
            concept_id=cid,
            source_id=uuid.uuid4(),
            title=title,
            concept_type="spec",
            content="...",
            keywords=["battery"],
            page_reference=None,
            confidence_score=0.9,
        )

    def source(title):
        return KnowledgeSource(
            source_id=uuid.uuid4(),
            title=title,
            author=None,
            type="pdf",
            version=None,
            file_path="/tmp",
            processing_status="done",
            metadata={},
        )

    src._rows = [
        (concept(c1, "Battery Performance"), source("Ion Hybrid Whitepaper")),
        (concept(c2, "Safety Ratings"), source("NHTSA Summary")),
        (concept(c3, "Charging Options"), source("Charging Guide")),
    ]

    result = await service.retrieve(
        customer_id=uuid.uuid4(),
        context_id=uuid.uuid4(),
        product_interest="2025 Ion Hybrid",
        query_embedding=[0.1, 0.2, 0.3],
        limit=2,
    )

    assert len(result.items) == 2
    # Ensure sorted by score desc (0.91 then 0.88)
    assert result.items[0].score >= result.items[1].score


@pytest.mark.anyio
async def test_retrieve_empty_on_no_embedding():
    vec = DummyVectorRepository()
    src = DummySourceRepository()
    service = RetrievalService(vector_repository=vec, source_repository=src)

    result = await service.retrieve(
        customer_id=uuid.uuid4(),
        context_id=uuid.uuid4(),
        product_interest="2025 Ion Hybrid",
        query_embedding=[],
    )

    assert result.items == []
