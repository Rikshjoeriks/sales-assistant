"""Quick diagnostics for knowledge vectors persistence.

Run this to:
- Print row counts for sources, concepts, and vectors
- Show latest source processing statuses
- Attempt a manual vector upsert for an existing concept and report the outcome
"""
from __future__ import annotations

import sys
import uuid
from typing import Any

from src.app.core.db import SessionLocal
from src.app.knowledge.models import KnowledgeConceptModel, KnowledgeSourceModel
from src.app.knowledge.repositories.vector_repository import VectorRecord, VectorRepository


def main() -> int:
    session = SessionLocal()
    try:
        sources = session.query(KnowledgeSourceModel).all()
        concepts = session.query(KnowledgeConceptModel).all()
        vectors_count = session.execute("SELECT COUNT(*) FROM knowledge_vectors").scalar_one()

        print(f"Sources: {len(sources)}")
        print(f"Concepts: {len(concepts)}")
        print(f"Vectors: {vectors_count}")

        if sources:
            print("Latest sources (up to 5):")
            for src in sorted(sources, key=lambda s: s.created_at, reverse=True)[:5]:
                print(f"  - id={src.id} title={src.title!r} status={src.processing_status} processed_at={src.processed_at}")

        if not concepts:
            print("No concepts to test vector upsert against.")
            return 0

        test_concept_id = concepts[0].id  # pick first
        print(f"Attempting manual vector upsert for concept_id={test_concept_id}...")
        repo = VectorRepository(session=session)
        # Small 3-dim vector for quick test; cosine works as long as dims match at query time
        repo.upsert([VectorRecord(concept_id=test_concept_id, embedding=(0.1, 0.2, 0.3), metadata={"debug": True})])

        new_vectors_count = session.execute("SELECT COUNT(*) FROM knowledge_vectors").scalar_one()
        print(f"Vectors after upsert: {new_vectors_count}")
        if new_vectors_count == vectors_count:
            print("WARN: Vector upsert did not change row count. Investigate constraints or errors.")
        else:
            print("OK: Vector upsert inserted/updated a row successfully.")
        return 0
    except Exception as exc:  # pragma: no cover - diagnostic script
        print(f"ERROR during verification: {exc}")
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
