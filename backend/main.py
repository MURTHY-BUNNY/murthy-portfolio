"""
Murthy Portfolio Backend
FastAPI + SQLite contact form API.
Run from this folder: uvicorn main:app --reload
"""
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "portfolio.db")))

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
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


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
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Database unavailable.") from exc


@app.post("/api/contact", status_code=201)
def create_contact_message(payload: ContactMessage):
    try:
        with closing(get_connection()) as conn:
            cursor = conn.execute(
                """
                INSERT INTO contact_messages
                    (name, email, subject, message, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    payload.name,
                    str(payload.email),
                    payload.subject,
                    payload.message,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
            message_id = cursor.lastrowid
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail="The message could not be saved. Please try again later.",
        ) from exc

    return {
        "success": True,
        "message": "Thank you! Your message has been received.",
        "id": message_id,
    }
