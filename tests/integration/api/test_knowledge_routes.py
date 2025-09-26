"""Integration coverage for knowledge ingestion endpoints."""
from __future__ import annotations

import json

import pytest


async def _upload_sample(async_client) -> dict[str, str]:
    payload = {
        "title": (None, "Sample Psychology Note"),
        "type": (None, "psychology"),
        "author": (None, "Test Author"),
        "version": (None, "1.0"),
        "metadata": (None, json.dumps({"tags": ["demo"]})),
    }
    files = {
        "file": ("sample.txt", b"Social proof builds trust and reduces objections.", "text/plain"),
    }
    response = await async_client.post("/api/v1/knowledge/sources", data=payload, files=files)
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_upload_and_list_sources(async_client) -> None:
    created = await _upload_sample(async_client)

    assert created["processing_status"] == "processed"
    assert created["title"] == "Sample Psychology Note"

    list_response = await async_client.get("/api/v1/knowledge/sources")
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total_count"] == 1
    assert body["sources"][0]["title"] == "Sample Psychology Note"


@pytest.mark.asyncio
async def test_semantic_search_returns_results(async_client) -> None:
    await _upload_sample(async_client)

    search_payload = {
        "query": "How can I build trust with hesitant buyers?",
        "limit": 3,
        "similarity_threshold": 0.1,
    }
    response = await async_client.post("/api/v1/knowledge/search", json=search_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["total_results"] >= 1
    first_result = body["results"][0]
    assert first_result["source"]["title"] == "Sample Psychology Note"
