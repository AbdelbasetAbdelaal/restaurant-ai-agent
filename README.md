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

## Quick Start with Docker

```bash
# 1. Clone repository & configure environment
cp .env.example .env

# 2. Start full stack (PostgreSQL, Redis, Backend, Frontend)
docker compose up --build
```

- **Frontend System Status**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## Local Development (Without Docker)

### Backend
```bash
# Set up Python virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
# or: source venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r backend/requirements.txt

# Run backend API
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Testing & Quality Assurance

```bash
# Backend pytest suite
cd backend
pytest -v

# Backend code formatting & linting
ruff check backend/
ruff format backend/

# Frontend build verification
cd frontend
npm run build
```

---

## Documentation

- [Architecture Design](docs/architecture.md)
- [Development Guide](docs/development.md)
- [Phase 1 Scope & Boundary](docs/phase-1.md)
