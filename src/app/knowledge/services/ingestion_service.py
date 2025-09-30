"""File ingestion utilities for knowledge sources."""
from __future__ import annotations

import io
import logging
import mimetypes
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile

logger = logging.getLogger(__name__)


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}
DEFAULT_STORAGE_DIR = Path("var") / "knowledge" / "uploads"


class IngestionError(RuntimeError):
    """Raised when a document cannot be ingested."""


@dataclass(slots=True)
class IngestedDocument:
    """Represents the outcome of a single file ingestion operation."""

    document_id: uuid.UUID
    filename: str
    stored_path: Path
    content: str
    content_type: str
    metadata: dict[str, str | int | float | bool | None]


class IngestionService:
    """High level helper responsible for normalising uploaded documents."""

    def __init__(self, *, storage_dir: Path | None = None, min_chunk_chars: int = 100) -> None:
        self._storage_dir = Path(storage_dir or DEFAULT_STORAGE_DIR)
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._min_chunk_chars = max(0, min_chunk_chars)

    def ingest_bytes(
        self,
        *,
        filename: str,
        data: bytes,
        content_type: str | None = None,
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> IngestedDocument:
        """Persist an uploaded file locally and extract normalised text content.

        Parameters
        ----------
        filename:
            Original filename provided by the user.
        data:
            Raw binary data of the uploaded document.
        content_type:
            Optional MIME type derived from the upload headers.
        metadata:
            Optional metadata captured at upload time (author, version, etc.).
        """

        extension = self._resolve_extension(filename, content_type)

        document_id = uuid.uuid4()
        stored_filename = f"{document_id}{extension}"
        stored_path = self._storage_dir / stored_filename
        stored_path.write_bytes(data)

        text_content = self._extract_text(extension=extension, data=data)
        normalised_text = self._normalise_whitespace(text_content)

        return IngestedDocument(
            document_id=document_id,
            filename=filename,
            stored_path=stored_path,
            content=normalised_text,
            content_type=content_type or mimetypes.types_map.get(extension, "application/octet-stream"),
            metadata=metadata or {},
        )

    def _resolve_extension(self, filename: str, content_type: str | None) -> str:
        extension = Path(filename).suffix.lower()
        if extension and extension in SUPPORTED_EXTENSIONS:
            return extension

        if content_type:
            guessed_ext = mimetypes.guess_extension(content_type)
            if guessed_ext in SUPPORTED_EXTENSIONS:
                return guessed_ext

        raise IngestionError(
            f"Unsupported document type for '{filename}'. Supported extensions: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    def _extract_text(self, *, extension: str, data: bytes) -> str:
        if extension == ".txt":
            return data.decode("utf-8", errors="ignore")
        if extension == ".pdf":
            return self._extract_pdf(data)
        if extension == ".docx":
            return self._extract_docx(data)
        # Should never happen because we validate upfront, but keep safe fallback.
        raise IngestionError(f"Unsupported extension: {extension}")

    def _extract_pdf(self, data: bytes) -> str:
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency fallback
            logger.warning("pypdf not available, falling back to raw decode: %s", exc)
            return data.decode("utf-8", errors="ignore")

        try:
            reader = PdfReader(io.BytesIO(data))
        except Exception as exc:
            logger.warning("Failed to parse PDF via pypdf, falling back to raw decode: %s", exc)
            return data.decode("utf-8", errors="ignore")

        extracted_pages: list[str] = []
        for page in reader.pages:
            try:
                extracted_pages.append(page.extract_text() or "")
            except Exception as exc:  # pragma: no cover - defensive fallback
                logger.debug("Error extracting PDF page text: %s", exc)
                continue
        return "\n".join(filter(None, extracted_pages)) or data.decode("utf-8", errors="ignore")

    def _extract_docx(self, data: bytes) -> str:
        try:
            with ZipFile(io.BytesIO(data)) as docx_archive:
                with docx_archive.open("word/document.xml") as document_xml:
                    raw_xml = document_xml.read().decode("utf-8", errors="ignore")
        except Exception as exc:  # pragma: no cover - fallback
            logger.warning("Failed to parse DOCX content, falling back to raw decode: %s", exc)
            return data.decode("utf-8", errors="ignore")

        text = re.sub(r"<(.|\n)*?>", " ", raw_xml)
        return self._normalise_whitespace(text)

    def _normalise_whitespace(self, text: str) -> str:
        collapsed = re.sub(r"\s+", " ", text).strip()
        if not collapsed:
            return ""

        if self._min_chunk_chars <= 0:
            return collapsed

        sentences = self._split_sentences(collapsed)
        return " ".join(sentences)

    def _split_sentences(self, text: str) -> Iterable[str]:
        # Lightweight sentence approximator that avoids large NLP dependencies.
        return re.split(r"(?<=[.!?])\s+", text)


__all__ = [
    "IngestedDocument",
    "IngestionError",
    "IngestionService",
]
