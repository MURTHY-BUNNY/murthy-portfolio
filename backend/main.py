"""
Murthy Portfolio Backend
FastAPI + SQLite/PostgreSQL contact form API.
Run from this folder: uvicorn main:app --reload
"""
import os
import logging
import smtplib
import sqlite3
import ssl
from contextlib import closing
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from pydantic import BaseModel, EmailStr, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DB_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "portfolio.db")))
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = bool(DATABASE_URL)
DATABASE_ERRORS = (sqlite3.Error, psycopg.Error)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Murthy Portfolio API",
    description="Backend API for the Murthy portfolio contact form.",
    version="1.0.0",
)

DEFAULT_ORIGINS = (
    "http://localhost:5500,"
    "http://127.0.0.1:5500,"
    "http://localhost:3000,"
    "http://localhost:5173,"
    "https://murthy-bunny.github.io"
)
allowed_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", DEFAULT_ORIGINS).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


def get_connection():
    if USE_POSTGRES:
        return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=10)

    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    if not USE_POSTGRES:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with closing(get_connection()) as conn:
        id_type = (
            "BIGSERIAL PRIMARY KEY"
            if USE_POSTGRES
            else "INTEGER PRIMARY KEY AUTOINCREMENT"
        )
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id {id_type},
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def send_contact_notification(payload: "ContactMessage", message_id: int) -> bool:
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("MAIL_FROM")
    recipient = os.getenv("MAIL_TO", "kothagundlamurthy@gmail.com")

    if not all((smtp_username, smtp_password, sender, recipient)):
        logger.warning("Contact message %s saved, but email is not configured.", message_id)
        return False

    try:
        smtp_host = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        email = EmailMessage()
        email["Subject"] = f"New portfolio message #{message_id}"
        email["From"] = sender
        email["To"] = recipient
        email["Reply-To"] = str(payload.email)
        email.set_content(
            "\n".join(
                (
                    f"Name: {payload.name}",
                    f"Email: {payload.email}",
                    f"Subject: {payload.subject}",
                    "",
                    payload.message,
                )
            )
        )

        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(email)
    except (OSError, smtplib.SMTPException, ValueError):
        logger.exception("Email notification failed for contact message %s.", message_id)
        return False

    return True


@app.on_event("startup")
def on_startup():
    initialize_database()


class ContactMessage(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(min_length=2, max_length=150)
    message: str = Field(min_length=10, max_length=5000)

    @field_validator("name", "subject", "message")
    @classmethod
    def trim_and_require_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Murthy Portfolio API"}


@app.get("/api/health")
def api_health():
    try:
        initialize_database()
        return {"status": "ok", "database": "connected"}
    except DATABASE_ERRORS as exc:
        raise HTTPException(status_code=500, detail="Database unavailable.") from exc


@app.post("/api/contact", status_code=201)
def create_contact_message(payload: ContactMessage):
    try:
        initialize_database()
        with closing(get_connection()) as conn:
            placeholders = "%s, %s, %s, %s, %s" if USE_POSTGRES else "?, ?, ?, ?, ?"
            insert_sql = f"""
                INSERT INTO contact_messages
                    (name, email, subject, message, created_at)
                VALUES ({placeholders})
            """
            if USE_POSTGRES:
                insert_sql += " RETURNING id"

            cursor = conn.execute(
                insert_sql,
                (
                    payload.name,
                    str(payload.email),
                    payload.subject,
                    payload.message,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
            message_id = cursor.fetchone()["id"] if USE_POSTGRES else cursor.lastrowid
    except DATABASE_ERRORS as exc:
        raise HTTPException(
            status_code=500,
            detail="The message could not be saved. Please try again later.",
        ) from exc

    email_sent = send_contact_notification(payload, message_id)
    return {
        "success": True,
        "message": (
            "Thank you! Your message has been received and an email notification was sent."
            if email_sent
            else "Your message was saved, but its email notification could not be sent. Please try again later."
        ),
        "email_sent": email_sent,
        "id": message_id,
    }
