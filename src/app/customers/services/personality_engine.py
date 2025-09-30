"""Heuristic personality assessment utilities."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Mapping

_DISC_KEYS = ("dominant", "influential", "steady", "conscientious")


@dataclass(slots=True)
class PersonalityProfile:
    type: str
    confidence: float
    traits: Mapping[str, float]
    communication_style: str | None
    primary_trait: str


class PersonalityEngine:
    """Map conversational cues to DISC personality profiles."""

    scoring_weights: Dict[str, tuple[str, ...]] = {
        "dominant": (
            "fast",
            "performance",
            "results",
            "deadline",
            "win",
            "lead",
            "aggressive",
        ),
        "influential": (
            "team",
            "community",
            "excited",
            "share",
            "story",
            "together",
        ),
        "steady": (
            "support",
            "trust",
            "relationship",
            "comfort",
            "family",
            "stable",
            "together",
        ),
        "conscientious": (
            "data",
            "spec",
            "analysis",
            "detail",
            "evidence",
            "compare",
            "calculate",
        ),
    }

    def evaluate(self, profile_data: Mapping[str, Any]) -> PersonalityProfile:
        assessment = profile_data.get("personality_assessment", {}) or {}
        disc_type = (assessment.get("type") or "").upper() or self._infer_from_preferences(profile_data)
        disc_type = disc_type if disc_type in {"D", "I", "S", "C"} else "S"
        communication = (profile_data.get("communication_preferences") or {}).get("style")
        traits = self._base_trait_distribution(disc_type, assessment.get("confidence"))
        confidence = float(assessment.get("confidence") or 0.7)
        primary = self._disc_key(disc_type)
        return PersonalityProfile(
            type=disc_type,
            confidence=min(max(confidence, 0.0), 1.0),
            traits=traits,
            communication_style=communication,
            primary_trait=primary,
        )

    def analyze_transcript(self, transcript: str) -> PersonalityProfile:
        text = transcript.lower()
        scores: Dict[str, float] = {key: 0.0 for key in _DISC_KEYS}
        for trait, keywords in self.scoring_weights.items():
            scores[trait] = self._keyword_score(text, keywords)

        total = sum(scores.values()) or 1.0
        normalized = {trait: round(score / total, 4) for trait, score in scores.items()}
        primary_trait = max(normalized, key=lambda item: normalized[item])
        disc_type = {
            "dominant": "D",
            "influential": "I",
            "steady": "S",
            "conscientious": "C",
        }[primary_trait]
        confidence = normalized[primary_trait]
        return PersonalityProfile(
            type=disc_type,
            confidence=float(round(confidence if confidence > 0 else 0.5, 2)),
            traits=normalized,
            communication_style=self._communication_style(primary_trait),
            primary_trait=primary_trait,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _base_trait_distribution(self, disc: str, confidence: float | None) -> Mapping[str, float]:
        confidence = confidence or 0.7
        weights: Dict[str, float] = {}
        for key in _DISC_KEYS:
            weights[key] = 0.1
        primary_key = self._disc_key(disc)
        weights[primary_key] = confidence
        total = sum(weights.values())
        return {key: round(value / total, 4) for key, value in weights.items()}

    def _keyword_score(self, text: str, keywords: tuple[str, ...]) -> float:
        score = 0.0
        for keyword in keywords:
            occurrences = len(re.findall(rf"\b{re.escape(keyword)}\b", text))
            score += occurrences * 1.0
        return score

    def _communication_style(self, primary_trait: str) -> str:
        return {
            "dominant": "direct",
            "influential": "collaborative",
            "steady": "supportive",
            "conscientious": "analytical",
        }.get(primary_trait, "direct")

    def _infer_from_preferences(self, profile_data: Mapping[str, Any]) -> str:
        decision_factors = profile_data.get("decision_factors") or {}
        primary = decision_factors.get("primary", [])
        if any(factor in {"performance", "results", "speed"} for factor in primary):
            return "D"
        if any(factor in {"relationships", "referrals", "community"} for factor in primary):
            return "I"
        if any(factor in {"reliability", "comfort", "support"} for factor in primary):
            return "S"
        if any(factor in {"technology", "data", "efficiency"} for factor in primary):
            return "C"
        return "S"

    def _disc_key(self, disc: str) -> str:
        mapping = {"D": "dominant", "I": "influential", "S": "steady", "C": "conscientious"}
        return mapping.get(disc.upper(), "steady")


__all__ = [
    "PersonalityEngine",
    "PersonalityProfile",
]
