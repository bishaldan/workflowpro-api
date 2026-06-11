# WorkFlowPro API

Production-style multi-tenant FastAPI SaaS backend for project and task management.

This project is built as a senior Python backend portfolio project. It demonstrates API design, JWT authentication, organization-level tenancy, role-based access control, SQLAlchemy models, Alembic migrations, Docker Compose infrastructure, Celery-ready background jobs, and automated tests.

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Celery
- Redis
- Docker Compose
- Pytest
- GitHub Actions
- Structured request logging
- Request ID middleware
- Consistent error responses
- Lightweight rate limiting

## Current Features

- Health check API
- User registration and login
- JWT access tokens
- Password hashing
- Organization creation
- Organization membership with roles
- Organization invitations and acceptance flow
- Project CRUD scoped by organization
- Task CRUD scoped by organization and project
- Pagination, search, and task filters
- Basic role-based write protection
- Activity log API
- Organization analytics API
- Database-backed notification records
- Project CSV export jobs with download endpoint
- Celery task modules for exports and overdue task summaries
- Request ID response headers
- Consistent validation/error response format
- In-memory rate limiter for login and write endpoints
- Demo seed data script
- Test suite using FastAPI TestClient

## Architecture

```text
Client / Swagger UI
        |
        v
FastAPI application
        |
        +-- Auth / JWT / RBAC
        +-- Organization tenancy
        +-- Project and task APIs
        +-- Activity, analytics, notifications
        +-- CSV export workflow
        |
        v
SQLAlchemy models + Alembic migrations
        |
        +-- PostgreSQL in Docker
        +-- Redis-backed Celery worker modules
```

## Local Setup

```bash
cp .env.example .env
docker compose up --build
```

API docs:

```text
http://localhost:8000/docs
```

Run tests locally:

```bash
pip install -e ".[dev]"
pytest
```

Seed demo data:

```bash
python scripts/seed_demo.py
```

Demo credentials:

```text
owner@example.com / password123
member@example.com / password123
viewer@example.com / password123
```

API examples are available in [docs/api-examples.md](docs/api-examples.md).

## API Overview

```text
GET  /api/v1/health
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/users/me
POST /api/v1/organizations
GET  /api/v1/organizations
GET  /api/v1/organizations/{organization_id}/members
POST /api/v1/organizations/{organization_id}/invitations
POST /api/v1/organizations/{organization_id}/invitations/{invitation_id}/accept
POST /api/v1/organizations/{organization_id}/projects
GET  /api/v1/organizations/{organization_id}/projects
POST /api/v1/organizations/{organization_id}/tasks
GET  /api/v1/organizations/{organization_id}/tasks
GET  /api/v1/organizations/{organization_id}/activity
GET  /api/v1/organizations/{organization_id}/analytics
GET  /api/v1/organizations/{organization_id}/notifications
POST /api/v1/organizations/{organization_id}/exports
GET  /api/v1/organizations/{organization_id}/exports/{export_id}
GET  /api/v1/organizations/{organization_id}/exports/{export_id}/download
```

## Error Shape

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "request_id": "4ec26bf1-9f21-4ed7-bd2f-28a6b8df68c4",
    "details": []
  }
}
```

## Portfolio Positioning

CV summary:

> Built a production-style multi-tenant FastAPI backend with JWT authentication, RBAC, organization invitations, project/task APIs, filtering, activity logs, analytics, database-backed notifications, Celery/Redis job modules, CSV export workflows, structured request logging, request IDs, rate limiting, PostgreSQL migrations, Docker infrastructure, automated tests, and GitHub Actions CI.
