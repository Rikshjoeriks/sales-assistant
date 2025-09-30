"""Personality engine behavioural tests."""
from __future__ import annotations

import pytest


def test_personality_engine_exposes_trait_weights() -> None:
    from src.app.customers.services.personality_engine import PersonalityEngine

    engine = PersonalityEngine()

    assert set(engine.scoring_weights) == {"dominant", "influential", "steady", "conscientious"}


def test_personality_engine_evaluates_profile(sample_customer_profile) -> None:
    from src.app.customers.services.personality_engine import PersonalityEngine

    engine = PersonalityEngine()

    profile_data = {
        "name": "Test Customer",
        "personality_assessment": {"type": "D", "confidence": 0.82, "assessment_method": "survey"},
        "communication_preferences": {"style": "direct"},
        "decision_factors": {"primary": ["performance", "safety"]},
    }

    result = engine.evaluate(profile_data)

    assert result.type == "D"
    assert result.communication_style == "direct"
    assert pytest.approx(result.confidence, rel=0.01) == 0.82
    assert set(result.traits) == {"dominant", "influential", "steady", "conscientious"}
    assert result.traits["dominant"] > result.traits["steady"]


@pytest.mark.parametrize(
    "transcript, expected_profile",
    [
        ("I need the fastest acceleration and performance", "D"),
        ("Let's bring the whole family to test drive", "S"),
        ("I want to tell our community about this sustainability story", "I"),
        ("I would like to review the specifications and data", "C"),
    ],
)
def test_personality_engine_classifies_transcripts(transcript: str, expected_profile: str) -> None:
    from src.app.customers.services.personality_engine import PersonalityEngine

    engine = PersonalityEngine()

    result = engine.analyze_transcript(transcript)

    assert result.type == expected_profile
    assert 0.0 < result.confidence <= 1.0
    assert result.traits[result.primary_trait] == max(result.traits.values())
