def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_request_id_header_is_returned(client):
    response = client.get("/api/v1/health", headers={"X-Request-ID": "test-request-id"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-id"


def test_validation_errors_use_consistent_shape(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "bad-email", "full_name": "A", "password": "short"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["request_id"]
