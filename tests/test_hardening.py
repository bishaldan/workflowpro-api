from app.core.config import settings
from app.core.rate_limit import rate_limiter


def test_login_rate_limit_returns_consistent_error(client):
    original_limit = settings.rate_limit_requests
    original_window = settings.rate_limit_window_seconds
    settings.rate_limit_requests = 1
    settings.rate_limit_window_seconds = 60
    rate_limiter.reset()
    try:
        first_response = client.post(
            "/api/v1/auth/login",
            json={"email": "missing@example.com", "password": "password123"},
        )
        second_response = client.post(
            "/api/v1/auth/login",
            json={"email": "missing@example.com", "password": "password123"},
        )
    finally:
        settings.rate_limit_requests = original_limit
        settings.rate_limit_window_seconds = original_window
        rate_limiter.reset()

    assert first_response.status_code == 401
    assert second_response.status_code == 429
    assert second_response.json()["error"]["code"] == "rate_limit_exceeded"
