from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_preflight_allows_frontend_origin() -> None:
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code in (200, 204)
    assert response.headers["access-control-allow-origin"] == "*"


def test_chat_get_returns_usage_instead_of_405() -> None:
    response = client.get("/chat")

    assert response.status_code == 200
    assert "Use POST /chat" in response.json()["detail"]
