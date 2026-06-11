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
- Test suite using FastAPI TestClient

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

## Portfolio Positioning

CV summary:

> Built a production-style multi-tenant FastAPI backend with JWT authentication, role-based access control, organization invitations, project/task APIs, filtering, activity logs, analytics, database-backed notifications, Celery/Redis background-job modules, CSV export jobs, PostgreSQL migrations, Docker Compose infrastructure, and automated Pytest/GitHub Actions CI.
