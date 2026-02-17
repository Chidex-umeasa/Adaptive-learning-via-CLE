import shutil
import pytest


def test_get_problems_returns_non_empty_list(client):
    resp = client.get("/problems")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_problem_sum_two(client):
    resp = client.get("/problems/sum_two")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "sum_two"
    assert data["title"] == "Sum of Two Numbers"
    assert data["difficulty"] == 1
    assert data["category"] == "basics"
    assert len(data["test_cases"]) > 0


@pytest.mark.skipif(
    shutil.which("node") is None,
    reason="Node.js not available on this system",
)
def test_submit_correct_code(client, sample_session_id):
    # Create session first
    client.post("/sessions", json={
        "session_id": sample_session_id,
        "consent_telemetry": True,
        "consent_webcam": False,
    })

    resp = client.post("/problems/submit", json={
        "session_id": sample_session_id,
        "problem_id": "sum_two",
        "code": "function sum(a, b) { return a + b; }",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["correct"] is True
    assert data["tests_passed"] == data["tests_total"]
