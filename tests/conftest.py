"""Project-wide pytest fixtures for Sales Assistant."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Return an HTTPX async client bound to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture()
def db_session() -> MagicMock:
    """Provide a mocked database session for service tests."""
    session = MagicMock(name="db_session")
    session.commit.side_effect = RuntimeError("Database commit not configured for tests yet")
    session.rollback.side_effect = RuntimeError("Database rollback not configured for tests yet")
    return session


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
