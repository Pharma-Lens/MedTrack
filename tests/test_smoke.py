"""Smoke test — confirms the app boots and the dashboard endpoint responds."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard():
    response = client.get("/dashboard/facility-001/drug-001")
    assert response.status_code == 200
    body = response.json()
    assert "availability" in body
    assert "diversion" in body
