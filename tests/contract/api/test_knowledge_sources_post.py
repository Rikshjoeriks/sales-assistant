"""Contract test for uploading knowledge sources."""
from __future__ import annotations

from io import BytesIO

import pytest


@pytest.mark.asyncio
async def test_upload_knowledge_source_contract(async_client) -> None:
    files = {
        "file": ("psychology_of_selling.pdf", BytesIO(b"fake"), "application/pdf"),
    }
    data = {
        "title": "The Psychology of Selling",
        "author": "Brian Tracy",
        "type": "psychology",
        "version": "2nd Edition",
    }

    response = await async_client.post("/api/v1/knowledge/sources", files=files, data=data)

    assert response.status_code == 201
    payload = response.json()
    for key in ("id", "title", "type", "processing_status", "estimated_processing_time"):
        assert key in payload
