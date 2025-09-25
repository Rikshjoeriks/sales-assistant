"""Integration test for the health endpoint."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_reports_ok(async_client) -> None:
    response = await async_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "sales-assistant-api"
