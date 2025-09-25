"""FastAPI router for knowledge management APIs."""
from __future__ import annotations

import json
import time
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from src.app.knowledge.dependencies import (
    get_orchestrator,
    get_source_repository,
)
from src.app.knowledge.repositories.source_repository import KnowledgeSourceRepository
from src.app.knowledge.services.ingestion_service import IngestionError
from src.app.knowledge.services.orchestrator import IngestionRequest, KnowledgeIngestionOrchestrator

from .schemas import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
    KnowledgeSearchResultSource,
    KnowledgeSourceCreatePayload,
    KnowledgeSourceListResponse,
    KnowledgeSourceResponse,
)


router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge"])


@router.post(
    "/sources",
    response_model=KnowledgeSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_knowledge_source(
    file: UploadFile = File(...),
    title: str = Form(...),
    type: str = Form(...),
    author: str | None = Form(None),
    version: str | None = Form(None),
    metadata: str | None = Form(None),
    orchestrator: KnowledgeIngestionOrchestrator = Depends(get_orchestrator),
) -> KnowledgeSourceResponse:
    try:
        payload = KnowledgeSourceCreatePayload(
            title=title,
            type=type,
            author=author,
            version=version,
            metadata=_parse_metadata(metadata),
        )
    except Exception as exc:  # pragma: no cover - defensive path
        raise HTTPException(status_code=400, detail={"error": "validation_failed", "message": str(exc)}) from exc

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail={"error": "validation_failed", "message": "File is empty"})

    try:
        source = orchestrator.ingest(
            IngestionRequest(
                filename=file.filename or payload.title,
                data=file_bytes,
                content_type=file.content_type,
                title=payload.title,
                source_type=payload.type,
                author=payload.author,
                version=payload.version,
                metadata=payload.metadata.dict() if payload.metadata else {},
            )
        )
    except IngestionError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_failed",
                "message": str(exc),
                "details": {"field": "file", "supported_formats": ["pdf", "txt", "docx"]},
            },
        ) from exc

    return KnowledgeSourceResponse.model_validate(
        {
            "source_id": source.source_id,
            "title": source.title,
            "author": source.author,
            "type": source.type,
            "version": source.version,
            "processing_status": source.processing_status,
            "created_at": source.created_at,
            "processed_at": source.processed_at,
        }
    )


@router.get("/sources", response_model=KnowledgeSourceListResponse)
async def list_sources(
    repository: KnowledgeSourceRepository = Depends(get_source_repository),
) -> KnowledgeSourceListResponse:
    sources = repository.list_sources()
    return KnowledgeSourceListResponse(
        sources=[
            KnowledgeSourceResponse(
                id=source.source_id,
                title=source.title,
                author=source.author,
                type=source.type,
                version=source.version,
                processing_status=source.processing_status,
                created_at=source.created_at,
                processed_at=source.processed_at,
            )
            for source in sources
        ],
        total_count=len(sources),
    )


@router.post("/search", response_model=KnowledgeSearchResponse)
async def semantic_search(
    payload: KnowledgeSearchRequest,
    orchestrator: KnowledgeIngestionOrchestrator = Depends(get_orchestrator),
) -> KnowledgeSearchResponse:
    start = time.perf_counter()
    results = await orchestrator.semantic_search(
        query=payload.query,
        limit=payload.limit,
        min_score=payload.similarity_threshold,
        source_types=payload.source_types,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    formatted_results = [
        KnowledgeSearchResult(
            concept_id=result.concept.concept_id,
            title=result.concept.title,
            summary=result.concept.content,
            similarity_score=round(result.score, 4),
            source=KnowledgeSearchResultSource(
                title=result.source.title,
                author=result.source.author,
                type=result.source.type,
            ),
            page_reference=result.concept.page_reference,
        )
        for result in results
    ]

    return KnowledgeSearchResponse(
        results=formatted_results,
        total_results=len(formatted_results),
        query_processing_time=f"{elapsed_ms:.2f}ms",
    )


def _parse_metadata(payload: str | None) -> Any:
    if not payload:
        return None
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive path
        raise ValueError("metadata must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("metadata must be a JSON object")
    return parsed


__all__ = ["router"]
