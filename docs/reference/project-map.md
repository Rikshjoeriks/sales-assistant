# Project Knowledge Map

Track every directory and key file so collaborators (and the assistant) can navigate with certainty. Update this map whenever structure changes.

| Path | Type | Purpose / Key Contents | Owner / Notes |
|------|------|------------------------|---------------|
| `/` | Directory | Repository root holding governance, specs, and docs. |  |
| `/.gitignore` | File | Git ignore rules. |  |
| `/.specify/` | Directory | Spec Kit configuration, memory, and helper scripts. | Governed by constitution updates. |
| `/.specify/memory/constitution.md` | File | Canonical governance document (v1.6.0). | Update via controlled amendments only. |
| `/.specify/scripts/` | Directory | Automation scripts (e.g., plan setup). | Leave untouched unless updating Spec Kit tooling. |
| `/.specify/templates/` | Directory | Template files used by Spec Kit. | Reference only. |
| `/alembic.ini` | File | Alembic configuration pointing to `src/alembic`. | Keep DB URL synced with environments. |
| `/docs/` | Directory | Documentation hub (logs, manuals, reference). |  |
| `/docs/logs/` | Directory | Task journal, logging README, future decision logs. | Update per `/log-latest`. |
| `/docs/logs/task-journal.md` | File | Chronological task and prompt log with verification evidence. | Append after every implementation action. |
| `/docs/logs/README.md` | File | Instructions for logging workflow. | Keep aligned with constitution. |
| `/docs/manual/` | Directory | Process manuals and onboarding guides. |  |
| `/docs/manual/working-with-spec-kit.md` | File | Project playbook and handshake protocol. | Update as workflow evolves. |
| `/docs/reference/` | Directory | Knowledge map, tooling registry, future reference docs. |  |
| `/docs/reference/project-map.md` | File | This file—structural map. | Maintain diligently. |
| `/docs/reference/tooling-registry.md` | File | Agreed instruments, plugins, services with versions and risks. | Update whenever tooling changes. |
| `/docs/setup.md` | File | Local environment bootstrap instructions. | Revise when dependencies or workflows change. |
| `/specs/` | Directory | Feature specifications and planning artifacts. |  |
| `/specs/main/` | Directory | Core sales assistant specification package. | Houses spec, plan, tasks, research. |
| `/specs/main/spec.md` | File | Functional spec for knowledge ingestion & content generation. | Update when scope changes. |
| `/specs/main/plan.md` | File | Implementation roadmap with progress tracking. | Mark phases as complete. |
| `/specs/main/tasks.md` | File | Master task list (T001–T084). | Reference for task IDs. |
| `/specs/main/research.md` | File | Supporting research notes. | Extend as new insights land. |
| `/specs/main/data-model.md` | File | Entities and schema overview. | Sync with code changes once implemented. |
| `/specs/main/contracts/` | Directory | API contracts (knowledge, customers, recommendations). | Keep in lockstep with service evolution. |
| `/specs/main/quickstart.md` | File | Setup/run instructions once implemented. | Update when environment shifts. |
| `/src/` | Directory | Application source code (FastAPI app, workers, CLI). | Modules use src-based layout. |
| `/src/app/main.py` | File | FastAPI entrypoint exposing `/health`. | Extend as routers and deps grow. |
| `/src/app/core/` | Directory | Core infrastructure (config, logging, observability, future middleware). |  |
| `/src/app/core/config.py` | File | Pydantic settings + feature flags. | Expand with new env vars. |
| `/src/app/core/logging.py` | File | Structlog JSON logging helpers. | Bind extra context fields carefully. |
| `/src/app/core/observability.py` | File | Request middleware & CORS setup. | Extend with tracing exporters later. |
| `/src/app/core/db.py` | File | SQLAlchemy engine/session helpers and declarative base for knowledge models. | Keep metadata synced with migrations. |
| `/src/app/knowledge/` | Directory | Knowledge ingestion domain modules (services, repositories, API, models). | Phase 3.3 implementation. |
| `/src/app/knowledge/models.py` | File | SQLAlchemy models for sources, concepts, vectors. | Align with Alembic migrations (T038). |
| `/src/app/knowledge/dependencies.py` | File | Dependency providers wiring orchestrator stack. | Ensure singleton instances stay thread-safe. |
| `/src/app/knowledge/services/` | Directory | Ingestion pipeline components (ingestion, chunker, concept extractor, embeddings, metrics, orchestrator). | Review for future Celery integration. |
| `/src/app/knowledge/api/` | Directory | FastAPI router and Pydantic schemas for knowledge endpoints. | Contracts synced with `/specs/main/contracts/knowledge.yaml`. |
| `/src/app/knowledge/repositories/` | Directory | In-memory repositories for sources and vectors (pgvector placeholder). | Replace with SQLAlchemy/pgvector in T038+. |
| `/src/app/customers/` | Directory | Customer intelligence domain (models, services, API). | Phase 3.4 implementation in progress. |
| `/src/app/customers/models.py` | File | SQLAlchemy models for profiles and interactions. | Sync with upcoming customer migrations. |
| `/src/app/customers/dependencies.py` | File | FastAPI dependency wiring for customer services. | Provides shared session + singleton services. |
| `/src/app/customers/api/` | Directory | FastAPI router and schemas for customer profiles & analytics. | Align responses with `/specs/main/contracts/customers.yaml`. |
| `/src/app/customers/repositories/` | Directory | Persistence adapters for profiles and interactions. | Requires Postgres integration later. |
| `/src/app/customers/services/` | Directory | Personality, decision, and search services for customers. | Heuristic engines; extend with ML later. |
| `/src/alembic/` | Directory | Alembic migration environment and versions. | Add migrations under `versions/`. |
| `/src/alembic/env.py` | File | Alembic runtime configuration referencing settings. | Update target metadata once models exist. |
| `/pytest.ini` | File | Pytest configuration (async mode, warnings). | Extend as new markers/paths added. |
| `/README.md` | File | Repo overview. | Refresh when major milestones achieved. |
| `/pyproject.toml` | File | Poetry project configuration with dependencies and tooling. | Maintain pinned versions. |
| `/ruff.toml` | File | Ruff linting configuration. | Keep in sync with team rules. |
| `/.pre-commit-config.yaml` | File | Pre-commit hook definitions (ruff, black, isort). | Run `pre-commit autoupdate` periodically. |
| `/Makefile` | File | Common local automation commands. | Update when workflows change. |
| `/docker/` | Directory | Docker build context for API and worker images. |  |
| `/docker/Dockerfile.api` | File | API service container definition. | Keep dependencies aligned with `pyproject`. |
| `/docker/Dockerfile.worker` | File | Background worker container definition. | Ensure command matches Celery app path. |
| `/docker-compose.yml` | File | Multi-service dev stack (API, worker, Postgres, Redis). | Update when services or env vars shift. |
| `/scripts/` | Directory | Helper scripts (DB, seeds, deploy). |  |
| `/scripts/db/initialize.sql` | File | Postgres bootstrap (roles, pgvector). | Run once per environment. |
| `/tests/` | Directory | Pytest suite organized by unit/contract/integration/perf/e2e. | Expand as features implement. |
| `/tests/conftest.py` | File | Shared pytest fixtures (async client, mocks). | Extend with real DB/OpenAI fixtures later. |
| `/tests/integration/api/test_health.py` | File | Health endpoint contract. | Should always pass. |
| `/tests/integration/api/test_knowledge_routes.py` | File | Exercises knowledge upload + semantic search flow (Phase 3.3 verification). | Keep fixtures aligned with orchestrator behaviour. |
| `/tests/integration/api/test_customers_routes.py` | File | Covers customer CRUD, interactions, analytics endpoints. | Depends on in-memory SQLite fixtures. |
| `/tests/contract/api/` | Directory | API contract tests (knowledge, recommendations, customers). | Keep aligned with OpenAPI design. |
| `/tests/unit/core/test_config.py` | File | Validates config loader behaviour. | Update as settings expand. |
| `/tests/unit/knowledge/test_vector_store.py` | File | Ensures vector repository interface. | Update once implementation solidified. |
| `/tests/unit/knowledge/test_source_repository.py` | File | Verifies knowledge source repository persistence. | Uses SQLite-backed session fixture. |
| `/tests/unit/customers/test_personality_engine.py` | File | Disc personality engine expectations. | Update when engine implemented. |
| `/tests/unit/customers/test_decision_service.py` | File | Ensures decision insights aggregate profile + interactions. | Expand as analytics mature. |
| `/tests/unit/customers/test_search_service.py` | File | Verifies customer search pagination & filters. | Uses repository test double. |
| `/tests/unit/customers/test_personality_engine.py` | File | Disc personality engine expectations. | Update when engine implemented. |
| `/tests/integration/recommendations/test_pipeline_happy_path.py` | File | Recommendation pipeline end-to-end scenario expectations. | Flesh out with real assertions later. |
| `/tests/unit/analytics/test_effectiveness_metrics.py` | File | Analytics effectiveness contract. | Update alongside analytics engine. |
| `/MyProject/` | Directory | Legacy or placeholder content (investigate before use). | Flag for cleanup in future. |
| `/Staying_organized_and_productive.md` | File | Legacy note—review for relevance. | Consider migrating or archiving. |
| `/steps1.md` | File | Legacy instructions. | Evaluate during implementation phase. |

> **Reminder:** Whenever you add, move, or remove files/directories, update this table in the same commit. Include the reason or task ID in the notes column.
