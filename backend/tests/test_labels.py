def test_effort_label_ingestion(client, sample_session_id):
    # Create session first
    client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": False,
    })

    resp = client.post("/labels/effort", json={
        "session_id": sample_session_id,
        "ts_ms": 5000,
        "rating_1_7": 4,
    })
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_rating_zero_returns_400(client, sample_session_id):
    # Create session first
    client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": False,
    })

    resp = client.post("/labels/effort", json={
        "session_id": sample_session_id,
        "ts_ms": 5000,
        "rating_1_7": 0,
    })
    assert resp.status_code == 400


def test_rating_eight_returns_400(client, sample_session_id):
    # Create session first
    client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": False,
    })

    resp = client.post("/labels/effort", json={
        "session_id": sample_session_id,
        "ts_ms": 5000,
        "rating_1_7": 8,
    })
    assert resp.status_code == 400
