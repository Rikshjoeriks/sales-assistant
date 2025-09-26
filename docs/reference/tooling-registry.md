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
| 2025-09-25 | T029 | sentence-transformers | Embedding generation for knowledge chunks. | `sentence-transformers` 2.6.x | Requires Torch; ensure models cached locally. | Large model download (~400MB); document offline strategy. | AI Integrations |
