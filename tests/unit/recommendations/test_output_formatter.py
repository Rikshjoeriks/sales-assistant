"""Tests for output formatter service (T057)."""
from __future__ import annotations

import pytest

from src.app.recommendations.services.output_formatter import OutputFormatter


@pytest.fixture()
def formatter() -> OutputFormatter:
    return OutputFormatter()


def test_email_format_includes_salutation_and_signature(formatter: OutputFormatter) -> None:
    text = "The Camry Hybrid offers excellent fuel efficiency and safety features."
    result = formatter.format(text=text, output_format="email", audience_name="Pat")
    assert result.lower().startswith("dear pat")
    assert result.endswith("\n\nBest regards,\nYour Sales Assistant")


def test_bullet_format_adds_dashes_and_linebreaks(formatter: OutputFormatter) -> None:
    text = "Feature A\nFeature B\nFeature C"
    result = formatter.format(text=text, output_format="bullet")
    lines = result.splitlines()
    assert all(line.startswith("- ") for line in lines if line.strip())
    assert len(lines) == 3


def test_script_format_labels_speaker(formatter: OutputFormatter) -> None:
    text = "Introduce benefits. Address concerns. Ask for next steps."
    result = formatter.format(text=text, output_format="script")
    assert "Agent:" in result


def test_presentation_format_has_headings(formatter: OutputFormatter) -> None:
    text = "Fuel Efficiency\nSafety\nTotal Cost of Ownership"
    result = formatter.format(text=text, output_format="presentation")
    assert "# Recommendations" in result
    assert "- Fuel Efficiency" in result


def test_unknown_format_returns_original_text(formatter: OutputFormatter) -> None:
    text = "Plain text"
    assert formatter.format(text=text, output_format="raw") == text
