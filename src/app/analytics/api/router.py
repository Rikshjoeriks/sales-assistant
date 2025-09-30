"""Analytics API router for recommendations effectiveness (T064)."""
from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import APIRouter, Depends, Query
from src.app.security.auth import require_api_key
from src.app.security.rate_limiter import rate_limit

from src.app.core.db import SessionLocal
from src.app.analytics.services.effectiveness_engine import EffectivenessEngine
from src.app.feedback.repositories import FeedbackRepository


router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["Analytics"],
    dependencies=[Depends(require_api_key), Depends(rate_limit)],
)


def get_session():  # pragma: no cover
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _parse_period(period: str) -> int:
    # Very simple "Nd" parser (e.g., "30d"). Defaults to 30 if invalid.
    try:
        if period.endswith("d"):
            return max(1, int(period[:-1]))
        return max(1, int(period))
    except Exception:
        return 30


@router.get("/analytics")
def get_analytics(
    period: str = Query(default="30d"),
    group_by: str | None = Query(default=None),  # Placeholder, not implemented in this iteration
    format: str = Query(default="summary"),  # Placeholder, not implemented in this iteration
    session=Depends(get_session),
) -> dict[str, Any]:
    days = _parse_period(period)
    end = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    start = end - dt.timedelta(days=days)

    repo = FeedbackRepository(session=session)
    engine = EffectivenessEngine()

    feedback_rows = repo.list_in_period(start=start, end=end)
    # Transform to dicts as expected by EffectivenessEngine (already close to dicts)
    feedback_dicts: list[dict[str, Any]] = [
        {
            "interaction_outcome": row.interaction_outcome,
            "effectiveness_rating": row.effectiveness_rating,
            "techniques_that_worked": row.techniques_that_worked,
            "recorded_at": row.recorded_at,
        }
        for row in feedback_rows
    ]

    summary = engine.calculate_summary(feedback_dicts)
    trends = engine.calculate_trends(feedback_dicts, window=days)

    # Minimal contract-aligned shape (values are illustrative based on our minimal engine)
    return {
        "period": f"{start.date()} to {end.date()}",
        "summary": {
            "total_recommendations": len(feedback_rows),
            "average_effectiveness": summary.get("average_effectiveness", 0.0),
            "success_rate": summary.get("success_rate", 0.0),
            "most_effective_techniques": list(summary.get("technique_frequency", {}).keys()),
        },
        "by_customer_type": [],
        "knowledge_source_performance": [],
        "trends": trends,
    }


__all__ = ["router"]
