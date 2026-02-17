import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db import Base, get_db


@pytest.fixture()
def test_db():
    """Create an in-memory SQLite database for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(test_db):
    """FastAPI TestClient with the DB dependency overridden to use the test database."""

    def _override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_session_id():
    return "test-session-001"


@pytest.fixture()
def seeded_session(client, sample_session_id):
    """Create a session and seed it with sample events."""
    # Create the session
    resp = client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": True,
    })
    assert resp.status_code == 200

    # Seed some events
    events = [
        {"ts_ms": 1000, "name": "compile_error", "payload": {}},
        {"ts_ms": 2000, "name": "run_code", "payload": {}},
        {"ts_ms": 3000, "name": "keystroke_batch", "payload": {"pause_mean_ms": 200, "deletes": 5, "chars_typed": 50}},
        {"ts_ms": 4000, "name": "correct_answer", "payload": {}},
        {"ts_ms": 5000, "name": "hint_open", "payload": {}},
    ]
    resp = client.post("/events/batch", json={
        "session_id": sample_session_id,
        "events": events,
    })
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 5

    return sample_session_id
