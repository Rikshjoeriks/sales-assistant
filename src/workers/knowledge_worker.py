"""Celery worker to process knowledge ingestion asynchronously."""
from __future__ import annotations

import base64
import json

from celery import Celery

from src.app.core.config import settings
from src.app.knowledge.dependencies import get_orchestrator
from src.app.knowledge.services.orchestrator import IngestionRequest


celery_app = Celery("knowledge_worker")
celery_app.conf.broker_url = settings.redis_url
celery_app.conf.result_backend = settings.redis_url


@celery_app.task(name="knowledge.ingest")
def ingest_task(payload: dict[str, str]) -> str:
    orchestrator = get_orchestrator()
    request = IngestionRequest(
        filename=payload["filename"],
        data=base64.b64decode(payload["data"]),
        content_type=payload.get("content_type"),
        title=payload["title"],
        source_type=payload["source_type"],
        author=payload.get("author"),
        version=payload.get("version"),
        metadata=json.loads(payload.get("metadata", "{}")),
    )
    source = orchestrator.ingest(request)
    return str(source.source_id)


__all__ = ["celery_app", "ingest_task"]
