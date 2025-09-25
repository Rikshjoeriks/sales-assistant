"""In-memory repository for knowledge sources and extracted concepts."""
from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence


ProcessingStatus = str


@dataclass(slots=True)
class KnowledgeSource:
    source_id: uuid.UUID
    title: str
    author: str | None
    type: str
    version: str | None
    file_path: str
    processing_status: ProcessingStatus = "queued"
    created_at: dt.datetime = field(default_factory=lambda: dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc))
    processed_at: dt.datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class KnowledgeConcept:
    concept_id: uuid.UUID
    source_id: uuid.UUID
    title: str
    concept_type: str
    content: str
    keywords: list[str]
    page_reference: str | None
    confidence_score: float


class KnowledgeSourceRepository:
    """Persistence abstraction with safe in-memory defaults."""

    def __init__(self, *, session: Any | None = None) -> None:
        self._session = session
        self._sources: dict[uuid.UUID, KnowledgeSource] = {}
        self._concepts: dict[uuid.UUID, KnowledgeConcept] = {}

    def create_source(
        self,
        *,
        title: str,
        source_type: str,
        file_path: str,
        author: str | None = None,
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeSource:
        source_id = uuid.uuid4()
        source = KnowledgeSource(
            source_id=source_id,
            title=title,
            author=author,
            type=source_type,
            version=version,
            file_path=file_path,
            metadata=metadata or {},
        )
        self._sources[source_id] = source
        return source

    def update_processing_status(
        self,
        source_id: uuid.UUID,
        *,
        status: ProcessingStatus,
        processed_at: dt.datetime | None = None,
    ) -> KnowledgeSource:
        source = self._require_source(source_id)
        source.processing_status = status
        source.processed_at = processed_at
        return source

    def add_concepts(self, source_id: uuid.UUID, concepts: Iterable[KnowledgeConcept]) -> None:
        self._require_source(source_id)
        for concept in concepts:
            self._concepts[concept.concept_id] = concept

    def list_sources(self) -> list[KnowledgeSource]:
        return sorted(self._sources.values(), key=lambda s: s.created_at, reverse=True)

    def get_source(self, source_id: uuid.UUID) -> KnowledgeSource:
        return self._require_source(source_id)

    def concepts_for_source(self, source_id: uuid.UUID) -> list[KnowledgeConcept]:
        return [concept for concept in self._concepts.values() if concept.source_id == source_id]

    def delete_source(self, source_id: uuid.UUID) -> None:
        if source_id in self._sources:
            del self._sources[source_id]
        for concept_id, concept in list(self._concepts.items()):
            if concept.source_id == source_id:
                del self._concepts[concept_id]

    def search_concepts(self, *, concept_ids: Sequence[uuid.UUID]) -> list[KnowledgeConcept]:
        return [self._concepts[concept_id] for concept_id in concept_ids if concept_id in self._concepts]

    def concepts_with_sources(
        self,
        *,
        concept_ids: Sequence[uuid.UUID],
        source_types: Sequence[str] | None = None,
    ) -> list[tuple[KnowledgeConcept, KnowledgeSource]]:
        allowed_types = {type_name.lower() for type_name in (source_types or []) if type_name}
        results: list[tuple[KnowledgeConcept, KnowledgeSource]] = []
        for concept_id in concept_ids:
            concept = self._concepts.get(concept_id)
            if not concept:
                continue
            source = self._sources.get(concept.source_id)
            if not source:
                continue
            if allowed_types and source.type.lower() not in allowed_types:
                continue
            results.append((concept, source))
        return results

    def _require_source(self, source_id: uuid.UUID) -> KnowledgeSource:
        try:
            return self._sources[source_id]
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise KeyError(f"Knowledge source {source_id} not found") from exc


__all__ = [
    "KnowledgeSourceRepository",
    "KnowledgeSource",
    "KnowledgeConcept",
]
