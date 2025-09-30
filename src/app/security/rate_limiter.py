"""Simple in-memory rate limiter (dev/demo) with feature flag (T074)."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import DefaultDict
from collections import defaultdict

from fastapi import Header, HTTPException, status

from src.app.core.config import settings


@dataclass(slots=True)
class _Bucket:
    reset_at: float
    count: int = 0


@dataclass(slots=True)
class RateLimiter:
    window_seconds: int = settings.rate_limit_window_seconds
    max_requests: int = settings.rate_limit_max_requests
    _buckets: DefaultDict[str, _Bucket] = field(default_factory=lambda: defaultdict(lambda: _Bucket(reset_at=0.0)))

    def check(self, key: str) -> None:
        now = time.time()
        bucket = self._buckets[key]
        if bucket.reset_at <= now:
            bucket.reset_at = now + self.window_seconds
            bucket.count = 0
        bucket.count += 1
        if bucket.count > self.max_requests:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate_limited")


limiter = RateLimiter()


def rate_limit(x_forwarded_for: str | None = Header(default=None)) -> bool:
    if not settings.feature_flags.rate_limiting_enabled:  # no-op unless enabled
        return True
    key = (x_forwarded_for or "127.0.0.1").split(",", 1)[0].strip()
    limiter.check(key)
    return True


__all__ = ["rate_limit"]
