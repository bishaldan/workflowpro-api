# API Examples

Set the base URL:

```bash
BASE_URL=http://localhost:8000/api/v1
```

## Register And Login

```bash
curl -sS -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@example.com","full_name":"Owner User","password":"password123"}'
```

```bash
TOKEN=$(curl -sS -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@example.com","password":"password123"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
```

## Create Organization

```bash
curl -sS -X POST "$BASE_URL/organizations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Operations","slug":"acme-operations"}'
```

## Create Project

```bash
curl -sS -X POST "$BASE_URL/organizations/1/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Client Onboarding","description":"Standard onboarding workflow"}'
```

## Create Task

```bash
curl -sS -X POST "$BASE_URL/organizations/1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"title":"Prepare kickoff checklist","priority":"high"}'
```

## Filter Tasks

```bash
curl -sS "$BASE_URL/organizations/1/tasks?priority=high&search=kickoff" \
  -H "Authorization: Bearer $TOKEN"
```

## Request CSV Export

```bash
curl -sS -X POST "$BASE_URL/organizations/1/exports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id":1}'
```

## Download CSV Export

```bash
curl -sS "$BASE_URL/organizations/1/exports/1/download" \
  -H "Authorization: Bearer $TOKEN"
```

