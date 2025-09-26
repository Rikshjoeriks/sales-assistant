# Tasks: Core Knowledge Ingestion & Sales Content Generation

**Input**: Design documents from `C:\Users\vanag\Documents\SALESASSISTANT\specs\main`  
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI/worker
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness
```

## Phase 3.1: Setup & Infrastructure
- [X] T001 Initialize repo Python project structure (`src/`, `tests/`, `scripts/`)
- [X] T002 Configure Python toolchain (`pyproject.toml` with FastAPI, SQLAlchemy, pgvector, sentence-transformers, OpenAI)
- [X] T003 Create `.env.example` with placeholders (OPENAI_API_KEY, DATABASE_URL, REDIS_URL)
- [X] T004 [P] Set up Dockerfiles (`docker/Dockerfile.api`, `docker/Dockerfile.worker`) and `docker-compose.yml`
- [X] T005 [P] Configure linting/formatting (`ruff.toml`, `black`, `isort`, pre-commit hooks)
- [X] T006 Establish base FastAPI app scaffold (`src/app/main.py`) with health endpoint
- [X] T007 Create database initialization scripts (`scripts/db/initialize.sql`, Alembic setup)
- [X] T008 Define project logging config (`src/app/core/logging.py`) with JSON logs
- [X] T009 Configure observability basics (structlog logging middleware, request ID injection)
- [X] T010 Add Makefile/Taskfile for common commands (`make install`, `make test`, `make lint`)
- [X] T011 Implement feature flag/config loader (`src/app/core/config.py`) reading env vars
- [X] T012 Document setup instructions in `docs/setup.md`

## Phase 3.2: Tests First (TDD) – Foundational Contracts & Utilities
**All tests MUST exist and fail before related implementation.**
- [X] T013 Create pytest configuration (`pytest.ini`) with async plugins
- [X] T014 Write failing integration test for health endpoint (`tests/integration/api/test_health.py`)
- [X] T015 [P] Contract test for knowledge source upload API (`tests/contract/api/test_knowledge_sources_post.py`)
- [X] T016 [P] Contract test for knowledge concept search API (`tests/contract/api/test_knowledge_search_post.py`)
- [X] T017 [P] Contract test for recommendation generation API (`tests/contract/api/test_recommendations_generate_post.py`)
- [X] T018 [P] Contract test for objection handling API (`tests/contract/api/test_recommendations_objection_post.py`)
- [X] T019 [P] Contract test for customer profile API (`tests/contract/api/test_customers_post.py`)
- [X] T020 [P] Unit tests for configuration loader (`tests/unit/core/test_config.py`)
- [X] T021 Define fixtures for database and OpenAI mocks (`tests/conftest.py`)
- [X] T022 Create failing semantic search tests (`tests/unit/knowledge/test_vector_store.py`)
- [X] T023 Create failing tests for personality detection heuristics (`tests/unit/customers/test_personality_engine.py`)
- [X] T024 Write scenario test for recommendation pipeline (`tests/integration/recommendations/test_pipeline_happy_path.py`)
- [X] T025 Write failing test for feedback analytics (`tests/unit/analytics/test_effectiveness_metrics.py`)

## Phase 3.3: Knowledge Ingestion & Processing
- [X] T026 Implement file ingestion service (`src/app/knowledge/services/ingestion_service.py`) supporting PDF/TXT/DOCX parsing
- [X] T027 Build text chunker and metadata extractor (`src/app/knowledge/services/chunker.py`)
- [X] T028 Create concept extraction pipeline (`src/app/knowledge/services/concept_extractor.py`) using spaCy rules
- [X] T029 Add embedding generator using sentence-transformers (`src/app/knowledge/services/embedding_service.py`)
- [X] T030 Implement vector store gateway (`src/app/knowledge/repositories/vector_repository.py`) with pgvector
- [X] T031 Develop knowledge source repository (`src/app/knowledge/repositories/source_repository.py`)
- [X] T032 Build knowledge processing background worker (`src/workers/knowledge_worker.py`) with task queue (RQ/Celery)
- [X] T033 Create ingestion orchestration service (`src/app/knowledge/services/orchestrator.py`)
- [X] T034 Implement knowledge API router (`src/app/knowledge/api/router.py`) satisfying contracts
- [X] T035 Add validation schemas (Pydantic models) for knowledge endpoints (`src/app/knowledge/api/schemas.py`)
- [X] T036 Wire ingestion metrics and logging (`src/app/knowledge/services/metrics.py`)
- [X] T037 Populate sample seed scripts for three starter knowledge sources (`scripts/seed/seed_knowledge.py`)
- [X] T038 Update Alembic migrations for knowledge tables and pgvector extension

## Phase 3.4: Customer Intelligence Platform
- [ ] T039 Implement customer profile ORM models (`src/app/customers/models.py`)
- [ ] T040 Implement customer repository (`src/app/customers/repositories/profile_repository.py`)
- [ ] T041 Build personality assessment engine (`src/app/customers/services/personality_engine.py`)
- [ ] T042 Create decision factor analyzer (`src/app/customers/services/decision_service.py`)
- [ ] T043 Implement interaction log model/repository (`src/app/customers/repositories/interaction_repository.py`)
- [ ] T044 Build customer API router (`src/app/customers/api/router.py`) covering CRUD endpoints
- [ ] T045 Add schemas and validators (`src/app/customers/api/schemas.py`)
- [ ] T046 Implement customer search/filter service with pagination (`src/app/customers/services/search_service.py`)
- [ ] T047 Integrate analytics summary endpoints (`src/app/customers/api/analytics_router.py`)
- [ ] T048 Seed sample customer personas (`scripts/seed/seed_customers.py`)

## Phase 3.5: Recommendation Engine & Prompt Orchestration
- [ ] T049 Implement sales context model/repository (`src/app/recommendations/models.py`)
- [ ] T050 Build recommendation context builder (`src/app/recommendations/services/context_builder.py`)
- [ ] T051 Create retrieval pipeline combining knowledge concepts (`src/app/recommendations/services/retrieval_service.py`)
- [ ] T052 Develop prompt template manager (`src/app/recommendations/services/prompt_builder.py`)
- [ ] T053 Implement ChatGPT client wrapper with retry/backoff (`src/app/recommendations/clients/chatgpt_client.py`)
- [ ] T054 Build recommendation synthesis service (`src/app/recommendations/services/synthesis_service.py`) enforcing source attribution
- [ ] T055 Implement objection handling generator (`src/app/recommendations/services/objection_service.py`)
- [ ] T056 Add recommendation API router (`src/app/recommendations/api/router.py`)
- [ ] T057 Implement output formatter for multi-format responses (`src/app/recommendations/services/output_formatter.py`)
- [ ] T058 Integrate token usage tracking + cost estimation (`src/app/recommendations/services/token_tracker.py`)
- [ ] T059 Add guardrail filters (basic courtesy, profanity check) (`src/app/recommendations/services/guardrails.py`)
- [ ] T060 Create caching for recent recommendations (`src/app/recommendations/services/cache.py`)

## Phase 3.6: Feedback Loop & Analytics
- [ ] T061 Implement recommendation feedback model/repository (`src/app/feedback/models.py`)
- [ ] T062 Build feedback recording service (`src/app/feedback/services/feedback_service.py`)
- [ ] T063 Integrate effectiveness scoring engine (`src/app/analytics/services/effectiveness_engine.py`)
- [ ] T064 Implement analytics API router (`src/app/analytics/api/router.py`)
- [ ] T065 Create scheduled job to update learning metrics (`src/workers/analytics_worker.py`)
- [ ] T066 Generate dashboards/reports via CLI (`src/cli/reports.py`)
- [ ] T067 Add automated prompts to adjust weighting based on feedback (`src/app/recommendations/services/learning_adjuster.py`)

## Phase 3.7: Integration, Security & Compliance
- [ ] T068 Configure API authentication/authorization (API keys, rate limiting) (`src/app/security/auth.py`)
- [ ] T069 Implement middleware for request logging, correlation IDs (`src/app/core/middleware.py`)
- [ ] T070 Add error handling & problem details responses (`src/app/core/errors.py`)
- [ ] T071 Configure OpenAPI documentation (`src/app/main.py`, `docs/api/openapi_overrides.py`)
- [ ] T072 Integrate background task queue (Redis/Celery setup) (`src/app/core/task_queue.py`)
- [ ] T073 Implement secrets management helper (AWS/GCP/Azure placeholder) (`src/app/core/secrets.py`)
- [ ] T074 Add rate limiting middleware and tests (`src/app/security/rate_limiter.py`)

## Phase 3.8: Quality Assurance & Operations
- [ ] T075 Implement load/performance tests for recommendation endpoint (`tests/performance/test_recommendations_perf.py`)
- [ ] T076 Add contract tests for CLI report generation (`tests/contract/cli/test_reports.py`)
- [ ] T077 Configure CI pipeline (GitHub Actions workflow `.github/workflows/ci.yml`)
- [ ] T078 Create staging deployment script (`scripts/deploy/staging_deploy.ps1`)
- [ ] T079 Document runbooks (`docs/runbooks/ingestion.md`, `docs/runbooks/recommendations.md`)
- [ ] T080 Add end-to-end smoke test scenario (`tests/e2e/test_sales_flow.py`)
- [ ] T081 Populate README Quickstart section with API usage examples
- [ ] T082 Create knowledge base maintenance guide (`docs/knowledge/maintenance.md`)
- [ ] T083 Final regression test sweep checklist (`docs/qa/regression_checklist.md`)
- [ ] T084 Prepare release notes template (`docs/releases/release_template.md`)

## Dependency Graph (High-Level)
- Phase 3.1 must complete before Phase 3.3+  
- Phase 3.2 tests precede implementations in Phases 3.3–3.6  
- Knowledge ingestion (Phase 3.3) required before recommendation engine (Phase 3.5)  
- Customer intelligence (Phase 3.4) and knowledge ingestion feed recommendation engine  
- Feedback loop (Phase 3.6) depends on recommendations being operational  
- Integration & QA (Phases 3.7–3.8) depend on core features being in place

## Parallel Execution Examples
- Run T004/T005 (Docker + linting) in parallel with T006 (FastAPI scaffold)
- Execute knowledge vector repository (T030) alongside concept extractor (T028) after base ingestion service (T026) exists
- Customer API tasks (T044–T047) can proceed while recommendation retrieval (T051) is in progress  
- Feedback analytics (T061–T067) parallel with security tasks (T068–T074) once recommendations are functional

## Validation Checklist
- [ ] All tests written prior to implementation per TDD mandate
- [ ] Each API contract has corresponding tests and implementation
- [ ] Recommendation outputs provide citation metadata and pass courtesy guardrails
- [ ] Performance target (<2s) validated with load tests
- [ ] Documentation and runbooks updated before release
