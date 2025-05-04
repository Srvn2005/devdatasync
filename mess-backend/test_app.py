import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_menu():
    response = client.get("/menu")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_login_failure():
    response = client.post(
        "/token",
        data={"username": "invaliduser", "password": "invalidpassword"}
    )
    assert response.status_code == 401