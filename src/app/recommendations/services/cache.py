"""Lightweight in-memory cache for recent recommendations (T060)."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CacheItem:
    value: Any
    expires_at: float


@dataclass(slots=True)
class RecommendationCache:
    ttl_seconds: int = 60
    max_items: int = 256
    _store: dict[str, CacheItem] = field(default_factory=dict)

    def _now(self) -> float:
        return time.time()

    def _evict_if_needed(self) -> None:
        if len(self._store) <= self.max_items:
            return
        # Evict oldest by expiry then arbitrary
        keys = sorted(self._store.keys(), key=lambda k: self._store[k].expires_at)
        for k in keys[: max(1, len(keys) - self.max_items)]:
            self._store.pop(k, None)

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        if item.expires_at < self._now():
            self._store.pop(key, None)
            return None
        return item.value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = CacheItem(value=value, expires_at=self._now() + self.ttl_seconds)
        self._evict_if_needed()


__all__ = ["RecommendationCache"]
