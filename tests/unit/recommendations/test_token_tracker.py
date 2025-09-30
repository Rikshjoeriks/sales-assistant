from __future__ import annotations

from src.app.recommendations.services.token_tracker import TokenTracker


def test_token_tracker_estimates_tokens_and_cost():
    tracker = TokenTracker(prompt_cost_per_1k=0.004, completion_cost_per_1k=0.012)
    text = "Hello world. This is a test message for counting tokens."
    est = tracker.estimate_tokens(prompt_text=text, completion_text="response text")
    assert est["prompt_tokens"] > 0
    assert est["completion_tokens"] > 0
    total = est["total_tokens"]
    assert total == est["prompt_tokens"] + est["completion_tokens"]

    cost = tracker.estimate_cost(prompt_tokens=est["prompt_tokens"], completion_tokens=est["completion_tokens"])
    assert cost > 0.0