"""Heuristic concept extraction from document chunks."""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass
from typing import Iterable, Sequence

from .chunker import TextChunk


logger = logging.getLogger(__name__)


DEFAULT_CONCEPT_TYPES = (
    ("psychology", re.compile(r"principle|technique|objection", re.IGNORECASE)),
    ("technical", re.compile(r"horsepower|safety|feature|engine|battery", re.IGNORECASE)),
    ("communication", re.compile(r"story|script|presentation|tone|message", re.IGNORECASE)),
)


@dataclass(slots=True)
class ExtractedConcept:
    concept_id: uuid.UUID
    source_chunk_id: uuid.UUID
    title: str
    concept_type: str
    summary: str
    keywords: list[str]
    confidence_score: float


class ConceptExtractor:
    """Lightweight extractor turning chunks into structured concepts."""

    def __init__(
        self,
        *,
        custom_type_patterns: Sequence[tuple[str, re.Pattern[str]]] | None = None,
        max_keywords: int = 8,
    ) -> None:
        self._max_keywords = max(1, max_keywords)
        self._patterns = tuple(custom_type_patterns or DEFAULT_CONCEPT_TYPES)

    def extract(self, chunks: Iterable[TextChunk]) -> list[ExtractedConcept]:
        concepts: list[ExtractedConcept] = []
        for chunk in chunks:
            if not chunk.text.strip():
                continue

            title = self._infer_title(chunk.text)
            concept_type = self._infer_type(chunk.text)
            keywords = self._derive_keywords(chunk.text)

            concepts.append(
                ExtractedConcept(
                    concept_id=uuid.uuid4(),
                    source_chunk_id=chunk.chunk_id,
                    title=title,
                    concept_type=concept_type,
                    summary=chunk.text.strip()[:500],
                    keywords=keywords,
                    confidence_score=self._estimate_confidence(chunk.text, keywords),
                )
            )

        return concepts

    def _infer_title(self, text: str) -> str:
        first_line = text.strip().split(".")[0]
        first_line = re.sub(r"[^a-zA-Z0-9\s]", "", first_line).strip()
        if len(first_line.split()) <= 12 and first_line:
            return first_line.title()
        return text.strip()[:60].title()

    def _infer_type(self, text: str) -> str:
        for type_name, pattern in self._patterns:
            if pattern.search(text):
                return type_name
        return "general"

    def _derive_keywords(self, text: str) -> list[str]:
        words = re.findall(r"[a-zA-Z]{4,}", text.lower())
        unique: list[str] = []
        seen: set[str] = set()
        for word in words:
            if word not in seen:
                seen.add(word)
                unique.append(word)
            if len(unique) >= self._max_keywords:
                break
        return unique

    def _estimate_confidence(self, text: str, keywords: list[str]) -> float:
        token_count = max(1, len(text.split()))
        keyword_ratio = min(1.0, len(keywords) / 6)
        length_bonus = min(1.0, token_count / 200)
        return round(0.5 + 0.5 * (keyword_ratio + length_bonus) / 2, 2)


__all__ = ["ConceptExtractor", "ExtractedConcept"]
