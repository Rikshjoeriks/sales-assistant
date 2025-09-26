"""Dependency helpers for knowledge components."""
from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.app.core.db import SessionLocal
from src.app.knowledge.repositories.source_repository import KnowledgeSourceRepository
from src.app.knowledge.repositories.vector_repository import VectorRepository
from src.app.knowledge.services.chunker import TextChunker
from src.app.knowledge.services.concept_extractor import ConceptExtractor
from src.app.knowledge.services.embedding_service import EmbeddingService
from src.app.knowledge.services.ingestion_service import IngestionService
from src.app.knowledge.services.metrics import KnowledgeMetrics
from src.app.knowledge.services.orchestrator import KnowledgeIngestionOrchestrator


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


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


def get_source_repository(session: Session = Depends(get_session)) -> KnowledgeSourceRepository:
    return KnowledgeSourceRepository(session=session)


def get_vector_repository(session: Session = Depends(get_session)) -> VectorRepository:
    return VectorRepository(session=session)


def build_orchestrator(*, session: Session) -> KnowledgeIngestionOrchestrator:
    return KnowledgeIngestionOrchestrator(
        ingestion_service=get_ingestion_service(),
        chunker=get_chunker(),
        concept_extractor=get_concept_extractor(),
        embedding_service=get_embedding_service(),
        source_repository=KnowledgeSourceRepository(session=session),
        vector_repository=VectorRepository(session=session),
        metrics=get_metrics(),
    )


def get_orchestrator(session: Session = Depends(get_session)) -> Generator[KnowledgeIngestionOrchestrator, None, None]:
    orchestrator = build_orchestrator(session=session)
    try:
        yield orchestrator
        session.commit()
    except Exception:
        session.rollback()
        raise


@contextmanager
def orchestrator_session(session: Session | None = None) -> Generator[KnowledgeIngestionOrchestrator, None, None]:
    own_session = session is None
    if session is None:
        session = SessionLocal()
    current_session: Session = session
    try:
        orchestrator = build_orchestrator(session=current_session)
        yield orchestrator
        current_session.commit()
    except Exception:
        current_session.rollback()
        raise
    finally:
        if own_session:
            current_session.close()


__all__ = [
    "build_orchestrator",
    "get_orchestrator",
    "get_session",
    "get_source_repository",
    "get_vector_repository",
    "orchestrator_session",
]
