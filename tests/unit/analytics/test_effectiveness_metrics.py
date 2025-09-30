"""Analytics effectiveness metrics expectations."""
from __future__ import annotations

import pytest


def test_effectiveness_engine_summary_metrics() -> None:
    from src.app.analytics.services.effectiveness_engine import EffectivenessEngine

    engine = EffectivenessEngine()
    feedback = [
        {
            "recommendation_id": "rec-123",
            "effectiveness_rating": 4,
            "interaction_outcome": "interested",
            "techniques_that_worked": ["social_proof"],
        }
    ]
    summary = engine.calculate_summary(feedback)
    assert summary["average_effectiveness"] >= 0.0
    assert summary["success_rate"] >= 0.0
    assert "technique_frequency" in summary


def test_effectiveness_engine_provides_trend_analysis() -> None:
    from src.app.analytics.services.effectiveness_engine import EffectivenessEngine

    engine = EffectivenessEngine()
    trends = engine.calculate_trends([], window=30)
    assert trends["window_days"] == 30
    assert trends["count"] == 0
