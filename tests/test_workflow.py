def auth_headers(client, email="owner@example.com", name="Owner User"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": name,
            "password": "strong-password",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "strong-password"},
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
        f"/api/v1/organizations/{organization_id}/tasks?priority=high&search=kickoff",
        headers=headers,
    )
    assert tasks_response.status_code == 200
    assert len(tasks_response.json()) == 1

    analytics_response = client.get(
        f"/api/v1/organizations/{organization_id}/analytics",
        headers=headers,
    )
    assert analytics_response.status_code == 200
    assert analytics_response.json()["tasks_total"] == 1
    assert analytics_response.json()["tasks_by_priority"]["high"] == 1

    activity_response = client.get(
        f"/api/v1/organizations/{organization_id}/activity",
        headers=headers,
    )
    assert activity_response.status_code == 200
    actions = {item["action"] for item in activity_response.json()}
    assert {"organization.created", "project.created", "task.created"}.issubset(actions)


def test_authenticated_user_can_read_profile(client):
    headers = auth_headers(client)

    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"


def test_owner_can_invite_member_and_member_can_accept(client):
    owner_headers = auth_headers(client)
    member_headers = auth_headers(client, email="member@example.com", name="Member User")

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "Nimbus Labs", "slug": "nimbus-labs"},
        headers=owner_headers,
    )
    organization_id = org_response.json()["id"]

    invitation_response = client.post(
        f"/api/v1/organizations/{organization_id}/invitations",
        json={"email": "member@example.com", "role": "member"},
        headers=owner_headers,
    )
    assert invitation_response.status_code == 201
    invitation_id = invitation_response.json()["id"]

    accept_response = client.post(
        f"/api/v1/organizations/{organization_id}/invitations/{invitation_id}/accept",
        headers=member_headers,
    )
    assert accept_response.status_code == 200
    assert accept_response.json()["role"] == "member"

    members_response = client.get(
        f"/api/v1/organizations/{organization_id}/members",
        headers=owner_headers,
    )
    assert members_response.status_code == 200
    assert len(members_response.json()) == 2


def test_viewer_cannot_create_project(client):
    owner_headers = auth_headers(client)
    viewer_headers = auth_headers(client, email="viewer@example.com", name="Viewer User")

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "Read Only Co", "slug": "read-only-co"},
        headers=owner_headers,
    )
    organization_id = org_response.json()["id"]
    invitation_response = client.post(
        f"/api/v1/organizations/{organization_id}/invitations",
        json={"email": "viewer@example.com", "role": "viewer"},
        headers=owner_headers,
    )
    invitation_id = invitation_response.json()["id"]
    client.post(
        f"/api/v1/organizations/{organization_id}/invitations/{invitation_id}/accept",
        headers=viewer_headers,
    )

    project_response = client.post(
        f"/api/v1/organizations/{organization_id}/projects",
        json={"name": "Restricted Project"},
        headers=viewer_headers,
    )
    assert project_response.status_code == 403


def test_task_assignment_creates_notification(client):
    owner_headers = auth_headers(client)
    member_headers = auth_headers(client, email="assignee@example.com", name="Assignee User")

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "Notify Co", "slug": "notify-co"},
        headers=owner_headers,
    )
    organization_id = org_response.json()["id"]
    invitation_response = client.post(
        f"/api/v1/organizations/{organization_id}/invitations",
        json={"email": "assignee@example.com", "role": "member"},
        headers=owner_headers,
    )
    invitation_id = invitation_response.json()["id"]
    accept_response = client.post(
        f"/api/v1/organizations/{organization_id}/invitations/{invitation_id}/accept",
        headers=member_headers,
    )
    assignee_id = accept_response.json()["user_id"]

    project_response = client.post(
        f"/api/v1/organizations/{organization_id}/projects",
        json={"name": "Notification Project"},
        headers=owner_headers,
    )
    project_id = project_response.json()["id"]
    task_response = client.post(
        f"/api/v1/organizations/{organization_id}/tasks",
        json={
            "project_id": project_id,
            "title": "Review assigned task",
            "assignee_id": assignee_id,
        },
        headers=owner_headers,
    )
    assert task_response.status_code == 201

    notifications_response = client.get(
        f"/api/v1/organizations/{organization_id}/notifications",
        headers=member_headers,
    )
    assert notifications_response.status_code == 200
    assert notifications_response.json()[0]["type"] == "task_assigned"


def test_project_export_generates_csv_and_notification(client):
    headers = auth_headers(client)
    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "Export Co", "slug": "export-co"},
        headers=headers,
    )
    organization_id = org_response.json()["id"]
    project_response = client.post(
        f"/api/v1/organizations/{organization_id}/projects",
        json={"name": "Reporting Project"},
        headers=headers,
    )
    project_id = project_response.json()["id"]
    client.post(
        f"/api/v1/organizations/{organization_id}/tasks",
        json={"project_id": project_id, "title": "Export this task", "priority": "urgent"},
        headers=headers,
    )

    export_response = client.post(
        f"/api/v1/organizations/{organization_id}/exports",
        json={"project_id": project_id},
        headers=headers,
    )
    assert export_response.status_code == 201
    assert export_response.json()["status"] == "completed"
    export_id = export_response.json()["id"]

    download_response = client.get(
        f"/api/v1/organizations/{organization_id}/exports/{export_id}/download",
        headers=headers,
    )
    assert download_response.status_code == 200
    assert "Export this task" in download_response.text
    assert "text/csv" in download_response.headers["content-type"]

    notifications_response = client.get(
        f"/api/v1/organizations/{organization_id}/notifications",
        headers=headers,
    )
    assert notifications_response.status_code == 200
    assert notifications_response.json()[0]["type"] == "export_completed"
