import os
import tempfile
from pathlib import Path

# Set database path before importing app.
temp_dir = tempfile.TemporaryDirectory()
os.environ["DATABASE_PATH"] = str(Path(temp_dir.name) / "test_portfolio.db")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_contact_saved():
    response = client.post("/api/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Portfolio enquiry",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 201
    assert response.json()["success"] is True


def test_invalid_email_rejected():
    response = client.post("/api/contact", json={
        "name": "Test User",
        "email": "not-an-email",
        "subject": "Hello",
        "message": "This is a test message."
    })
    assert response.status_code == 422
