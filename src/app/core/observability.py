"""Observability primitives (logging, request IDs, instrumentation)."""
from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import Awaitable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.app.core.config import settings
from src.app.core.logging import bind_request_context, configure_logging


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach correlation IDs and timing information to each request."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start_time = time.perf_counter()

        bind_request_context(request_id=request_id)

        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["x-request-id"] = request_id
        response.headers["x-response-time-ms"] = f"{duration_ms:.2f}"
        return response


def configure_observability(app: FastAPI) -> None:
    """Initialize logging, CORS, and request context middleware."""
    configure_logging("sales-assistant-api")

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def _startup_event() -> None:  # pragma: no cover - side-effect configuration
        bind_request_context()
