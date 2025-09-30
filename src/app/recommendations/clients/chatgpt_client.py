"""ChatGPT client wrapper with retry/backoff (T053)."""
from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(slots=True)
class ChatGPTClient:
    """Thin async wrapper around an OpenAI-like client.

    Parameters:
    - client: An object exposing `.chat.completions.create(**kwargs)` coroutine
    - model: model name to use for chat completions
    - max_retries: maximum retry attempts on transient errors
    - base_delay: base backoff delay in seconds
    - max_delay: cap for exponential backoff
    """

    client: Any
    model: str
    max_retries: int = 3
    base_delay: float = 0.25
    max_delay: float = 4.0

    async def chat(
        self,
        *,
        messages: Sequence[Mapping[str, Any]],
        temperature: float = 0.2,
        timeout: float | None = None,
    ) -> str:
        attempt = 0
        delay = self.base_delay
        while True:
            try:
                # Note: no network call here; we call the provided client's async API
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=list(messages),
                    temperature=temperature,
                    timeout=timeout,
                )
                return response.choices[0].message.content
            except Exception as exc:  # pragma: no cover - generic for test doubles
                attempt += 1
                if attempt > self.max_retries:
                    raise
                # Exponential backoff with jitter
                await asyncio.sleep(min(delay, self.max_delay))
                delay = min(self.max_delay, delay * 2 + random.random() * self.base_delay)


__all__ = ["ChatGPTClient"]
