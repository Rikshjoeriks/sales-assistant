"""Co-ordinates knowledge ingestion pipeline steps."""
from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Iterable, Sequence

from src.app.knowledge.repositories.source_repository import (
    KnowledgeConcept,
    KnowledgeSource,
    KnowledgeSourceRepository,
)
from src.app.knowledge.repositories.vector_repository import VectorRecord, VectorRepository

from .chunker import TextChunker
from .concept_extractor import ConceptExtractor
from .embedding_service import EmbeddingService
from .ingestion_service import IngestionService, IngestedDocument
from .metrics import KnowledgeMetrics


@dataclass(slots=True)
class IngestionRequest:
    filename: str
    data: bytes
    content_type: str | None
    title: str
    source_type: str
    author: str | None
    version: str | None
    metadata: dict[str, str | int | float | bool | None]


@dataclass(slots=True)
class SearchResult:
    concept: KnowledgeConcept
    source: KnowledgeSource
    score: float


class KnowledgeIngestionOrchestrator:
    """Run the ingestion pipeline synchronously for now."""

    def __init__(
        self,
        *,
        ingestion_service: IngestionService,
        chunker: TextChunker,
        concept_extractor: ConceptExtractor,
        embedding_service: EmbeddingService,
        source_repository: KnowledgeSourceRepository,
        vector_repository: VectorRepository,
        metrics: KnowledgeMetrics,
    ) -> None:
        self._ingestion_service = ingestion_service
        self._chunker = chunker
        self._concept_extractor = concept_extractor
        self._embedding_service = embedding_service
        self._source_repository = source_repository
        self._vector_repository = vector_repository
        self._metrics = metrics

    def ingest(self, request: IngestionRequest) -> KnowledgeSource:
        source = self._source_repository.create_source(
            title=request.title,
            source_type=request.source_type,
            author=request.author,
            version=request.version,
            file_path="",  # placeholder until ingestion completes
            metadata=request.metadata,
        )

        with self._metrics.track_duration() as duration_timer:
            try:
                self._source_repository.update_processing_status(source.source_id, status="processing")

                document = self._ingestion_service.ingest_bytes(
                    filename=request.filename,
                    data=request.data,
                    content_type=request.content_type,
                    metadata=request.metadata,
                )

                processed_source = self._process_document(source, document)
                elapsed = duration_timer()
                processed_source.file_path = str(document.stored_path)
                processed_source.processing_status = "processed"
                processed_source.processed_at = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
                self._metrics.record_ingestion_success(
                    source_id=str(source.source_id),
                    duration_ms=elapsed,
                    concept_count=len(self._source_repository.concepts_for_source(source.source_id)),
                )
                return processed_source
            except Exception as exc:  # pragma: no cover - defensive logging
                self._source_repository.update_processing_status(
                    source.source_id,
                    status="failed",
                    processed_at=dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc),
                )
                self._metrics.record_ingestion_failure(source_id=str(source.source_id), error=exc)
                raise

    def _process_document(self, source: KnowledgeSource, document: IngestedDocument) -> KnowledgeSource:
        chunks = self._chunker.chunk(document.content)
        concepts = self._concept_extractor.extract(chunks)

        knowledge_concepts = [
            KnowledgeConcept(
                concept_id=concept.concept_id,
                source_id=source.source_id,
                title=concept.title,
                concept_type=concept.concept_type,
                content=concept.summary,
                keywords=concept.keywords,
                page_reference=None,
                confidence_score=concept.confidence_score,
            )
            for concept in concepts
        ]

        self._source_repository.add_concepts(source.source_id, knowledge_concepts)

        embeddings = self._embedding_service.embed([concept.summary for concept in concepts])
        vector_records = [
            VectorRecord(
                concept_id=concept.concept_id,
                embedding=tuple(embedding.vector),
                metadata={
                    "source_id": str(source.source_id),
                    "title": concept.title,
                    "concept_type": concept.concept_type,
                },
            )
            for concept, embedding in zip(concepts, embeddings)
        ]
        self._vector_repository.upsert(vector_records)
        return source

    async def semantic_search(
        self,
        *,
        query: str,
        limit: int,
        min_score: float,
        source_types: Sequence[str] | None = None,
    ) -> list[SearchResult]:
        with self._metrics.track_duration() as duration_timer:
            embedding = self._embedding_service.embed([query])
            if not embedding:
                return []

            search_results = await self._vector_repository.similarity_search(
                query_embedding=embedding[0].vector,
                limit=limit,
                min_score=min_score,
            )
            paired_concepts = self._source_repository.concepts_with_sources(
                concept_ids=[result.concept_id for result in search_results],
                source_types=source_types,
            )
            elapsed = duration_timer()
            self._metrics.record_search(query=query, result_count=len(paired_concepts), duration_ms=elapsed)

            score_lookup = {result.concept_id: result.score for result in search_results}
            results: list[SearchResult] = []
            for concept, source in paired_concepts:
                score = score_lookup.get(concept.concept_id)
                if score is None:
                    continue
                results.append(SearchResult(concept=concept, source=source, score=score))
            return results


__all__ = [
    "KnowledgeIngestionOrchestrator",
    "IngestionRequest",
    "SearchResult",
]
