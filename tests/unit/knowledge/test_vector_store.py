"""Expectations for the vector repository interface."""
from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest


def test_vector_repository_exposes_core_contract() -> None:
    from src.app.knowledge.repositories.vector_repository import VectorRecord, VectorRepository  # noqa: WPS433

    repository = VectorRepository(session=None)

    concept_id = uuid4()
    repository.upsert([VectorRecord(concept_id=concept_id, embedding=(1.0, 0.0, 0.0))])

    results = asyncio.run(repository.similarity_search(query_embedding=(1.0, 0.0, 0.0), limit=1))



@pytest.mark.asyncio
async def test_vector_repository_similarity_search_contract() -> None:
    from src.app.knowledge.repositories.vector_repository import VectorRecord, VectorRepository  # noqa: WPS433

    repository = VectorRepository()
    target_id = uuid4()
    repository.upsert(
        [
            VectorRecord(concept_id=uuid4(), embedding=(0.0, 1.0, 0.0)),
            VectorRecord(concept_id=target_id, embedding=(1.0, 0.0, 0.0), metadata={"title": "Match"}),
        ]
    )

    results = await repository.similarity_search(query_embedding=(1.0, 0.0, 0.0), limit=1)

    assert results
    assert results[0].concept_id == target_id
    assert results[0].metadata["title"] == "Match"
