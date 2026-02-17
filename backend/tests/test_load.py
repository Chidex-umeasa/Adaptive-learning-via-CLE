def test_get_load_returns_valid_schema(seeded_session, client):
    session_id = seeded_session
    resp = client.get(f"/load/{session_id}", params={"end_ts_ms": 10000})
    assert resp.status_code == 200
    data = resp.json()
    assert "load_score" in data
    assert "label" in data
    assert "confidence" in data
    assert "recommended_action" in data
    assert 0.0 <= data["load_score"] <= 1.0
    assert data["label"] in ("LOW", "MED", "HIGH")
    assert 0.0 <= data["confidence"] <= 1.0
