from __future__ import annotations

import uuid

from src.app.core.db import SessionLocal
from src.app.feedback.repositories import FeedbackRepository
from src.app.recommendations.models import SalesRecommendationModel


def test_create_and_list_feedback(monkeypatch):
    session = SessionLocal()
    try:
        # Create a dummy recommendation to satisfy FK
        rec_id = uuid.uuid4()
        ctx_id = uuid.uuid4()
        session.add(
            SalesRecommendationModel(
                id=rec_id,
                context_id=ctx_id,
                recommendation_text="text",
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

        repo = FeedbackRepository(session=session)
        payload = {
            "interaction_outcome": "interested",
            "effectiveness_rating": 4,
            "techniques_that_worked": ["social_proof"],
            "techniques_that_failed": [],
            "follow_up_scheduled": True,
        }
        created = repo.create(recommendation_id=rec_id, payload=payload)
        assert created.recommendation_id == rec_id
        assert created.interaction_outcome == "interested"
        assert created.effectiveness_rating == 4
        assert created.follow_up_scheduled is True

        results = repo.list_for_recommendations([rec_id])
        assert len(results) >= 1
        assert any(r.feedback_id == created.feedback_id for r in results)
    finally:
        session.close()
