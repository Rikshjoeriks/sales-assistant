"""Project-wide pytest fixtures for Sales Assistant."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from src.app.core.db import Base, SessionLocal
from src.app.main import app
from src.app.knowledge.services.embedding_service import EmbeddingResult, EmbeddingService


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine() -> Generator[Any, None, None]:
    original_bind = SessionLocal.kw.get("bind")
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if original_bind is not None:
        SessionLocal.configure(bind=original_bind)
    else:
        SessionLocal.configure(bind=None)


@pytest.fixture()
def reset_db(engine: Any) -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
async def async_client(reset_db: None) -> AsyncGenerator[AsyncClient, None]:
    """Return an HTTPX async client bound to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture()
def db_session(reset_db: None) -> Generator[Any, None, None]:
    """Provide a real SQLAlchemy session for service tests."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


@pytest.fixture(autouse=True)
def force_embedding_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure embeddings rely on deterministic fallback during tests."""

    def _embed(self: EmbeddingService, texts: Any) -> list[EmbeddingResult]:
        results: list[EmbeddingResult] = []
        for text in texts:
            vector = self._fallback_embedding(str(text)).astype("float32").tolist()
            results.append(EmbeddingResult(text=str(text), vector=vector))
        return results

    monkeypatch.setattr(EmbeddingService, "embed", _embed, raising=False)


@pytest.fixture()
def openai_client() -> MagicMock:
    """Provide a mocked OpenAI client with configurable responses."""
    client = MagicMock(name="openai_client")
    client.chat.completions.create.side_effect = RuntimeError("OpenAI client not stubbed")
    return client


@pytest.fixture()
def sample_customer_profile() -> dict[str, Any]:
    """Seed data used across recommendation tests."""
    return {
        "id": "customer-uuid-123",
        "personality_type": "D",
        "communication_style": "direct",
        "decision_factors": ["performance", "safety", "value"],
        "budget_range": "40k_60k",
    }
