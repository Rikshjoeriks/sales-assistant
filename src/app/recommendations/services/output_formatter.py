"""Output formatter for multi-format responses (T057)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OutputFormatter:
    """Format generated recommendation text into requested output styles.

    Supported formats:
    - email: Adds a salutation and a simple signature
    - bullet: Converts newline-separated lines to dashed bullet points
    - script: Prefixes lines with a speaker label
    - presentation: Adds a heading and bulletizes each line
    - default: returns original text
    """

    def format(self, *, text: str, output_format: str, audience_name: str | None = None) -> str:
        fmt = (output_format or "").lower().strip()
        if fmt == "email":
            name = (audience_name or "Customer").strip()
            salutation = f"Dear {name},\n\n"
            signature = "\n\nBest regards,\nYour Sales Assistant"
            return f"{salutation}{text}{signature}"
        if fmt == "bullet":
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(f"- {line}" for line in lines)
        if fmt == "script":
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(f"Agent: {line}" for line in lines)
        if fmt == "presentation":
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            bullets = "\n".join(f"- {line}" for line in lines)
            return f"# Recommendations\n\n{bullets}"
        return text


__all__ = ["OutputFormatter"]
