"""Metrics helpers for knowledge ingestion and search."""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Callable, Iterator

import structlog

logger = structlog.get_logger(__name__)


class KnowledgeMetrics:
    """Lightweight wrapper over structlog for consistent observability."""

    def record_ingestion_success(self, *, source_id: str, duration_ms: float, concept_count: int) -> None:
        logger.info(
            "knowledge.ingestion.success",
            source_id=source_id,
            duration_ms=round(duration_ms, 2),
            concept_count=concept_count,
        )

    def record_ingestion_failure(self, *, source_id: str, error: Exception) -> None:
        logger.error("knowledge.ingestion.failure", source_id=source_id, error=str(error))

    def record_search(self, *, query: str, result_count: int, duration_ms: float) -> None:
        logger.info(
            "knowledge.search.completed",
            query=query,
            result_count=result_count,
            duration_ms=round(duration_ms, 2),
        )

    @contextmanager
    def track_duration(self) -> Iterator[Callable[[], float]]:
        start = time.perf_counter()

        def end() -> float:
            return (time.perf_counter() - start) * 1000

        yield end


__all__ = ["KnowledgeMetrics"]
