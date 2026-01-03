# Placeholder implementation for aggregate_window
def aggregate_window(data, window_size):
    """
    Aggregates data into windows of a given size.
    Args:
        data (list): List of numerical values.
        window_size (int): Size of each window.
    Returns:
        list: List of aggregated window sums.
    """
    return [sum(data[i:i+window_size]) for i in range(0, len(data), window_size)]

# Placeholder implementation for heuristic_load_score
def heuristic_load_score(features):
    """
    Calculates a heuristic load score from features.
    Args:
        features (dict): Dictionary of feature values.
    Returns:
        float: Heuristic score (example: sum of values).
    """
    return sum(features.values()) if isinstance(features, dict) else 0
from sqlalchemy.orm import Session
from . import models

def upsert_session(db: Session, session_id: str, consent_telemetry: bool, consent_webcam: bool):
    s = db.get(models.Session, session_id)
    if s:
        s.consent_telemetry = consent_telemetry
        s.consent_webcam = consent_webcam
        return s
    s = models.Session(id=session_id, consent_telemetry=consent_telemetry, consent_webcam=consent_webcam)
    db.add(s)
    return s

def add_events(db: Session, session_id: str, events: list[dict]):
    for e in events:
        db.add(models.Event(session_id=session_id, ts_ms=e["ts_ms"], name=e["name"], payload=e.get("payload", {})))

def add_webcam_features(db: Session, session_id: str, feats: list[dict]):
    for f in feats:
        db.add(models.WebcamFeature(session_id=session_id, **f))

def add_effort_label(db: Session, session_id: str, ts_ms: int, rating_1_7: int):
    db.add(models.EffortLabel(session_id=session_id, ts_ms=ts_ms, rating_1_7=rating_1_7))
