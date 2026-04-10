"""
Smoke & unit tests for opsCopilot API.

Run with:  pytest backend/tests/ -v
Requires a running Postgres (see docker-compose.yml or set DATABASE_URL env var).
Set JWT_SECRET and DATABASE_URL before running, e.g.:

    export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5433/opscopilot"
    export JWT_SECRET="test-secret"
    pytest backend/tests/ -v
"""

import os
import uuid
import pytest
from fastapi.testclient import TestClient

# Ensure test env vars are set before importing app
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/opscopilot")
os.environ.setdefault("JWT_SECRET", "test-secret-do-not-use-in-prod")

from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)

# ── helpers ──────────────────────────────────────────────────────────────────

_TEST_EMAIL = f"smoketest+{uuid.uuid4().hex[:8]}@example.com"
_TEST_PASSWORD = "SmokePass123!"


def _register_and_login() -> str:
    """Register a fresh user and return a valid Bearer token."""
    r = client.post("/api/auth/register", json={"email": _TEST_EMAIL, "password": _TEST_PASSWORD})
    assert r.status_code in (200, 201, 409), f"register failed: {r.text}"

    r = client.post(
        "/api/auth/login",
        data={"username": _TEST_EMAIL, "password": _TEST_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, f"login failed: {r.text}"
    return r.json()["access_token"]


# ── health ────────────────────────────────────────────────────────────────────


def test_health_returns_ok():
    r = client.get("/api/health")
    assert r.status_code in (200, 503)
    body = r.json()
    assert "ok" in body
    assert "db" in body


def test_health_shape():
    r = client.get("/api/health")
    body = r.json()
    assert isinstance(body["ok"], bool)
    assert body["db"] in ("up", "down")
    assert "db_ms" in body


# ── auth ──────────────────────────────────────────────────────────────────────


def test_register_new_user():
    email = f"newuser+{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/api/auth/register", json={"email": email, "password": "ValidPass123!"})
    assert r.status_code in (200, 201)
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_register_duplicate_email():
    email = f"dup+{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "ValidPass123!"})
    r = client.post("/api/auth/register", json={"email": email, "password": "ValidPass123!"})
    assert r.status_code == 409


def test_login_wrong_password():
    email = f"wrongpass+{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "ValidPass123!"})
    r = client.post(
        "/api/auth/login",
        data={"username": email, "password": "WrongPassword!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 401


def test_login_unknown_user():
    r = client.post(
        "/api/auth/login",
        data={"username": "nobody@nowhere.com", "password": "irrelevant"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 401


# ── documents ─────────────────────────────────────────────────────────────────


def test_list_documents_requires_auth():
    r = client.get("/api/documents")
    assert r.status_code == 401


def test_list_documents_authenticated():
    token = _register_and_login()
    r = client.get("/api/documents", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_upload_requires_auth():
    r = client.post("/api/documents/upload", files={"file": ("test.txt", b"hello", "text/plain")})
    assert r.status_code == 401


def test_upload_txt_document():
    token = _register_and_login()
    content = b"This is a test document for opsCopilot smoke tests.\n" * 20
    r = client.post(
        "/api/documents/upload",
        files={"file": ("smoke_test.txt", content, "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "document_id" in body
    assert body["status"] == "UPLOADED"


def test_delete_document():
    token = _register_and_login()
    # Upload first
    r = client.post(
        "/api/documents/upload",
        files={"file": ("delete_me.txt", b"temporary content", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    doc_id = r.json()["document_id"]

    # Delete
    r = client.delete(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 204

    # Confirm gone
    r = client.get("/api/documents", headers={"Authorization": f"Bearer {token}"})
    ids = [d["id"] for d in r.json()]
    assert doc_id not in ids


def test_delete_other_users_document_returns_404():
    token_a = _register_and_login()
    token_b = _register_and_login()

    # A uploads a doc
    r = client.post(
        "/api/documents/upload",
        files={"file": ("a_doc.txt", b"owned by A", "text/plain")},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    doc_id = r.json()["document_id"]

    # B tries to delete it
    r = client.delete(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert r.status_code == 404


# ── chat ──────────────────────────────────────────────────────────────────────


def test_chat_requires_auth():
    r = client.post("/api/chat/ask", json={"question": "What is this?"})
    assert r.status_code == 401


def test_chat_returns_answer_shape():
    token = _register_and_login()
    r = client.post(
        "/api/chat/ask",
        json={"question": "What documents do I have?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # May be 200 (with answer) or 500 if LLM/embeddings unavailable in test env
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        body = r.json()
        assert "answer_markdown" in body
        assert "citations" in body
        assert "query_log_id" in body


# ── eval ──────────────────────────────────────────────────────────────────────


def test_eval_recent_requires_auth():
    r = client.get("/api/eval/recent")
    assert r.status_code == 401


def test_eval_recent_returns_list():
    token = _register_and_login()
    r = client.get("/api/eval/recent", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
