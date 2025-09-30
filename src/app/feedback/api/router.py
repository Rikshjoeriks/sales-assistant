"""Feedback API router (T063): POST /api/v1/recommendations/{id}/feedback."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from src.app.security.auth import require_api_key
from src.app.security.rate_limiter import rate_limit

from src.app.core.db import SessionLocal
from src.app.feedback.repositories import FeedbackRepository
from src.app.feedback.services.service import FeedbackService, FeedbackPayload


router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["Feedback"],
    dependencies=[Depends(require_api_key), Depends(rate_limit)],
)


def get_session():  # pragma: no cover
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_service(session=Depends(get_session)):
    repo = FeedbackRepository(session=session)
    return FeedbackService(repository=repo)


@router.post("/{recommendation_id}/feedback", status_code=status.HTTP_201_CREATED)
def submit_feedback(recommendation_id: uuid.UUID, payload: FeedbackPayload, svc: FeedbackService = Depends(get_service)):
    try:
        result = svc.record(recommendation_id=recommendation_id, payload=payload)
    except Exception as ex:  # pragma: no cover - kept simple for contract tests
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))
    return {
        "feedback_id": str(result.feedback_id),
        "recommendation_id": str(result.recommendation_id),
        "recorded_at": result.recorded_at,
        "learning_impact": result.learning_impact,
    }


__all__ = ["router"]
