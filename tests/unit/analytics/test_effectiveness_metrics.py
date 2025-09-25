"""Analytics effectiveness metrics expectations."""
from __future__ import annotations

import pytest


def test_effectiveness_engine_requires_feedback_payload() -> None:
    from src.app.analytics.services.effectiveness_engine import EffectivenessEngine  # noqa: WPS433

    engine = EffectivenessEngine()
    feedback = [
        {
            "recommendation_id": "rec-123",
            "effectiveness_rating": 4,
            "interaction_outcome": "interested",
            "techniques_that_worked": ["social_proof"],
        }
    ]

    with pytest.raises(NotImplementedError):
        engine.calculate_summary(feedback)


def test_effectiveness_engine_provides_trend_analysis() -> None:
    from src.app.analytics.services.effectiveness_engine import EffectivenessEngine  # noqa: WPS433

    engine = EffectivenessEngine()

    with pytest.raises(NotImplementedError):
        engine.calculate_trends([], window=30)
