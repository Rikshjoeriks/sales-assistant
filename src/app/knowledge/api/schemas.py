"""Pydantic schemas for knowledge API endpoints."""
from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from pydantic import BaseModel, Field


class KnowledgeSourceResponse(BaseModel):
    id: uuid.UUID = Field(validation_alias="source_id")
    title: str
    author: str | None = None
    type: str = Field(pattern=r"^(psychology|technical|communication)$")
    version: str | None = None
    processing_status: str
    created_at: dt.datetime
    processed_at: dt.datetime | None = None
    estimated_processing_time: str | None = Field(default="5-10 minutes")


class KnowledgeSourceListResponse(BaseModel):
    sources: list[KnowledgeSourceResponse]
    total_count: int


class KnowledgeSearchRequest(BaseModel):
    query: str
    source_types: list[str] = Field(default_factory=list)
    limit: int = 5
    similarity_threshold: float = Field(default=0.6, ge=0.0, le=1.0)


class KnowledgeSearchResultSource(BaseModel):
    title: str
    author: str | None = None
    type: str


class KnowledgeSearchResult(BaseModel):
    concept_id: uuid.UUID
    title: str
    content: str = Field(alias="summary")
    source: KnowledgeSearchResultSource
    similarity_score: float
    page_reference: str | None = None


class KnowledgeSearchResponse(BaseModel):
    results: list[KnowledgeSearchResult]
    query_processing_time: str
    total_results: int


class KnowledgeSourceMetadata(BaseModel):
    publication_year: int | None = None
    page_count: int | None = None
    language: str | None = None


class KnowledgeSourceCreatePayload(BaseModel):
    title: str
    author: str | None = None
    type: str = Field(pattern=r"^(psychology|technical|communication)$")
    version: str | None = None
    metadata: KnowledgeSourceMetadata | None = None
