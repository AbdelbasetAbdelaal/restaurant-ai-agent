# Restaurant AI Agent (Phase 2: Database & Restaurant Foundation)

A production-oriented SaaS platform engineered to enable restaurant patrons to place orders via conversational channels powered by an AI agent.

> [!NOTE]
> **Current Status**: **Phase 2: Database & Restaurant Foundation** is complete.
> PostgreSQL multi-tenant database models (`Restaurant`, `RestaurantSettings`, `Customer`, `Staff`), Alembic migrations, tenant isolation policies, and full REST CRUD endpoints are active.
> WhatsApp integration, AI agent conversational execution, menu management, cart logic, orders, and payment processing are deliberately reserved for subsequent phases.

---

## Architecture Overview

```text
restaurant-ai-agent/
├── backend/            # FastAPI, SQLAlchemy 2.x, Pydantic, Alembic, Multi-Tenant Services
├── frontend/           # Next.js, React, TypeScript, Tailwind CSS
├── database/           # Alembic migrations (PostgreSQL DDL)
├── docs/               # Architecture, development, Phase 1 & 2 documentation
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
- **Tenant Foundation Dashboard**: [http://localhost:3000](http://localhost:3000)

> [!TIP]
> In local development mode without Docker, the backend and frontend run smoothly without crashing. The health dashboard accurately reflects that the Backend is `Connected`, while PostgreSQL and Redis are reported as `Offline` with an overall `degraded` readiness status, and the Foundation view gracefully displays database offline guidance.

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

## Phase 2 REST API Endpoints

| Resource | Method | Path | Description |
| :--- | :--- | :--- | :--- |
| **Restaurants** | `POST` | `/api/v1/restaurants` | Onboard restaurant with auto default settings |
| | `GET` | `/api/v1/restaurants` | List restaurants (paginated) |
| | `GET` | `/api/v1/restaurants/{id}` | Get restaurant by UUID |
| | `PATCH` | `/api/v1/restaurants/{id}` | Update restaurant profile |
| **Settings** | `GET` | `/api/v1/restaurants/{id}/settings` | Get restaurant operational settings |
| | `PATCH` | `/api/v1/restaurants/{id}/settings` | Update operational settings |
| **Customers** | `POST` | `/api/v1/restaurants/{id}/customers` | Register customer (scoped unique phone) |
| | `GET` | `/api/v1/restaurants/{id}/customers` | List tenant customers |
| | `GET` | `/api/v1/restaurants/{id}/customers/{customer_id}` | Get customer (strict tenant isolation) |
| | `PATCH` | `/api/v1/restaurants/{id}/customers/{customer_id}` | Update customer profile |
| **Staff** | `POST` | `/api/v1/restaurants/{id}/staff` | Add staff (`OWNER`, `MANAGER`, `STAFF`) |
| | `GET` | `/api/v1/restaurants/{id}/staff` | List tenant staff members |
| | `GET` | `/api/v1/restaurants/{id}/staff/{staff_id}` | Get staff member (tenant isolation) |
| | `PATCH` | `/api/v1/restaurants/{id}/staff/{staff_id}` | Update staff member |

---

## Testing & Quality Assurance

```cmd
# Run backend pytest suite (65 tests)
cd backend
..\.venv\Scripts\pytest -v

# Code linting and formatting checks
..\.venv\Scripts\ruff check .
..\.venv\Scripts\ruff format --check .

# Frontend build verification
cd ../frontend
npm run build
```

---

## Documentation

- [Architecture Design](docs/architecture.md)
- [Development Guide (Windows & Docker)](docs/development.md)
- [Phase 1 Foundation Scope](docs/phase-1.md)
- [Phase 2 Database & Restaurant Foundation Report](docs/phase-2.md)
