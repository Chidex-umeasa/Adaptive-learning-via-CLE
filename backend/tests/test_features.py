from app.features import aggregate_window, heuristic_load_score


def _zeroed_features():
    """Return a feature dict with all values set to zero."""
    return {
        "compile_errors": 0,
        "runtime_errors": 0,
        "wrong": 0,
        "correct": 0,
        "hint_open": 0,
        "run_code": 0,
        "pause_mean_ms": 0.0,
        "delete_ratio": 0.0,
        "face_present": 0.0,
        "gaze_on_screen": 0.0,
        "gaze_dispersion": 0.0,
        "blink_rate": 0.0,
        "head_motion": 0.0,
        "away_events": 0,
    }


def test_zeroed_features_returns_low():
    feat = _zeroed_features()
    score, confidence, label, action = heuristic_load_score(feat)
    assert label == "LOW"


def test_high_errors_returns_high():
    feat = _zeroed_features()
    feat["compile_errors"] = 3
    feat["runtime_errors"] = 3
    feat["wrong"] = 3
    feat["hint_open"] = 4
    feat["away_events"] = 3
    feat["head_motion"] = 2.0
    score, confidence, label, action = heuristic_load_score(feat)
    assert label == "HIGH"


def test_score_between_zero_and_one():
    feat = _zeroed_features()
    score, confidence, label, action = heuristic_load_score(feat)
    assert 0.0 <= score <= 1.0

    # Also test with high values
    feat["compile_errors"] = 10
    feat["wrong"] = 10
    score2, _, _, _ = heuristic_load_score(feat)
    assert 0.0 <= score2 <= 1.0


def test_confidence_increases_with_webcam_data():
    feat_no_webcam = _zeroed_features()
    feat_no_webcam["run_code"] = 1  # some telemetry activity

    feat_with_webcam = _zeroed_features()
    feat_with_webcam["run_code"] = 1
    feat_with_webcam["face_present"] = 0.9

    _, conf_no_webcam, _, _ = heuristic_load_score(feat_no_webcam)
    _, conf_with_webcam, _, _ = heuristic_load_score(feat_with_webcam)

    assert conf_with_webcam > conf_no_webcam
