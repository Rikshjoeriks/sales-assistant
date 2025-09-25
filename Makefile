POETRY ?= poetry
PYTHON ?= python

.PHONY: install dev-install lint format test test-unit test-integration fmt-check run api worker db-up db-down precommit

install:
	$(POETRY) install --without dev

dev-install:
	$(POETRY) install

lint:
	$(POETRY) run ruff check .

format:
	$(POETRY) run ruff check --fix .
	$(POETRY) run ruff format .
	$(POETRY) run isort .
	$(POETRY) run black .

fmt-check:
	$(POETRY) run ruff format --check .
	$(POETRY) run black --check .
	$(POETRY) run isort --check --diff .

precommit:
	$(POETRY) run pre-commit run --all-files

test:
	$(POETRY) run pytest

test-unit:
	$(POETRY) run pytest tests/unit

test-integration:
	$(POETRY) run pytest tests/integration

run:
	$(POETRY) run uvicorn src.app.main:app --reload

api:
	docker compose up api --build

worker:
	docker compose up worker --build

db-up:
	docker compose up db redis -d

db-down:
	docker compose down
