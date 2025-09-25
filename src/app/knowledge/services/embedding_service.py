"""Embedding generation backed by sentence-transformers with graceful fallback."""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from functools import cached_property
from typing import Iterable, Sequence

import numpy as np


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class EmbeddingResult:
    text: str
    vector: list[float]


class EmbeddingService:
    """Generate semantic embeddings with optional deterministic fallback."""

    def __init__(
        self,
        *,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        fallback_dim: int = 384,
        device: str | None = None,
    ) -> None:
        self._model_name = model_name
        self._fallback_dim = fallback_dim
        self._device = device

    def embed(self, texts: Sequence[str]) -> list[EmbeddingResult]:
        if not texts:
            return []

        try:
            vectors = self._model.encode(list(texts), device=self._device, normalize_embeddings=True)
            if isinstance(vectors, list):
                array = np.array(vectors, dtype=np.float32)
            else:
                array = vectors.astype(np.float32)
        except Exception as exc:  # pragma: no cover - triggered when model is unavailable
            logger.warning("Falling back to hash-based embeddings: %s", exc)
            array = np.vstack([self._fallback_embedding(text) for text in texts])

        results: list[EmbeddingResult] = []
        for text, vector in zip(texts, array):
            results.append(EmbeddingResult(text=text, vector=vector.astype(np.float32).tolist()))
        return results

    @cached_property
    def _model(self):  # type: ignore[no-untyped-def]
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(self._model_name)

    def _fallback_embedding(self, text: str) -> np.ndarray:
        digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
        repeat_count = int(np.ceil(self._fallback_dim / len(digest)))
        repeated = (digest * repeat_count)[: self._fallback_dim]
        vector = np.frombuffer(repeated, dtype=np.uint8).astype(np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm


__all__ = ["EmbeddingService", "EmbeddingResult"]
