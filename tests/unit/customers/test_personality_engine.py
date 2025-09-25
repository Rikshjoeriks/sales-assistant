"""Personality engine contract tests."""
from __future__ import annotations

import pytest


def test_personality_engine_provides_evaluate_method(sample_customer_profile) -> None:
    from src.app.customers.services.personality_engine import PersonalityEngine  # noqa: WPS433

    engine = PersonalityEngine()

    for trait in ("dominant", "influential", "steady", "conscientious"):
        assert trait in engine.scoring_weights

    with pytest.raises(NotImplementedError):
        engine.evaluate(sample_customer_profile)


@pytest.mark.parametrize(
    "transcript, expected_profile",
    [
        ("I need the fastest acceleration and performance", "D"),
        ("Let's bring the whole family to test drive", "S"),
    ],
)
def test_personality_engine_returns_disc_code(transcript: str, expected_profile: str) -> None:
    from src.app.customers.services.personality_engine import PersonalityEngine  # noqa: WPS433

    engine = PersonalityEngine()

    with pytest.raises(NotImplementedError):
        engine.analyze_transcript(transcript)
