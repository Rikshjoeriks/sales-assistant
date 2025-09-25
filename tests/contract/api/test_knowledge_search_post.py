"""Contract test for semantic knowledge search."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_knowledge_search_contract(async_client) -> None:
    payload = {
        "query": "handling price objections in car sales",
        "source_types": ["psychology", "communication"],
        "limit": 5,
        "similarity_threshold": 0.7,
    }

    response = await async_client.post("/api/v1/knowledge/search", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert isinstance(body["results"], list)
    assert "query_processing_time" in body
