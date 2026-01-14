from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Event, WebcamFeature

WINDOW_MS = 10_000  # 10s

def aggregate_window(db: Session, session_id: str, end_ts_ms: int):
    start_ts = end_ts_ms - WINDOW_MS

    events = db.execute(
        select(Event).where(
            Event.session_id == session_id,
            Event.ts_ms >= start_ts,
            Event.ts_ms <= end_ts_ms
        )
    ).scalars().all()

    webcam = db.execute(
        select(WebcamFeature).where(
            WebcamFeature.session_id == session_id,
            WebcamFeature.ts_ms >= start_ts,
            WebcamFeature.ts_ms <= end_ts_ms
        )
    ).scalars().all()

    # --- telemetry counts ---
    names = [e.name for e in events]
    compile_errors = names.count("compile_error")
    runtime_errors = names.count("runtime_error")
    wrong = names.count("wrong_answer")
    correct = names.count("correct_answer")
    hint_open = names.count("hint_open")
    run_code = names.count("run_code")

    # typing batch stats
    pauses = []
    deletes = 0
    typed = 0
    for e in events:
        if e.name == "keystroke_batch":
            p = e.payload or {}
            pauses.append(float(p.get("pause_mean_ms", 0)))
            deletes += int(p.get("deletes", 0))
            typed += int(p.get("chars_typed", 0))

    pause_mean = sum(pauses)/len(pauses) if pauses else 0.0
    delete_ratio = (deletes / max(typed, 1)) if typed else 0.0

    # --- webcam aggregates ---
    if webcam:
        face_present = sum(w.face_present for w in webcam) / len(webcam)
        gaze_on_screen = sum(w.gaze_on_screen for w in webcam) / len(webcam)
        gaze_dispersion = sum(w.gaze_dispersion for w in webcam) / len(webcam)
        blink_rate = sum(w.blink_rate for w in webcam) / len(webcam)
        head_motion = sum(w.head_motion for w in webcam) / len(webcam)
        away_events = sum(w.away_events for w in webcam)
    else:
        face_present = gaze_on_screen = gaze_dispersion = blink_rate = head_motion = 0.0
        away_events = 0

    return {
        "compile_errors": compile_errors,
        "runtime_errors": runtime_errors,
        "wrong": wrong,
        "correct": correct,
        "hint_open": hint_open,
        "run_code": run_code,
        "pause_mean_ms": pause_mean,
        "delete_ratio": delete_ratio,
        "face_present": face_present,
        "gaze_on_screen": gaze_on_screen,
        "gaze_dispersion": gaze_dispersion,
        "blink_rate": blink_rate,
        "head_motion": head_motion,
        "away_events": away_events,
    }

def heuristic_load_score(feat: dict) -> tuple[float, float, str, str | None]:
    """
    Returns: (score 0..1, confidence 0..1, label, recommended_action)
    """
    # High load signals: errors, wrong, lots of hints, long pauses, away events, low face_present
    score = 0.0
    score += 0.18 * min(feat["compile_errors"], 3)
    score += 0.12 * min(feat["runtime_errors"], 3)
    score += 0.20 * min(feat["wrong"], 3)
    score += 0.10 * min(feat["hint_open"], 4)
    score += 0.10 * min(feat["pause_mean_ms"] / 1500.0, 2.0)
    score += 0.08 * min(feat["delete_ratio"] / 0.25, 2.0)
    score += 0.10 * min(feat["away_events"], 3)
    score += 0.12 * min(feat["head_motion"] / 1.0, 2.0)
    score -= 0.08 * min(feat["correct"], 3)
    score -= 0.10 * min(feat["gaze_on_screen"], 1.0)
    score -= 0.08 * min(feat["face_present"], 1.0)

    # normalize-ish
    score = max(0.0, min(1.0, score / 1.2))

    if score < 0.33:
        label = "LOW"
    elif score < 0.66:
        label = "MED"
    else:
        label = "HIGH"

    # confidence: higher if we have both telemetry + webcam presence
    confidence = 0.55
    if feat["face_present"] > 0.2:
        confidence += 0.15
    if (feat["compile_errors"] + feat["wrong"] + feat["run_code"] + feat["hint_open"]) > 0:
        confidence += 0.15
    confidence = min(0.95, confidence)

    action = None
    if label == "HIGH" and (feat["compile_errors"] + feat["wrong"]) >= 2:
        action = "DECOMPOSE_TASK"
    elif label == "HIGH" and feat["hint_open"] >= 2:
        action = "WORKED_EXAMPLE"
    elif label == "LOW" and feat["correct"] >= 1:
        action = "HARDER_NEXT"

    return score, confidence, label, action
