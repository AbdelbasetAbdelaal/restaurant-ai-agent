# Development Guide

This guide details how to set up, run, test, and contribute to the **Restaurant AI Agent** repository.

---

## 1. Prerequisites

- Python 3.12+ (tested with 3.12 - 3.14)
- Node.js 18+ & npm
- Docker and Docker Compose (optional for local mock testing, required for full containerized stack)

---

## 2. Environment Setup

Copy `.env.example` to `.env` in the repository root:

```bash
cp .env.example .env
```

Ensure variables match your local environment.

---

## 3. Local Development (Without Docker)

### 3.1 Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run backend development server
cd backend
uvicorn app.main:app --reload --port 8000
```

### 3.2 Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the system status dashboard.

---

## 4. Running with Docker Compose

To start the complete stack (PostgreSQL, Redis, Backend, Frontend):

```bash
docker compose up --build
```

- Frontend status page: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Health Check: `http://localhost:8000/api/v1/health`
- OpenAPI Swagger Docs: `http://localhost:8000/docs`

To shut down containers and tear down networks:
```bash
docker compose down
```

---

## 5. Running Tests & Quality Checks

### 5.1 Backend Tests
```bash
cd backend
pytest -v
```

### 5.2 Linting & Formatting
```bash
# Lint backend
ruff check backend/

# Format backend
ruff format backend/

# Lint frontend
cd frontend
npm run lint
```

### 5.3 Frontend Build Validation
```bash
cd frontend
npm run build
```

---

## 6. Database Migrations (Alembic)

When models are added in future phases:
```bash
cd backend
# Generate migration
alembic revision --autogenerate -m "create new tables"

# Apply migration
alembic upgrade head
```
