import pytest


_test_user = {
    "email": "test@example.com",
    "password": "securepassword123",
    "display_name": "Test User",
}


def test_register_returns_token(client):
    resp = client.post("/auth/register", json=_test_user)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_correct_password_returns_token(client):
    # Register first
    client.post("/auth/register", json=_test_user)

    resp = client.post("/auth/login", json={
        "email": _test_user["email"],
        "password": _test_user["password"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    # Register first
    client.post("/auth/register", json=_test_user)

    resp = client.post("/auth/login", json={
        "email": _test_user["email"],
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_me_without_token_returns_401(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token_returns_user_info(client):
    # Register and get token
    reg_resp = client.post("/auth/register", json=_test_user)
    token = reg_resp.json()["access_token"]

    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == _test_user["email"]
    assert data["display_name"] == _test_user["display_name"]
    assert "id" in data
