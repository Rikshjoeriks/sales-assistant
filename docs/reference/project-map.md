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
| `/src/app/main.py` | File | FastAPI entrypoint exposing `/health` and mounting knowledge + customer routers. | Extend as routers and deps grow; register new domains here. |
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
| `/src/app/customers/` | Directory | Customer intelligence domain (models, services, API). | Phase 3.4 implementation complete. |
| `/src/app/customers/models.py` | File | SQLAlchemy models for profiles and interactions. | Sync with upcoming customer migrations. |
| `/src/app/customers/dependencies.py` | File | FastAPI dependency wiring for customer services. | Provides shared session + singleton services. |
| `/src/app/customers/api/` | Directory | FastAPI router and schemas for customer profiles, interactions, analytics. | Align responses with `/specs/main/contracts/customers.yaml`. |
| `/src/app/customers/api/router.py` | File | Implements customer CRUD, interaction logging, and search endpoints. | Keep response models synced with schemas and tests. |
| `/src/app/customers/api/analytics_router.py` | File | Customer analytics endpoints exposing summary metrics and follow-up reminders. | Mount alongside main router in `src/app/main.py`. |
| `/src/app/customers/api/schemas.py` | File | Pydantic models for customer creation, summaries, detail views, interactions, analytics. | Update alongside service contract changes. |
| `/src/app/customers/repositories/` | Directory | Persistence adapters for profiles and interactions. | Requires Postgres integration later. |
| `/src/app/customers/repositories/profile_repository.py` | File | Customer profile persistence abstraction with filtering helpers for search. | Replace in-memory logic with SQLAlchemy when DB wired. |
| `/src/app/customers/repositories/interaction_repository.py` | File | Stores and retrieves interaction history plus analytics aggregates. | Ensure schema stays aligned with migrations. |
| `/src/app/customers/services/` | Directory | Personality, decision, and search services for customers. | Heuristic engines; extend with ML later. |
| `/src/app/customers/services/personality_engine.py` | File | DISC-style personality inference with keyword heuristics and confidence scoring. | Tune heuristics using real interaction data. |
| `/src/app/customers/services/decision_service.py` | File | Aggregates decision drivers and surfaces sales recommendations. | Expand once analytics backend ready. |
| `/src/app/customers/services/search_service.py` | File | Translates filter requests into repository queries and wraps summaries/pagination. | Keep in sync with repository query capabilities. |
| `/src/app/customers/services/summary_service.py` | File | Builds profile summaries and transforms stored profiles for evaluation. | Shared utility across routers, seeds, and services. |
| `/src/app/recommendations/` | Directory | Recommendation engine domain (models, services, clients, API). | Phase 3.5 implementation in progress. |
| `/src/app/recommendations/models.py` | File | SQLAlchemy models for sales contexts, recommendations, and source references. | Sync with Alembic migrations. |
| `/src/app/recommendations/repositories/` | Directory | Persistence adapters for recommendation workflow. | Depends on models metadata. |
| `/src/app/recommendations/repositories/context_repository.py` | File | Manages sales contexts and generated recommendations with source references. | Provides domain records for recommendation services. |
| `/src/app/recommendations/services/` | Directory | Recommendation orchestration services (context building, retrieval, prompting). | Build out during Phase 3.5. |
| `/src/app/recommendations/services/context_builder.py` | File | Composes customer signals into persisted recommendation contexts. | Feeds downstream retrieval & generation. |
| `/src/app/recommendations/services/retrieval_service.py` | File | Retrieves relevant concepts and joins with source metadata for prompts. | Inputs: embedding + filters; outputs: sorted bundle. |
| `/src/app/recommendations/services/prompt_builder.py` | File | Builds chat prompts from context and retrieval bundles with truncation heuristics. | Produces system/user parts and messages list. |
| `/src/app/recommendations/clients/chatgpt_client.py` | File | Async ChatGPT client wrapper with retry/backoff. | Accepts preconfigured client; no network in tests. |
| `/src/app/recommendations/services/synthesis_service.py` | File | Orchestrates prompt build + chat call and records recommendation with source attributions. | Returns RecommendationRecord via repository. |
| `/src/app/recommendations/services/__init__.py` | File | Aggregates recommendation service exports. | Update as new services land. |
| `/src/alembic/` | Directory | Alembic migration environment and versions. | Add migrations under `versions/`. |
| `/src/alembic/env.py` | File | Alembic runtime configuration referencing settings. | Update target metadata once models exist. |
| `/src/alembic/versions/202509261300_customer_domain_tables.py` | File | Creates customer profile and interaction tables with indexes. | Keep in sync with models in `src/app/customers/models.py`. |
| `/src/alembic/versions/202509271000_recommendation_domain_tables.py` | File | Creates sales context, recommendation, and source reference tables. | Maintain alignment with `src/app/recommendations/models.py`. |
| `/src/alembic/versions/202509281100_feedback_domain_tables.py` | File | Creates `recommendation_feedback` table and index. | Sync with `src/app/feedback/models.py`. |
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
| `/scripts/seed/seed_customers.py` | File | Seeds sample customer personas and interactions via repositories. | Run after DB init to populate demo data. |
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
| `/tests/unit/customers/test_search_service.py` | File | Verifies customer search pagination, filter forwarding, and summary wrapping. | Uses repository test double mirroring service contract. |
| `/tests/unit/customers/test_summary_service.py` | File | Ensures profile summary helper merges personality and decision insights. | Keeps summary outputs deterministic. |
| `/tests/unit/recommendations/test_context_repository.py` | File | Validates sales context repository persistence and source linkage. | Uses real SQLAlchemy session fixture. |
| `/tests/unit/recommendations/test_context_builder.py` | File | Ensures context builder enriches contexts with personality, decision, and interaction signals. | Passes after T050 implementation. |
| `/tests/unit/recommendations/test_retrieval_service.py` | File | Validates retrieval sorting, limits, and empty-query behavior. | Uses dummy repositories for isolation. |
| `/tests/unit/recommendations/test_prompt_builder.py` | File | Ensures prompt sections, citations, and truncation behavior. | Uses synthetic context and retrieval bundle. |
| `/tests/unit/recommendations/test_chatgpt_client.py` | File | Validates retry/backoff behavior and payload passing to client. | Uses dummy async client doubles. |
| `/tests/integration/recommendations/test_pipeline_happy_path.py` | File | Recommendation pipeline end-to-end scenario expectations. | Flesh out with real assertions later. |
| `/tests/unit/analytics/test_effectiveness_metrics.py` | File | Analytics effectiveness contract. | Update alongside analytics engine. |
| `/src/app/feedback/` | Directory | Feedback loop domain (models, repo, service, API). | Phase 3.6 tasks T061–T064. |
| `/src/app/feedback/models.py` | File | SQLAlchemy model for recommendation feedback entries. | FK to `sales_recommendations`. |
| `/src/app/feedback/repositories.py` | File | Repository for creating and listing feedback records. | Returns typed `FeedbackRecord`. |
| `/src/app/feedback/services/service.py` | File | Feedback service with Pydantic payload and response. | Used by feedback API. |
| `/src/app/feedback/api/router.py` | File | FastAPI router exposing POST feedback endpoint. | Mounted in `src/app/main.py`. |
| `/tests/unit/feedback/test_feedback_repository.py` | File | Unit test for feedback repo round-trip. | Uses in-memory SQLite. |
| `/tests/contract/api/test_recommendations_feedback_post.py` | File | Contract test for POST /recommendations/{id}/feedback. | Expects 201 response. |
| `/MyProject/` | Directory | Legacy or placeholder content (investigate before use). | Flag for cleanup in future. |
| `/Staying_organized_and_productive.md` | File | Legacy note—review for relevance. | Consider migrating or archiving. |
| `/steps1.md` | File | Legacy instructions. | Evaluate during implementation phase. |

> **Reminder:** Whenever you add, move, or remove files/directories, update this table in the same commit. Include the reason or task ID in the notes column.
