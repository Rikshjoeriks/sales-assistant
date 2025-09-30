"""Expectations for the vector repository interface."""
from __future__ import annotations

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_vector_repository_similarity_search_in_memory() -> None:
    from src.app.knowledge.repositories.vector_repository import (
        VectorRecord,
        VectorRepository,
    )

    repository = VectorRepository(session=None)

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


@pytest.mark.asyncio
async def test_vector_repository_persists_vectors(db_session) -> None:
    from src.app.knowledge.repositories.vector_repository import (
        VectorRecord,
        VectorRepository,
    )

    repository = VectorRepository(session=db_session)
    concept_id = uuid4()
    repository.upsert([VectorRecord(concept_id=concept_id, embedding=(0.3, 0.4, 0.5))])

    db_session.expunge_all()

    # New repository instance loads rows from the database
    fresh_repository = VectorRepository(session=db_session)
    results = await fresh_repository.similarity_search(query_embedding=(0.3, 0.4, 0.5), limit=1)

    assert results
    assert results[0].concept_id == concept_id
