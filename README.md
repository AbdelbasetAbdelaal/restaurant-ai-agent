# Restaurant AI Agent (Phase 1: Foundation)

A production-oriented SaaS platform engineered to enable restaurant patrons to place orders via conversational channels powered by an AI agent.

> [!NOTE]
> **Current Status**: **Phase 1: Foundation** is complete.
> WhatsApp integration, AI agent conversational execution, menu management, cart logic, orders, and payment processing are deliberately reserved for subsequent phases.

---

## Architecture Overview

```text
restaurant-ai-agent/
├── backend/            # FastAPI, SQLAlchemy 2.x, Pydantic, Alembic, AI Provider Abstractions
├── frontend/           # Next.js, React, TypeScript, Tailwind CSS
├── database/           # Alembic migrations
├── docs/               # Architecture, development, and phase documentation
├── .github/workflows/  # CI pipeline (Linting, Tests, Build)
├── docker-compose.yml  # PostgreSQL, Redis, Backend, Frontend orchestration
├── Makefile            # Standard development automation tasks
└── .env.example        # Reference environment variables
```

---

## Windows Quick Start (Local Development - No Docker Needed)

### 1. Configure Environment
In Windows Command Prompt (`cmd.exe`):
```cmd
copy .env.example .env
```
*(Or in PowerShell: `Copy-Item .env.example .env`)*

### 2. Start Backend (Terminal 1)
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 3. Start Frontend (Terminal 2)
```cmd
cd frontend
npm install
npm run dev
```
- **System Status Dashboard**: [http://localhost:3000](http://localhost:3000)

> [!TIP]
> In local development mode without Docker, the backend and frontend run smoothly. The health dashboard accurately reflects that the Backend is `Connected`, while PostgreSQL and Redis are reported as `Offline` with an overall `degraded` readiness status.

---

## Docker Quick Start (Full Infrastructure Mode)

For full stack execution (PostgreSQL 16 + Redis 7 + Backend + Frontend):

```bash
# 1. Create environment
cp .env.example .env

# 2. Build and run containers
docker compose up --build
```

---

## Health Check Semantics & Performance

Subsystem health checks execute **concurrently** via `asyncio.gather()`, ensuring that `/api/v1/health` responds in ~2s (the longest single timeout) rather than waiting sequentially.

| Status | Meaning |
| :--- | :--- |
| **`ok`** | Backend is operational and all dependencies (PostgreSQL, Redis) are `Connected`. |
| **`degraded`** | Backend is operational, but one or both infrastructure dependencies are `Offline`. |
| **`down`** | Backend service itself cannot process requests. |

---

## Testing & Quality Assurance

```cmd
# Run backend pytest suite (32 tests)
.venv\Scripts\pytest -v backend/tests

# Code linting and formatting checks
.venv\Scripts\ruff check backend
.venv\Scripts\ruff format --check backend

# Frontend build verification
cd frontend
npm run build
```

---

## Documentation

- [Architecture Design](docs/architecture.md)
- [Development Guide (Windows & Docker)](docs/development.md)
- [Phase 1 Scope & Boundary](docs/phase-1.md)
