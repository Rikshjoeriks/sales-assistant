from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from src.app.main import app
from src.app.core.db import SessionLocal
from src.app.recommendations.models import SalesRecommendationModel


client = TestClient(app)


def test_post_feedback_happy_path():
    session = SessionLocal()
    try:
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
                confidence_score=0.5,
                token_count=1,
            )
        )
        session.commit()
    finally:
        session.close()

    payload = {
        "interaction_outcome": "interested",
        "customer_response": "Liked the details",
        "salesperson_notes": "Great call",
        "effectiveness_rating": 5,
        "techniques_that_worked": ["social_proof"],
        "techniques_that_failed": [],
        "follow_up_scheduled": True,
        "additional_notes": "Schedule test drive",
    }

    resp = client.post(f"/api/v1/recommendations/{rec_id}/feedback", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["recommendation_id"] == str(rec_id)
    assert data["feedback_id"]
    assert "recorded_at" in data
    assert "learning_impact" in data
