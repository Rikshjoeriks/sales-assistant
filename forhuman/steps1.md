Immediate Next Steps
Read the new manual: working-with-spec-kit.md. It’s your playbook for feeding me info, following the Spec Kit workflow, handling git, and staying constitution-compliant.
Start Phase 3.1 (Setup & Infrastructure) from tasks.md:
Initialize the Python project (FastAPI, SQLAlchemy, pgvector, OpenAI client).
Configure linting, logging, Docker, .env scaffolding.
Document the setup as you go (docs/setup.md once created).
Phase 3.2 (Tests First): Before writing implementation, add the failing contract and unit tests outlined for knowledge, customer, and recommendation APIs.
Implement Knowledge Ingestion (Phase 3.3) once tests are failing: build the ingestion pipeline so our three starter sources (sales psychology book, car spec sheet, communication guide) can be processed end-to-end.
Commit after meaningful checkpoints (e.g., environment scaffold done, knowledge tests implemented, ingestion service passing tests).