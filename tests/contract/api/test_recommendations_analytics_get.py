from __future__ import annotations

import uuid
import datetime as dt

from fastapi.testclient import TestClient

from src.app.main import app
from src.app.core.db import SessionLocal
from src.app.recommendations.models import SalesRecommendationModel
from src.app.feedback.models import RecommendationFeedbackModel


client = TestClient(app)


def test_get_analytics_summary():
    # Seed a small set of recommendation + feedback rows inside the SQLite test DB
    session = SessionLocal()
    try:
        now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
        rec_id = uuid.uuid4()
        ctx_id = uuid.uuid4()
        session.add(
            SalesRecommendationModel(
                id=rec_id,
                context_id=ctx_id,
                recommendation_text="hello",
                output_format="email",
                psychological_principles_json=[],
                technical_features_json=[],
                communication_techniques_json=[],
                metadata_json={},
                confidence_score=0.7,
                token_count=10,
            )
        )
        session.add(
            RecommendationFeedbackModel(
                recommendation_id=rec_id,
                interaction_outcome="interested",
                effectiveness_rating=4,
                techniques_that_worked=["social_proof"],
                techniques_that_failed=[],
                follow_up_scheduled=True,
                recorded_at=now,
            )
        )
        session.commit()
    finally:
        session.close()

    resp = client.get("/api/v1/recommendations/analytics?period=30d&group_by=customer_type&format=summary")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "period" in data
    assert "summary" in data
    assert "total_recommendations" in data["summary"]
    assert "average_effectiveness" in data["summary"]
    assert "success_rate" in data["summary"]
    assert isinstance(data.get("by_customer_type"), list)
    assert isinstance(data.get("knowledge_source_performance"), list)