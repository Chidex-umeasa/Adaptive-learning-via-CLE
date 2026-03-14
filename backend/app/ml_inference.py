import json
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent.parent / "ml" / "artifacts" / "load_model.joblib"
FEATURES_PATH = Path(__file__).parent.parent.parent / "ml" / "artifacts" / "feature_names.json"

_model = None
_feature_names = None


def get_model():
    global _model, _feature_names
    if _model is None and MODEL_PATH.exists():
        import joblib
        _model = joblib.load(MODEL_PATH)
        _feature_names = json.loads(FEATURES_PATH.read_text())
    return _model, _feature_names


def reload_model():
    """Force reload model from disk (call after retraining)."""
    global _model, _feature_names
    _model = None
    _feature_names = None
    return get_model()


def predict_load(features: dict) -> tuple[float, float, str, str | None]:
    model, feature_names = get_model()
    if model is None:
        from .features import heuristic_load_score
        return heuristic_load_score(features)

    X = [[features.get(f, 0.0) for f in feature_names]]
    raw_score = float(model.predict(X)[0])
    score = max(0.0, min(1.0, (raw_score - 1) / 6))

    if score < 0.33:
        label = "LOW"
    elif score < 0.66:
        label = "MED"
    else:
        label = "HIGH"

    confidence = 0.70
    if features.get("face_present", 0) > 0.2:
        confidence += 0.10
    if (features.get("compile_errors", 0) + features.get("wrong", 0) + features.get("run_code", 0)) > 0:
        confidence += 0.10
    confidence = min(0.95, confidence)

    action = None
    if label == "HIGH" and (features.get("compile_errors", 0) + features.get("wrong", 0)) >= 2:
        action = "DECOMPOSE_TASK"
    elif label == "HIGH" and features.get("hint_open", 0) >= 2:
        action = "WORKED_EXAMPLE"
    elif label == "LOW" and features.get("correct", 0) >= 1:
        action = "HARDER_NEXT"

    return score, confidence, label, action
