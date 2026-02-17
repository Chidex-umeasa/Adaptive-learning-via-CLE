def test_batch_ingestion_returns_correct_count(client, sample_session_id):
    # Create session first
    client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": False,
    })

    events = [
        {"ts_ms": 1000, "name": "compile_error", "payload": {}},
        {"ts_ms": 2000, "name": "run_code", "payload": {}},
        {"ts_ms": 3000, "name": "correct_answer", "payload": {}},
    ]
    resp = client.post("/events/batch", json={
        "session_id": sample_session_id,
        "events": events,
    })
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 3


def test_empty_batch_returns_zero(client, sample_session_id):
    # Create session first
    client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": False,
    })

    resp = client.post("/events/batch", json={
        "session_id": sample_session_id,
        "events": [],
    })
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 0
