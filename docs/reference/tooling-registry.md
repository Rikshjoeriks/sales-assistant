# Tooling & Integration Registry

Document every agreed instrument, plugin, external service, and interface layer before implementation begins. Update entries when versions change or new integrations are introduced.

| Date (UTC) | Phase / Task IDs | Tool / Service | Purpose & Scope | Version / Configuration | Access & Credential Notes | Compatibility / Risks | Owner |
|------------|------------------|----------------|-----------------|-------------------------|--------------------------|-----------------------|-------|
| 2025-09-24 | Phase 3 baseline | Python runtime | Primary language for services, tooling, and tests. | Python 3.11.x (exact patch TBD) | Local installation; virtualenv/poetry to be decided. | Ensure Windows compatibility; align with Docker image later. | Shared |
| 2025-09-24 | Phase 3 baseline | FastAPI | Web framework for service layer. | Latest stable 0.1x pinned via `pyproject` | Requires uvicorn/gunicorn; verify async support. | Keep dependency versions pinned to avoid breaking changes. | Backend |
| 2025-09-24 | Phase 3 baseline | PostgreSQL + pgvector | Primary data store and vector search extension. | PostgreSQL 15.x + pgvector 0.5+ | Manage via Docker Compose; secure credentials in `.env`. | Windows developers need Docker Desktop. | Data |
| 2025-09-24 | Phase 3 baseline | Redis | Caching layer for session/context storage. | Redis 7.x | Run via Docker Compose; set password via env vars. | Verify persistence strategy; flush between tests. | Infra |
| 2025-09-24 | Phase 3 baseline | OpenAI API | LLM inference provider. | `gpt-4o` family (exact model TBD) | API keys stored in 1Password → `.env` at runtime. | Monitor rate limits and cost; implement retries/backoff. | AI Integrations |
| 2025-09-24 | Phase 3 baseline | Git + GitHub | Source control and collaboration. | git >= 2.40 | SSH keys managed per contributor. | Enforce rebase workflow to minimize conflicts. | Everyone |
| 2025-09-24 | Phase 3 baseline | PowerShell environment | Default local shell for scripts/commands. | Windows PowerShell 5.1 | Consider installing PowerShell 7 for advanced scripts. | Ensure scripts are cross-shell compatible. | Dev Experience |
| 2025-09-25 | T001-T012 | Poetry | Python dependency and virtualenv manager. | >=1.8, `package-mode=false` | Install globally; run via `poetry` wrapper. | Keep lockfile in sync; ensure contributors use same version. | Platform |
| 2025-09-25 | T026+ (future) | Celery | Background worker for ingestion/analytics tasks. | 5.4.x | Broker via Redis, results backend TBD. | Configure retry/backoff; monitor worker concurrency. | Backend |
| 2025-09-25 | Cross-cutting | structlog | JSON logging and context binding. | 24.1.x | No secrets in logs; respect log level from env. | Ensure middleware binds request IDs to avoid missing context. | Platform |
| 2025-09-25 | T026 | pypdf | PDF extraction for ingestion service. | 4.3.x pinned via `pyproject` | Pure-Python, no extra system deps. | Validate against encrypted PDFs; fall back gracefully. | Backend |
| 2025-09-25 | T029 | sentence-transformers | Embedding generation for knowledge chunks. | `sentence-transformers` 3.0.x | Requires Torch; ensure models cached locally. | Large model download (~400MB); document offline strategy. | AI Integrations |
- 2025-09-25 – T029: EmbeddingService (src/app/knowledge/services/embedding_service.py)
	- Purpose: Generate text embeddings with sentence-transformers; deterministic fallback path.
- 2025-09-25 – T030: VectorRepository (src/app/knowledge/repositories/vector_repository.py)
	- Purpose: In-memory cosine similarity search; pgvector-ready interface for DB-backed path.
- 2025-09-25 – T031: KnowledgeSourceRepository (src/app/knowledge/repositories/source_repository.py)
	- Purpose: SQLAlchemy adapter for sources/concepts with join helpers.
- 2025-09-25 – T033: Knowledge Orchestrator (src/app/knowledge/services/orchestrator.py)
	- Purpose: Glue service to ingest, chunk, extract concepts, embed, and index.
- 2025-09-25 – T032: Knowledge Worker Skeleton (src/workers/knowledge_worker.py)
	- Purpose: Background worker entrypoint; future Celery task wiring.
- 2025-09-25 – T036: Ingestion Metrics Helper (src/app/knowledge/services/metrics.py)
	- Purpose: Structlog-backed counters/fields for ingestion pipeline.
- 2025-09-26 – T041: PersonalityEngine (src/app/customers/services/personality_engine.py)
	- Purpose: Heuristic DISC-style persona inference with confidence.
- 2025-09-26 – T040: CustomerProfileRepository (src/app/customers/repositories/profile_repository.py)
	- Purpose: Profile persistence abstraction + search filtering helpers.
- 2025-09-26 – T042: DecisionService (src/app/customers/services/decision_service.py)
	- Purpose: Aggregate decision drivers from profile + interactions.
- 2025-09-26 – T043: InteractionRepository (src/app/customers/repositories/interaction_repository.py)
	- Purpose: Interaction history store with aggregate helpers.
- 2025-09-26 – T046: Customer SearchService (src/app/customers/services/search_service.py)
	- Purpose: Filter + paginate profiles; wraps repository queries and summaries.
- 2025-09-26 – T049: Recommendation Context Repository (src/app/recommendations/repositories/context_repository.py)
	- Purpose: Persist sales contexts and generated recommendations.
- 2025-09-27 – T050: RecommendationContextBuilder (src/app/recommendations/services/context_builder.py)
	- Purpose: Compose/persist context enriched with personality, decision, and interactions.
| 2025-09-30 | Phase 3.5 (T050, T051) | SQLAlchemy ORM | Persistence for customers, recommendations, knowledge concepts. | 2.0.x | SQLite for tests; Postgres in Docker. | Keep metadata in sync with Alembic; watch for session scope in async. | Backend |
| 2025-09-30 | Phase 3.5 (T051) | AnyIO + pytest-asyncio | Async test harness for retrieval service. | anyio 4.11, pytest-asyncio 0.23 | Use `@pytest.mark.anyio` in async tests. | Ensure event loop policy compatible on Windows. | QA |
| 2025-09-30 | Phase 3.5 (T051) | In-memory vector cache | Test-friendly fallback inside VectorRepository. | Built-in | Enabled when Session is None. | Differences vs pgvector search semantics; align thresholds. | Backend |
| 2025-09-30 | Phase 3.5 (T051) | PowerShell 5.1 | Prereq script runner; `pwsh` not required. | Windows PowerShell v5.1 | Use `-ExecutionPolicy Bypass` when needed. | Prefer cross-shell scripts for portability. | Dev Experience |
| 2025-09-30 | Phase 3.5 (T051) | Typing guards | Type-ignore adapter for dummy repos in tests. | n/a | Apply narrow `# type: ignore` when mocking strict signatures. | Revisit when introducing protocol interfaces. | QA |
