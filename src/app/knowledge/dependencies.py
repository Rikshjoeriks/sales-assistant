"""Dependency helpers for knowledge components."""
from __future__ import annotations

from functools import lru_cache

from src.app.knowledge.repositories.source_repository import KnowledgeSourceRepository
from src.app.knowledge.repositories.vector_repository import VectorRepository
from src.app.knowledge.services.chunker import TextChunker
from src.app.knowledge.services.concept_extractor import ConceptExtractor
from src.app.knowledge.services.embedding_service import EmbeddingService
from src.app.knowledge.services.ingestion_service import IngestionService
from src.app.knowledge.services.metrics import KnowledgeMetrics
from src.app.knowledge.services.orchestrator import KnowledgeIngestionOrchestrator


@lru_cache(maxsize=1)
def get_source_repository() -> KnowledgeSourceRepository:
    return KnowledgeSourceRepository()


@lru_cache(maxsize=1)
def get_vector_repository() -> VectorRepository:
    return VectorRepository()


@lru_cache(maxsize=1)
def get_ingestion_service() -> IngestionService:
    return IngestionService()


@lru_cache(maxsize=1)
def get_chunker() -> TextChunker:
    return TextChunker()


@lru_cache(maxsize=1)
def get_concept_extractor() -> ConceptExtractor:
    return ConceptExtractor()


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


@lru_cache(maxsize=1)
def get_metrics() -> KnowledgeMetrics:
    return KnowledgeMetrics()


def get_orchestrator() -> KnowledgeIngestionOrchestrator:
    return KnowledgeIngestionOrchestrator(
        ingestion_service=get_ingestion_service(),
        chunker=get_chunker(),
        concept_extractor=get_concept_extractor(),
        embedding_service=get_embedding_service(),
        source_repository=get_source_repository(),
        vector_repository=get_vector_repository(),
        metrics=get_metrics(),
    )


__all__ = [
    "get_orchestrator",
    "get_source_repository",
    "get_vector_repository",
]
