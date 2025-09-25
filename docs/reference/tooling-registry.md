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
