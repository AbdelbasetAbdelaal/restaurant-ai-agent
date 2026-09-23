.PHONY: help install dev test lint format migrate docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install      Install backend and frontend dependencies"
	@echo "  make dev          Start backend and frontend in development mode"
	@echo "  make test         Run backend tests"
	@echo "  make lint         Run backend and frontend linters"
	@echo "  make format       Format code using ruff and black"
	@echo "  make migrate      Run database migrations"
	@echo "  make docker-up    Build and start all containers via Docker Compose"
	@echo "  make docker-down  Stop and remove all containers"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	@echo "Run backend: cd backend && uvicorn app.main:app --reload --port 8000"
	@echo "Run frontend: cd frontend && npm run dev"

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

format:
	cd backend && ruff format .

migrate:
	cd backend && alembic upgrade head

docker-up:
	docker compose up --build

docker-down:
	docker compose down
