# Setup Guide

Follow these steps to bootstrap the Sales Assistant project locally.

## 1. Prerequisites

- Python 3.11
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker Desktop (for PostgreSQL + Redis)
- Git

Optional but recommended:
- `make`
- `pre-commit`

## 2. Clone and Install Dependencies

```bash
git clone <repo-url>
cd SALESASSISTANT
poetry install
```

To install pre-commit hooks:

```bash
poetry run pre-commit install
```

## 3. Configure Environment Variables

Copy the example environment file and adjust values as needed.

```bash
cp .env.example .env
```

At a minimum, update:

- `OPENAI_API_KEY`
- `API_KEY_SECRET`
- `JWT_SECRET`

## 4. Start Supporting Services

```bash
docker compose up db redis -d
```

Initialize the database schema:

```bash
poetry run alembic upgrade head
```

## 5. Run the API Locally

```bash
poetry run uvicorn src.app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

## 6. Run the Worker (Optional during development)

```bash
poetry run celery -A src.workers.knowledge_worker worker --loglevel=info
```

## 7. QA Workflow

- `make lint` to run static analysis
- `make test` to run the full pytest suite
- `make format` to apply formatting fixes

## 8. Dockerized Workflow

Build and run the complete stack:

```bash
docker compose up --build
```

Run database migrations inside Docker:

```bash
docker compose run --rm vectordb-migrate
```

## 9. Troubleshooting

- Ensure Docker Desktop is running before starting containers
- If Poetry reports missing dependencies, rerun `poetry install`
- Use `docker compose logs <service>` to inspect container logs
- Remove containers/volumes with `docker compose down -v` when resetting the environment
