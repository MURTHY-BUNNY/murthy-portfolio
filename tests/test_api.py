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
    assert response.json()["email_sent"] is False
    assert "message was saved" in response.json()["message"]


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


def test_email_notification_sent(monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            sent["connection"] = (host, port, timeout)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def starttls(self, context):
            sent["tls"] = context

        def login(self, username, password):
            sent["login"] = (username, password)

        def send_message(self, message):
            sent["message"] = message

    monkeypatch.setenv("SMTP_USERNAME", "brevo-login")
    monkeypatch.setenv("SMTP_PASSWORD", "test-smtp-key")
    monkeypatch.setenv("MAIL_FROM", "verified@example.com")
    monkeypatch.setenv("MAIL_TO", "owner@example.com")
    monkeypatch.setattr(main.smtplib, "SMTP", FakeSMTP)

    payload = main.ContactMessage(
        name="Test User",
        email="visitor@example.com",
        subject="Portfolio enquiry",
        message="Hello, this is a test message.",
    )
    assert main.send_contact_notification(payload, 17) is True

    message = sent["message"]
    assert sent["connection"] == ("smtp-relay.brevo.com", 587, 15)
    assert sent["login"] == ("brevo-login", "test-smtp-key")
    assert message["To"] == "owner@example.com"
    assert message["Reply-To"] == "visitor@example.com"
    assert "Portfolio enquiry" in message.get_content()
    assert "Hello, this is a test message." in message.get_content()


def test_email_notification_requires_configuration(monkeypatch):
    for key in ("SMTP_USERNAME", "SMTP_PASSWORD", "MAIL_FROM", "MAIL_TO"):
        monkeypatch.delenv(key, raising=False)

    payload = main.ContactMessage(
        name="Test User",
        email="visitor@example.com",
        subject="Portfolio enquiry",
        message="Hello, this is a test message.",
    )
    assert main.send_contact_notification(payload, 18) is False
