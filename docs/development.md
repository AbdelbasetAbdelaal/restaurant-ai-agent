# Development Guide

This guide details how to set up, run, test, and contribute to the **Restaurant AI Agent** repository.

---

## 1. Prerequisites

- **Python**: 3.12+ (tested with Python 3.12, 3.13, 3.14)
- **Node.js**: 18+ (tested with Node.js 20 and 24) & npm
- **Docker & Docker Compose**: Optional for local development; required for full containerized stack.

---

## 2. Supported Development Modes

The architecture explicitly supports two development modes:

### Mode A: Full Infrastructure Mode (Production-aligned)
- **Stack**: PostgreSQL 16 + Redis 7 + FastAPI Backend + Next.js Frontend.
- **When to use**: End-to-end integration testing, database migrations verification, or production builds.
- **Run via**: Docker Compose (`docker compose up --build`) or local native PostgreSQL and Redis instances.
- **Health status**: All components report `Connected`, overall status is `ok`.

### Mode B: Backend / Frontend Local Development Mode (No Docker Required)
- **Stack**: FastAPI Backend + Next.js Frontend.
- **When to use**: Rapid local development on Windows or systems where Docker is unavailable.
- **Resilience**: The backend and frontend start cleanly without crashing when PostgreSQL and Redis are absent.
- **Health status**:
  - Backend: `Connected`
  - Database: `Offline` (connection timed out)
  - Redis: `Offline` (connection timed out)
  - Overall status: `degraded` (Backend is operational, but persistence/caching dependencies are offline)

---

## 3. Environment Setup

Copy `.env.example` to `.env` in the repository root.

### On Windows (Command Prompt - cmd.exe)
```cmd
copy .env.example .env
```

### On Windows (PowerShell)
```powershell
Copy-Item .env.example .env
```

### On Linux / macOS
```bash
cp .env.example .env
```

> [!IMPORTANT]
> `.env` is ignored by Git and must never be committed. `.env.example` contains safe local-development defaults targeting `localhost:5432` and `localhost:6379`. Docker Compose automatically passes internal service hostnames (`postgres` and `redis`) through environment variables.

---

## 4. Running Locally on Windows (Without Docker)

### 4.1 Backend Setup (Terminal 1)

In Windows Command Prompt (`cmd.exe`):
```cmd
REM 1. Create Python virtual environment (if not already created)
python -m venv .venv

REM 2. Activate virtual environment
.venv\Scripts\activate

REM 3. Install backend dependencies
pip install -r backend/requirements.txt

REM 4. Start FastAPI server with live reload
.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

Or in PowerShell:
```powershell
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 4.2 Frontend Setup (Terminal 2)

In a separate Command Prompt or PowerShell window:
```cmd
cd frontend
npm install
npm run dev
```

- **Frontend Status Dashboard**: [http://localhost:3000](http://localhost:3000)

---

## 5. Running with Docker Compose (Mode A)

To run the complete containerized stack:

```bash
docker compose up --build
```

To stop containers:
```bash
docker compose down
```

---

## 6. Health Check Semantics & Performance

The health check endpoints (`/health`, `/api/health`, `/api/v1/health`) execute subsystem checks **concurrently** using `asyncio.gather()` with individual timeouts (2.0s).

### Concurrency Target
When both PostgreSQL and Redis are offline, the health check returns in approximately the duration of the longest single timeout (~2s), rather than waiting sequentially (~4s).

### Status Policy
| State | Backend | Database | Redis | Overall Status |
| :--- | :--- | :--- | :--- | :--- |
| **All Operational** | `Connected` | `Connected` | `Connected` | `ok` |
| **Partial Outage** | `Connected` | `Connected` | `Offline` | `degraded` |
| **Partial Outage** | `Connected` | `Offline` | `Connected` | `degraded` |
| **Local Mode (No DB/Cache)** | `Connected` | `Offline` | `Offline` | `degraded` |
| **Fatal Backend Crash** | `Offline` | N/A | N/A | `down` / Unreachable |

---

## 7. Running Quality Checks & Tests

### 7.1 Backend Tests (pytest)
Runs 32 automated tests covering configuration, health concurrency, semantic statuses, database models, Redis service, error handling, and AI providers:
```cmd
.venv\Scripts\pytest -v backend/tests
```

### 7.2 Code Linting & Formatting (Ruff)
```cmd
.venv\Scripts\ruff check backend
.venv\Scripts\ruff format --check backend
```

To auto-format code:
```cmd
.venv\Scripts\ruff format backend
```

### 7.3 Frontend Production Build Validation
```cmd
cd frontend
npm run build
```

---

## 8. Optional Real Integration Verification

When native PostgreSQL and Redis servers are installed locally:
1. Start PostgreSQL on port `5432` with database `restaurant_db` and user `restaurant_user`.
2. Start Redis on port `6379`.
3. Start the backend: `.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload --port 8000`.
4. Run `curl http://localhost:8000/api/v1/health` (or open in browser).
5. Verify that `database` and `redis` report `"status": "Connected"`, and overall status switches to `"ok"`.
