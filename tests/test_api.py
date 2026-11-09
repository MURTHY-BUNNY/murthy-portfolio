import os
import tempfile
from pathlib import Path

# Set database path before importing app.
temp_dir = tempfile.TemporaryDirectory()
os.environ["DATABASE_PATH"] = str(Path(temp_dir.name) / "test_portfolio.db")

from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


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


def test_contact_saved_to_postgres(monkeypatch):
    executed_sql = []

    class FakeCursor:
        def fetchone(self):
            return {"id": 42}

    class FakeConnection:
        def execute(self, query, parameters=None):
            executed_sql.append((query, parameters))
            return FakeCursor()

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(main, "USE_POSTGRES", True)
    monkeypatch.setattr(main, "get_connection", FakeConnection)

    response = client.post("/api/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Portfolio enquiry",
        "message": "Hello, this is a test message."
    })

    assert response.status_code == 201
    assert response.json()["id"] == 42
    assert "BIGSERIAL PRIMARY KEY" in executed_sql[0][0]
    assert "RETURNING id" in executed_sql[-1][0]
    assert "%s, %s, %s, %s, %s" in executed_sql[-1][0]
