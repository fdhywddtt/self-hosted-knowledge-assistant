.PHONY: install migrate dev test lint docker-up docker-down

install:
	python -m venv .venv
	.venv/bin/pip install -e "backend[dev]"

migrate:
	cd backend && ../.venv/bin/alembic upgrade head

dev:
	.venv/bin/uvicorn app.main:app --app-dir backend --reload --port 8000

test:
	cd backend && ../.venv/bin/pytest

lint:
	cd backend && ../.venv/bin/ruff check app tests

docker-up:
	docker compose up --build

docker-down:
	docker compose down
