"""Bootstrap sample knowledge sources for local development."""
from __future__ import annotations

import argparse
from pathlib import Path

from src.app.knowledge.dependencies import orchestrator_session
from src.app.knowledge.services.orchestrator import IngestionRequest


SAMPLES = {
    "psychology": "Social proof and reciprocity remain powerful triggers in complex automotive sales.",
    "technical": "The 2024 Toyota Camry Hybrid pairs a 2.5L engine with an electric motor for 208 hp combined.",
    "communication": "Use consultative framing to acknowledge objections before reframing value propositions.",
}


def main(dir_path: Path) -> None:
    with orchestrator_session() as orchestrator:
        for type_name, text in SAMPLES.items():
            try:
                payload = IngestionRequest(
                    filename=f"seed-{type_name}.txt",
                    data=text.encode("utf-8"),
                    content_type="text/plain",
                    title=f"Seed {type_name.title()} Source",
                    source_type=type_name,
                    author="Seed Script",
                    version="1.0",
                    metadata={"generated": True},
                )
                source = orchestrator.ingest(payload)
                print(f"Seeded {type_name} source: {source.source_id}")
            except Exception as exc:
                print(f"Failed to seed {type_name}: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed local knowledge sources")
    parser.add_argument("--dir", type=Path, default=Path.cwd(), help="Unused placeholder for compatibility")
    args = parser.parse_args()
    main(args.dir)
