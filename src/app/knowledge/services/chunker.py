"""Utility for splitting documents into semantic chunks."""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass(slots=True)
class TextChunk:
    """Represents a single chunk of text with positional metadata."""

    chunk_id: uuid.UUID
    order: int
    text: str
    start_index: int
    end_index: int


class TextChunker:
    """Split normalised document text into overlapping windows."""

    def __init__(self, *, max_chars: int = 1000, overlap: int = 150) -> None:
        if max_chars <= 0:
            raise ValueError("max_chars must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= max_chars:
            raise ValueError("overlap must be smaller than max_chars")

        self._max_chars = max_chars
        self._overlap = overlap

    def chunk(self, text: str) -> list[TextChunk]:
        """Return chunks that are friendly for embedding generation."""

        if not text.strip():
            return []

        sentences = list(self._segment(text))
        windows = self._sliding_windows(sentences)

        return [self._build_chunk(chunk_text, order, start, end) for order, (chunk_text, start, end) in enumerate(windows)]

    def _segment(self, text: str) -> Iterable[tuple[str, int, int]]:
        sentence_pattern = re.compile(r"(?<=[.!?])\s+")
        matches = list(sentence_pattern.finditer(text))
        if not matches:
            yield text, 0, len(text)
            return

        start = 0
        for match in matches:
            end = match.end(0)
            yield text[start:match.start(0) + 1].strip(), start, match.start(0) + 1
            start = match.end(0) - 1
        if start < len(text):
            yield text[start:].strip(), start, len(text)

    def _sliding_windows(self, sentences: list[tuple[str, int, int]]) -> Iterator[tuple[str, int, int]]:
        current_text: list[str] = []
        current_start = sentences[0][1]
        current_end = sentences[0][2]

        for sentence, start, end in sentences:
            if not current_text:
                current_start = start
            current_text.append(sentence)
            current_end = end
            joined = " ".join(current_text).strip()

            if len(joined) >= self._max_chars:
                yield joined, current_start, current_end
                overlap_chars = min(self._overlap, len(joined))
                overlap_target = len(joined) - overlap_chars
                while current_text and len(" ".join(current_text).strip()) > overlap_target:
                    current_text.pop(0)
                current_start = start if current_text else end

        if current_text:
            yield " ".join(current_text).strip(), current_start, current_end

    def _build_chunk(self, text: str, order: int, start: int, end: int) -> TextChunk:
        return TextChunk(chunk_id=uuid.uuid4(), order=order, text=text, start_index=start, end_index=end)


__all__ = ["TextChunk", "TextChunker"]
