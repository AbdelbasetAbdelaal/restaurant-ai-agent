# Phase 1: Foundation Specification & Scope

## 1. Objectives

The primary goal of Phase 1 is to construct a resilient, cleanly architected foundation for the **Restaurant AI Agent** platform.

This phase deliberately isolates infrastructural prerequisites from complex business domains.

---

## 2. Completed Scope (Phase 1)

1. **Backend Infrastructure**:
   - FastAPI application configured with modular architecture.
   - Pydantic Settings (`BaseSettings`) loading validated environment configurations.
   - Structured JSON logging with request correlation IDs via `X-Request-ID`.
   - Global exception handling returning unified JSON error envelopes.
   - Root `/health`, versioned `/api/v1/health`, and `/api/health` endpoints.
   - CORS middleware configured for cross-origin frontend communication.

2. **Database & Cache Abstractions**:
   - SQLAlchemy 2.0 async engine and session management.
   - Base declarative model with timestamps and `restaurant_id` tenancy mixin.
   - Database connection health checking routine.
   - Alembic configuration with async migration environment.
   - Async `RedisService` wrapper with ping/health check verification.

3. **AI Provider Abstraction Framework**:
   - `AIProvider` protocol / abstract base class defining vendor-agnostic LLM contract.
   - Provider stubs: `OpenAIProvider`, `GroqProvider`, `HuggingFaceProvider`.
   - Dynamic `AIRouter` provider factory preventing business logic coupling to any single vendor.
   - Future AI tools directory and base interface definition (`backend/app/agents/tools/`).

4. **Frontend Foundation**:
   - Next.js App Router application in TypeScript and Tailwind CSS.
   - Centralized, typed API client abstraction (`lib/api-client.ts`).
   - Clean application shell with Error Boundary and loading indicators.
   - System Status dashboard displaying live health metrics for Backend, PostgreSQL, and Redis.

5. **DevOps & Testing**:
   - Containerized deployment via `docker-compose.yml` (backend, frontend, postgres, redis).
   - Automated pytest test suite verifying configuration, health endpoints, database resilience, Redis fallback, error formatting, and AI provider interfaces.
   - GitHub Actions CI workflow executing backend lint/tests and frontend production builds.

---

## 3. Explicit Non-Goals (Omitted from Phase 1)

> [!CAUTION]
> The following items are explicitly **NOT** implemented in Phase 1 and are reserved for Phase 2 and later:
> - WhatsApp Cloud API / Webhook handlers
> - Real external AI/LLM API calls or API keys
> - Autonomous ordering conversations or prompt engineering
> - Menu catalog, items, categories, or modifiers
> - Cart creation, item additions, or total calculations
> - Order fulfillment, kitchen screens, delivery tracking, or payments
> - Customer authentication, user management, or billing
