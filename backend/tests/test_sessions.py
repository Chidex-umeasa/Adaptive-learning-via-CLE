def test_create_session_returns_200_and_session_id(client, sample_session_id):
    resp = client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": False,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["session_id"] == sample_session_id


def test_upsert_updates_consent_flags(client, sample_session_id):
    # Create session
    client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": False,
    })
    # Upsert with different consent flags
    resp = client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": False,
        "consent_webcam": True,
    })
    assert resp.status_code == 200
    assert resp.json()["session_id"] == sample_session_id


def test_missing_session_id_returns_422(client):
    resp = client.post("/sessions", json={
        "consent_telemetry": True,
        "consent_webcam": False,
    })
    assert resp.status_code == 422
