"""Analyse decision factors and objections for customer profiles."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Iterable, Sequence


@dataclass(slots=True)
class DecisionInsight:
    primary_factors: list[str]
    secondary_factors: list[str]
    deal_breakers: list[str]
    objection_themes: list[str]
    urgency_level: str
    follow_up_required: bool
    success_indicators: list[str]


class DecisionService:
    """Summarises drivers, objections, and urgency for a customer profile."""

    def evaluate(self, profile: dict[str, Any], interactions: Sequence[dict[str, Any]] | None = None) -> DecisionInsight:
        decision_factors = profile.get("decision_factors") or {}
        primary = list(decision_factors.get("primary", []))
        secondary = list(decision_factors.get("secondary", []))
        deal_breakers = list(decision_factors.get("deal_breakers", []))
        interactions = list(interactions or [])

        objection_themes = self._collect_objections(interactions)
        urgency_level = self._infer_urgency(profile, interactions)
        follow_up_required = any(self._requires_follow_up(interaction) for interaction in interactions)
        success_indicators = self._success_indicators(interactions)

        return DecisionInsight(
            primary_factors=primary,
            secondary_factors=secondary,
            deal_breakers=deal_breakers,
            objection_themes=sorted(set(objection_themes)),
            urgency_level=urgency_level,
            follow_up_required=follow_up_required,
            success_indicators=success_indicators,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _collect_objections(self, interactions: Iterable[dict[str, Any]]) -> list[str]:
        themes: list[str] = []
        for interaction in interactions:
            feedback = interaction.get("customer_feedback") or {}
            for concern in feedback.get("primary_concerns", []) or []:
                themes.append(concern)
        return themes

    def _requires_follow_up(self, interaction: dict[str, Any]) -> bool:
        follow_up = interaction.get("follow_up") or {}
        return bool(follow_up.get("required"))

    def _success_indicators(self, interactions: Iterable[dict[str, Any]]) -> list[str]:
        indicators: list[str] = []
        for interaction in interactions:
            feedback = interaction.get("customer_feedback") or {}
            for response in feedback.get("positive_responses", []) or []:
                indicators.append(f"positive_response:{response}")
        return indicators

    def _infer_urgency(
        self,
        profile: dict[str, Any],
        interactions: Sequence[dict[str, Any]],
    ) -> str:
        buying_context = profile.get("buying_context") or {}
        timeline = (buying_context.get("timeline") or "").lower()
        if "weeks" in timeline or "within_1" in timeline:
            return "high"
        if "months" in timeline:
            return "medium"

        follow_up_dates: list[dt.datetime] = []
        for interaction in interactions:
            follow_up = interaction.get("follow_up") or {}
            raw_date = follow_up.get("date")
            if isinstance(raw_date, dt.datetime):
                follow_up_dates.append(raw_date)
        if follow_up_dates:
            soonest = min(follow_up_dates)
            delta = soonest - dt.datetime.now(tz=dt.timezone.utc)
            if delta.days <= 7:
                return "high"
            if delta.days <= 21:
                return "medium"
        return "low"


__all__ = [
    "DecisionService",
    "DecisionInsight",
]
