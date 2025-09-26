"""SQLAlchemy-backed repository for knowledge sources and concepts."""
from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.knowledge.models import KnowledgeConceptModel, KnowledgeSourceModel


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
    """Persistence abstraction bridging SQLAlchemy models and domain dataclasses."""

    def __init__(self, *, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

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
        model = KnowledgeSourceModel(
            title=title,
            author=author,
            type=source_type,
            version=version,
            file_path=file_path,
        )
        model.metadata_dict = metadata or {}
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_domain_source(model)

    def update_processing_status(
        self,
        source_id: uuid.UUID,
        *,
        status: ProcessingStatus,
        processed_at: dt.datetime | None = None,
    ) -> KnowledgeSource:
        model = self._require_source_model(source_id)
        model.processing_status = status
        model.processed_at = processed_at
        self._session.commit()
        self._session.refresh(model)
        return self._to_domain_source(model)

    def update_file_path(self, source_id: uuid.UUID, *, file_path: str) -> KnowledgeSource:
        model = self._require_source_model(source_id)
        model.file_path = file_path
        self._session.commit()
        self._session.refresh(model)
        return self._to_domain_source(model)

    def add_concepts(self, source_id: uuid.UUID, concepts: Iterable[KnowledgeConcept]) -> list[KnowledgeConcept]:
        self._require_source_model(source_id)
        stored: list[KnowledgeConcept] = []
        for concept in concepts:
            model = KnowledgeConceptModel(
                id=concept.concept_id,
                source_id=source_id,
                title=concept.title,
                concept_type=concept.concept_type,
                content=concept.content,
                confidence_score=concept.confidence_score,
                page_reference=concept.page_reference,
            )
            model.keywords = concept.keywords
            self._session.merge(model)
            stored.append(concept)
        self._session.commit()
        return stored

    def list_sources(self) -> list[KnowledgeSource]:
        statement = select(KnowledgeSourceModel).order_by(KnowledgeSourceModel.created_at.desc())
        models = self._session.execute(statement).scalars().all()
        return [self._to_domain_source(model) for model in models]

    def get_source(self, source_id: uuid.UUID) -> KnowledgeSource:
        model = self._require_source_model(source_id)
        return self._to_domain_source(model)

    def concepts_for_source(self, source_id: uuid.UUID) -> list[KnowledgeConcept]:
        statement = select(KnowledgeConceptModel).where(KnowledgeConceptModel.source_id == source_id)
        models = self._session.execute(statement).scalars().all()
        return [self._to_domain_concept(model) for model in models]

    def delete_source(self, source_id: uuid.UUID) -> None:
        model = self._session.get(KnowledgeSourceModel, source_id)
        if not model:
            return
        self._session.delete(model)
        self._session.commit()

    def search_concepts(self, *, concept_ids: Sequence[uuid.UUID]) -> list[KnowledgeConcept]:
        if not concept_ids:
            return []
        statement = select(KnowledgeConceptModel).where(KnowledgeConceptModel.id.in_(concept_ids))
        models = self._session.execute(statement).scalars().all()
        return [self._to_domain_concept(model) for model in models]

    def concepts_with_sources(
        self,
        *,
        concept_ids: Sequence[uuid.UUID],
        source_types: Sequence[str] | None = None,
    ) -> list[tuple[KnowledgeConcept, KnowledgeSource]]:
        if not concept_ids:
            return []
        statement = (
            select(KnowledgeConceptModel, KnowledgeSourceModel)
            .join(KnowledgeSourceModel, KnowledgeConceptModel.source_id == KnowledgeSourceModel.id)
            .where(KnowledgeConceptModel.id.in_(concept_ids))
        )
        if source_types:
            lowered = [item.lower() for item in source_types if item]
            if lowered:
                statement = statement.where(KnowledgeSourceModel.type.in_(lowered))

        rows = self._session.execute(statement).all()
        return [
            (self._to_domain_concept(concept_model), self._to_domain_source(source_model))
            for concept_model, source_model in rows
        ]

    def _require_source_model(self, source_id: uuid.UUID) -> KnowledgeSourceModel:
        model = self._session.get(KnowledgeSourceModel, source_id)
        if not model:  # pragma: no cover - defensive guard
            raise KeyError(f"Knowledge source {source_id} not found")
        return model

    def _to_domain_source(self, model: KnowledgeSourceModel) -> KnowledgeSource:
        return KnowledgeSource(
            source_id=model.id,
            title=model.title,
            author=model.author,
            type=model.type,
            version=model.version,
            file_path=model.file_path,
            processing_status=model.processing_status,
            created_at=model.created_at,
            processed_at=model.processed_at,
            metadata=model.metadata_dict,
        )

    def _to_domain_concept(self, model: KnowledgeConceptModel) -> KnowledgeConcept:
        return KnowledgeConcept(
            concept_id=model.id,
            source_id=model.source_id,
            title=model.title,
            concept_type=model.concept_type,
            content=model.content,
            keywords=model.keywords,
            page_reference=model.page_reference,
            confidence_score=model.confidence_score,
        )


__all__ = [
    "KnowledgeSourceRepository",
    "KnowledgeSource",
    "KnowledgeConcept",
]
