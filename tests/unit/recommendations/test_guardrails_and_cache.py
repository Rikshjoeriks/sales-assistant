from __future__ import annotations

import time

from src.app.recommendations.services.guardrails import Guardrails
from src.app.recommendations.services.cache import RecommendationCache


def test_guardrails_filters_basic_profanity():
    g = Guardrails()
    text = "This is damn good, what the hell"
    filtered = g.filter_text(text)
    assert "damn" not in filtered
    assert "hell" not in filtered


def test_recommendation_cache_ttl_and_eviction():
    cache = RecommendationCache(ttl_seconds=1, max_items=2)
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.get("a") == 1
    cache.set("c", 3)  # triggers eviction to respect max_items
    # Not guaranteed which one evicted, but size capped and at least one exists
    assert sum(1 for k in ("a", "b", "c") if cache.get(k) is not None) <= 2
    time.sleep(1.1)
    # Items should expire
    assert cache.get("a") is None and cache.get("b") is None and cache.get("c") is None
