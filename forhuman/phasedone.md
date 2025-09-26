Phase 3.1 setup complete—here’s what changed and how we verified it before moving on.

actions taken
T001 created the full repo scaffold (src, tests, scripts, docker, etc.) with package __init__.py files so upcoming modules import cleanly.
T002 authored pyproject.toml (Poetry application mode) pinning FastAPI, SQLAlchemy/pgvector, Celery, structlog, testing, and linting stacks plus shared tool configs.
T003 added .env.example covering API, database, Redis, logging, and feature flags.
T004 produced Docker assets (Dockerfile.api, Dockerfile.worker, docker-compose.yml) wiring the API, Celery worker, Postgres+pgvector, and Redis with health checks and migration profile.
T005 configured code quality tooling (ruff.toml, .pre-commit-config.yaml, Black/Isort/Ruff settings in pyproject.toml) for consistent formatting and linting.
T006 introduced main.py with a FastAPI app, health probe, and observability bootstrap.
T007 added database bootstrap artifacts (initialize.sql, alembic.ini, env.py, version folder) pointing migrations at our settings module.
T008 implemented structured logging helpers (logging.py) using structlog with context binding.
T009 wired observability basics (observability.py) for request IDs, response timing, and CORS.
T010 published a Makefile with install, lint, test, and Docker convenience targets.
T011 delivered a Pydantic settings loader (config.py) with feature flags and env overrides.
T012 documented the bootstrap process in setup.md.
Updated tasks.md, project-map.md, and tooling-registry.md to reflect new assets, and recorded the work in task-journal.md.