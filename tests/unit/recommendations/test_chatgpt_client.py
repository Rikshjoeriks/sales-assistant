"""Tests for ChatGPT client wrapper with retry/backoff (T053)."""
from __future__ import annotations

import asyncio
import types

import pytest

from src.app.recommendations.clients.chatgpt_client import ChatGPTClient


class RateLimitError(Exception):
    pass


class ServiceError(Exception):
    pass


class _DummyCompletions:
    def __init__(self, responses: list[tuple[str, str | Exception]]):
        # Each item: (kind, value) where kind in {"ok", "error"}
        self._responses = responses
        self.calls = 0

    async def create(self, **kwargs):  # type: ignore[no-untyped-def]
        self.calls += 1
        kind, value = self._responses.pop(0)
        await asyncio.sleep(0)  # yield control to simulate async
        if kind == "error":
            raise value  # type: ignore[misc]
        # Return a minimal shape similar to OpenAI chat completion
        class _Message:
            def __init__(self, content: str) -> None:
                self.content = content

        class _Choice:
            def __init__(self, content: str) -> None:
                self.message = _Message(content)

        class _Resp:
            def __init__(self, content: str) -> None:
                self.choices = [_Choice(content)]
                self.model = kwargs.get("model", "test-model")

        return _Resp(value)  # type: ignore[arg-type]


class _DummyChat:
    def __init__(self, completions: _DummyCompletions):
        self.completions = completions


class _DummyClient:
    def __init__(self, completions: _DummyCompletions):
        self.chat = _DummyChat(completions)


@pytest.mark.anyio
async def test_retries_on_rate_limit_then_succeeds():
    comps = _DummyCompletions(
        [
            ("error", RateLimitError("rate limit")),
            ("error", ServiceError("server error")),
            ("ok", "hello world"),
        ]
    )
    client = ChatGPTClient(client=_DummyClient(comps), model="gpt-test", max_retries=5, base_delay=0.0, max_delay=0.0)
    result = await client.chat(messages=[{"role": "user", "content": "hi"}], temperature=0.3)

    assert result == "hello world"
    assert comps.calls == 3


@pytest.mark.anyio
async def test_gives_up_after_max_retries():
    comps = _DummyCompletions(
        [("error", RateLimitError("rate limit")) for _ in range(4)]
    )
    client = ChatGPTClient(client=_DummyClient(comps), model="gpt-test", max_retries=3, base_delay=0.0, max_delay=0.0)

    with pytest.raises(RateLimitError):
        await client.chat(messages=[{"role": "user", "content": "hi"}], temperature=0.7)


@pytest.mark.anyio
async def test_passes_messages_and_temperature():
    recorded: dict = {}

    class _SpyCompletions(_DummyCompletions):
        async def create(self, **kwargs):  # type: ignore[no-untyped-def]
            recorded.update(kwargs)
            return await super().create(**kwargs)

    comps = _SpyCompletions([("ok", "ack")])
    client = ChatGPTClient(client=_DummyClient(comps), model="gpt-test", max_retries=1, base_delay=0.0, max_delay=0.0)
    await client.chat(messages=[{"role": "user", "content": "x"}], temperature=0.42)

    assert recorded["messages"][0]["content"] == "x"
    assert recorded["temperature"] == 0.42
