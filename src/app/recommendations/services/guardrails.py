"""Basic guardrails for courtesy/profanity (T059).

Initial implementation provides minimal redaction and tone softening helpers.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Guardrails:
    denylist: frozenset[str] = frozenset({"damn", "hell"})  # minimal placeholder

    def filter_text(self, text: str) -> str:
        if not text:
            return text
        result = text
        for word in self.denylist:
            result = result.replace(word, "****")
        return result


__all__ = ["Guardrails"]
