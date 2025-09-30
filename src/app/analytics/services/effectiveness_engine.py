"""Effectiveness analytics engine (skeleton for Phase 3.6)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(slots=True)
class EffectivenessEngine:
    def calculate_summary(self, feedback: Sequence[dict[str, Any]]) -> dict[str, Any]:
        """Compute aggregate effectiveness metrics from feedback records.

        Returns a dictionary with:
        - average_effectiveness (float)
        - success_rate (float) with 'interested'/'won' counted as success
        - technique_frequency (dict[str, int])
        """
        if not feedback:
            return {"average_effectiveness": 0.0, "success_rate": 0.0, "technique_frequency": {}}

        total_rating = 0.0
        rating_count = 0
        success = 0
        total = 0
        freq: dict[str, int] = {}

        for item in feedback:
            total += 1
            rating = item.get("effectiveness_rating")
            if isinstance(rating, (int, float)):
                total_rating += float(rating)
                rating_count += 1
            outcome = str(item.get("interaction_outcome", "")).lower()
            if outcome in {"interested", "won", "converted", "positive"}:
                success += 1
            for technique in item.get("techniques_that_worked", []) or []:
                freq[technique] = freq.get(technique, 0) + 1

        average = (total_rating / rating_count) if rating_count else 0.0
        success_rate = (success / total) if total else 0.0
        return {
            "average_effectiveness": round(average, 4),
            "success_rate": round(success_rate, 4),
            "technique_frequency": dict(sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))),
        }

    def calculate_trends(self, feedback: Sequence[dict[str, Any]], *, window: int = 30) -> dict[str, Any]:
        """Return trend statistics over a time window.

        Minimal implementation: returns window and counts; callers can extend later.
        """
        return {
            "window_days": int(window),
            "count": int(len(feedback or [])),
        }


__all__ = ["EffectivenessEngine"]
