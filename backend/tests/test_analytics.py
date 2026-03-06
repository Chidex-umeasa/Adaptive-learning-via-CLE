import pytest


def test_aggregate_stats_empty(client):
    resp = client.get("/analytics/aggregate")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sessions"] == 0
    assert data["total_events"] == 0
    assert data["total_users"] == 0
    assert data["mean_load_score"] is None


def test_aggregate_stats_with_data(client, seeded_session):
    resp = client.get("/analytics/aggregate")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sessions"] == 1
    assert data["total_events"] == 5


def test_aggregate_stats_mean_load_with_effort_label(client, seeded_session):
    client.post("/labels/effort", json={
        "session_id": seeded_session,
        "ts_ms": 3000,
        "rating_1_7": 7,
    })
    resp = client.get("/analytics/aggregate")
    assert resp.status_code == 200
    data = resp.json()
    # rating 7 -> (7-1)/6 = 1.0
    assert data["mean_load_score"] == 1.0


def test_sessions_list_empty(client):
    resp = client.get("/analytics/sessions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_sessions_list_with_session(client, seeded_session):
    resp = client.get("/analytics/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    row = data[0]
    assert row["session_id"] == seeded_session
    assert row["event_count"] == 5
    assert row["mean_load"] is None  # no effort labels yet


def test_sessions_list_mean_load_from_effort(client, seeded_session):
    # rating 4 -> (4-1)/6 = 0.5
    client.post("/labels/effort", json={
        "session_id": seeded_session,
        "ts_ms": 3000,
        "rating_1_7": 4,
    })
    resp = client.get("/analytics/sessions")
    assert resp.status_code == 200
    row = resp.json()[0]
    assert row["mean_load"] == pytest.approx(0.5, abs=0.01)


def test_ab_results_empty(client):
    resp = client.get("/analytics/ab_results")
    assert resp.status_code == 200
    data = resp.json()
    assert "variants" in data
    assert data["variants"] == {}


def test_ab_results_with_experiment(client, seeded_session):
    # Create an experiment
    exp_resp = client.post("/experiments", json={
        "name": "test-exp",
        "config": {"weights": {"control": 50, "heuristic": 50}},
    })
    assert exp_resp.status_code == 200
    exp_id = exp_resp.json()["id"]

    # Manually assign a session to a variant via the DB (no API for this)
    # Instead, test that the endpoint returns the right shape
    resp = client.get("/analytics/ab_results")
    assert resp.status_code == 200
    data = resp.json()
    assert "variants" in data
    # No assignments yet, so still empty
    assert data["variants"] == {}


def test_session_timeline(client, seeded_session):
    resp = client.get(f"/analytics/sessions/{seeded_session}/timeline")
    assert resp.status_code == 200
    data = resp.json()
    assert "points" in data
    assert isinstance(data["points"], list)
    assert len(data["points"]) > 0
    first = data["points"][0]
    assert "load_score" in first
    assert "label" in first
    assert "seconds" in first


def test_session_timeline_no_events(client):
    resp = client.get("/analytics/sessions/nonexistent-session/timeline")
    assert resp.status_code == 200
    assert resp.json() == {"points": []}


def test_feature_correlations_empty(client):
    resp = client.get("/analytics/feature_correlations")
    assert resp.status_code == 200
    data = resp.json()
    assert "correlations" in data
    assert data["correlations"] == {}
    assert data["sample_size"] == 0
