"""API key authentication dependency (T068)."""
from __future__ import annotations

from fastapi import Header, HTTPException, status

from src.app.core.config import settings


def require_api_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> bool:
    """Enforce API key if feature flag enabled; otherwise no-op.

    Accepts either Authorization: Bearer <key> or X-API-Key: <key>.
    """
    if not getattr(settings.feature_flags, "enforce_api_key", False):
        return True

    provided: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        provided = authorization.split(" ", 1)[1].strip()
    elif x_api_key:
        provided = x_api_key.strip()

    if not provided or provided != settings.api_key_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_api_key")
    return True


__all__ = ["require_api_key"]
