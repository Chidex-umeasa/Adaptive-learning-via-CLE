def test_webcam_batch_ingestion(client, sample_session_id):
    # Create session first
    client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": True,
    })

    features = [
        {
            "ts_ms": 1000,
            "face_present": 1.0,
            "gaze_on_screen": 0.9,
            "gaze_dispersion": 0.1,
            "blink_rate": 15.0,
            "head_motion": 0.2,
            "away_events": 0,
        },
        {
            "ts_ms": 2000,
            "face_present": 0.8,
            "gaze_on_screen": 0.7,
            "gaze_dispersion": 0.3,
            "blink_rate": 18.0,
            "head_motion": 0.5,
            "away_events": 1,
        },
    ]
    resp = client.post("/webcam/batch", json={
        "session_id": sample_session_id,
        "features": features,
    })
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 2
