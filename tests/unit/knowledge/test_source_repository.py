"""Persistence expectations for the knowledge source repository."""
from __future__ import annotations

import datetime as dt
from uuid import uuid4

from src.app.knowledge.repositories.source_repository import (
    KnowledgeConcept,
    KnowledgeSourceRepository,
)


def test_create_source_persists_and_returns_domain(db_session) -> None:
    repository = KnowledgeSourceRepository(session=db_session)

    created = repository.create_source(
        title="Test Source",
        source_type="psychology",
        file_path="/tmp/test.txt",
        author="Author",
        version="1.0",
        metadata={"topic": "testing"},
    )

    fetched = repository.get_source(created.source_id)

    assert fetched.title == "Test Source"
    assert fetched.metadata["topic"] == "testing"
    assert fetched.processing_status == "queued"


def test_add_concepts_and_query(db_session) -> None:
    repository = KnowledgeSourceRepository(session=db_session)
    source = repository.create_source(
        title="Concept Source",
        source_type="technical",
        file_path="/tmp/concept.txt",
    )

    concept = KnowledgeConcept(
        concept_id=uuid4(),
        source_id=source.source_id,
        title="Hybrid Engine",
        concept_type="technical",
        content="Hybrid systems blend combustion and electric power.",
        keywords=["hybrid", "engine", "electric"],
        page_reference="p.5",
        confidence_score=0.9,
    )

    repository.add_concepts(source.source_id, [concept])
    repository.update_processing_status(
        source.source_id,
        status="processed",
        processed_at=dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc),
    )

    concepts = repository.concepts_for_source(source.source_id)
    assert len(concepts) == 1
    assert concepts[0].title == "Hybrid Engine"

    pairs = repository.concepts_with_sources(concept_ids=[concept.concept_id])
    assert len(pairs) == 1
    stored_concept, stored_source = pairs[0]
    assert stored_concept.concept_id == concept.concept_id
    assert stored_source.title == source.title
