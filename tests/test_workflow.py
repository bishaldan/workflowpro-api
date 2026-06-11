def auth_headers(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@example.com",
            "full_name": "Owner User",
            "password": "strong-password",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "strong-password"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_can_create_org_project_and_task(client):
    headers = auth_headers(client)

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "Acme Operations", "slug": "acme-ops"},
        headers=headers,
    )
    assert org_response.status_code == 201
    organization_id = org_response.json()["id"]

    project_response = client.post(
        f"/api/v1/organizations/{organization_id}/projects",
        json={"name": "Client Onboarding", "description": "Standard onboarding workflow"},
        headers=headers,
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    task_response = client.post(
        f"/api/v1/organizations/{organization_id}/tasks",
        json={
            "project_id": project_id,
            "title": "Prepare kickoff checklist",
            "priority": "high",
        },
        headers=headers,
    )
    assert task_response.status_code == 201
    assert task_response.json()["title"] == "Prepare kickoff checklist"

    tasks_response = client.get(
        f"/api/v1/organizations/{organization_id}/tasks",
        headers=headers,
    )
    assert tasks_response.status_code == 200
    assert len(tasks_response.json()) == 1


def test_authenticated_user_can_read_profile(client):
    headers = auth_headers(client)

    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"

