"""Token usage and cost estimation (T058)."""
from __future__ import annotations

from dataclasses import dataclass


def _approx_tokens(text: str) -> int:
    # Heuristic: ~4 chars per token. Count words as fallback if non-ASCII heavy.
    if not text:
        return 0
    length = len(text)
    # Blend char and word estimates for robustness
    return max(1, int(0.25 * length + 0.5 * len(text.split())))


@dataclass(slots=True)
class TokenTracker:
    # Default rates approximate popular models; override via constructor if needed
    prompt_cost_per_1k: float = 0.005
    completion_cost_per_1k: float = 0.015

    def estimate_tokens(self, *, prompt_text: str, completion_text: str | None = None) -> dict[str, int]:
        prompt_tokens = _approx_tokens(prompt_text)
        completion_tokens = _approx_tokens(completion_text or "")
        total = prompt_tokens + completion_tokens
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total,
        }

    def estimate_cost(self, *, prompt_tokens: int, completion_tokens: int) -> float:
        prompt_cost = (prompt_tokens / 1000.0) * self.prompt_cost_per_1k
        completion_cost = (completion_tokens / 1000.0) * self.completion_cost_per_1k
        return round(prompt_cost + completion_cost, 6)


__all__ = ["TokenTracker"]
