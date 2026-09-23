# Architecture Design Document

## 1. Overview

**Restaurant AI Agent** is a multi-tenant SaaS platform designed to automate restaurant ordering via conversational channels (such as WhatsApp) powered by autonomous agents.

> [!IMPORTANT]
> **Phase 1 Boundary**: Only the architectural foundation, infrastructure, health checks, AI provider abstractions, and database/cache clients are implemented. Conversational logic, WhatsApp integration, menu/cart/order processing, and external LLM API calls are intentionally omitted until subsequent phases.

---

## 2. High-Level Architecture Diagram

```
┌────────────────────────────────────────────────────────┐
│                   Next.js Web Client                   │
│              (Status Dashboard / Future UI)            │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / REST
                            ▼
┌────────────────────────────────────────────────────────┐
│                     FastAPI App                        │
│                                                        │
│  ┌──────────────────┐          ┌────────────────────┐  │
│  │   /api/v1/health │          │ Structured Logger  │  │
│  └────────┬─────────┘          │ (Correlation ID)   │  │
│           │                    └────────────────────┘  │
│           │                                            │
│  ┌────────┴─────────┐          ┌────────────────────┐  │
│  │ DB & Cache Layer │          │ AI Provider Router │  │
│  │ (Postgres/Redis) │          │ (OpenAI/Groq/HF)   │  │
│  └────────┬─────────┘          └─────────┬──────────┘  │
└───────────┼──────────────────────────────┼─────────────┘
            │                              │
     ┌──────┴──────┐                ┌──────┴──────────────┐
     │             │                │ Abstract Interface  │
     ▼             ▼                ▼                     ▼
┌──────────┐ ┌───────────┐   ┌────────────┐        ┌─────────────┐
│PostgreSQL│ │   Redis   │   │   OpenAI   │        │    Groq     │
│ Database │ │Cache/State│   │(Stub/Mock) │        │ (Stub/Mock) │
└──────────┘ └───────────┘   └────────────┘        └─────────────┘
```

---

## 3. Backend Architecture

### 3.1 Layered Architecture
* **`api/`**: API route definitions, request validation, response serialization, and versioning (`/api/v1/`). Zero direct business or database logic.
* **`core/`**: Configuration via `pydantic-settings`, structured logging, request ID correlation middleware, and uniform error handlers.
* **`db/`**: SQLAlchemy 2.0 asynchronous engine, session factory, base model declarations, and connection health routines.
* **`models/`**: Declarative models. Base model provides `id`, `created_at`, `updated_at`, and a `TenantMixin` (`restaurant_id`) for multi-tenant readiness.
* **`schemas/`**: Pydantic schemas for data validation and API response formatting.
* **`services/`**: Infrastructure and domain services, including the `RedisService` wrapper.
* **`agents/`**: AI provider abstraction (`AIProvider`, `AIRouter`) and tool abstraction framework.

---

## 4. Multi-Tenant Preparedness

To support future SaaS operation across multiple restaurant tenants:
- All domain tables in future phases will inherit from `TenantMixin` or include `restaurant_id`.
- Foreign keys and database queries will enforce tenant scoping.
- The AI Provider router allows per-tenant or global model configuration without refactoring business logic.

---

## 5. Security & Error Handling

- **Error Format**: Uniform error payload:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human readable message",
      "request_id": "...",
      "details": []
    }
  }
  ```
- **Secrets Management**: Loaded exclusively through environment variables (`.env`). No secrets or API credentials committed to version control.
- **Trace Sanitization**: In non-debug production mode, internal stack traces are redacted.
