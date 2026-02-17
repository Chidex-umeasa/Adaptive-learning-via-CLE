#!/usr/bin/env python3
"""
Export training data from the SQLite database used by the Adaptive Load Tutor
backend.

Connects to ``backend/adaptive_load.db``, queries the *events*,
*webcam_features*, and *effort_labels* tables, aligns them by session_id and
10-second windows centred on each effort label timestamp, computes the same
aggregated features as ``backend/app/features.py``, and writes the result to
``ml/training_data.csv``.
"""

import os
import sqlite3
import json
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "backend", "adaptive_load.db")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "training_data.csv")

WINDOW_MS = 10_000  # 10 seconds, matching backend/app/features.py

FEATURE_COLS = [
    "compile_errors",
    "runtime_errors",
    "wrong",
    "correct",
    "hint_open",
    "run_code",
    "pause_mean_ms",
    "delete_ratio",
    "face_present",
    "gaze_on_screen",
    "gaze_dispersion",
    "blink_rate",
    "head_motion",
    "away_events",
]


def _aggregate_events(rows: list[dict]) -> dict:
    """Aggregate raw event rows into telemetry feature counts.

    Mirrors the logic in ``backend/app/features.aggregate_window``.
    """
    names = [r["name"] for r in rows]

    compile_errors = names.count("compile_error")
    runtime_errors = names.count("runtime_error")
    wrong = names.count("wrong_answer")
    correct = names.count("correct_answer")
    hint_open = names.count("hint_open")
    run_code = names.count("run_code")

    pauses = []
    deletes = 0
    typed = 0
    for r in rows:
        if r["name"] == "keystroke_batch":
            payload = r.get("payload") or {}
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except (json.JSONDecodeError, TypeError):
                    payload = {}
            pauses.append(float(payload.get("pause_mean_ms", 0)))
            deletes += int(payload.get("deletes", 0))
            typed += int(payload.get("chars_typed", 0))

    pause_mean = sum(pauses) / len(pauses) if pauses else 0.0
    delete_ratio = (deletes / max(typed, 1)) if typed else 0.0

    return {
        "compile_errors": compile_errors,
        "runtime_errors": runtime_errors,
        "wrong": wrong,
        "correct": correct,
        "hint_open": hint_open,
        "run_code": run_code,
        "pause_mean_ms": round(pause_mean, 1),
        "delete_ratio": round(delete_ratio, 4),
    }


def _aggregate_webcam(rows: list[dict]) -> dict:
    """Aggregate raw webcam feature rows.

    Mirrors the webcam section of ``backend/app/features.aggregate_window``.
    """
    if not rows:
        return {
            "face_present": 0.0,
            "gaze_on_screen": 0.0,
            "gaze_dispersion": 0.0,
            "blink_rate": 0.0,
            "head_motion": 0.0,
            "away_events": 0,
        }

    n = len(rows)
    return {
        "face_present": round(sum(r["face_present"] for r in rows) / n, 3),
        "gaze_on_screen": round(sum(r["gaze_on_screen"] for r in rows) / n, 3),
        "gaze_dispersion": round(sum(r["gaze_dispersion"] for r in rows) / n, 3),
        "blink_rate": round(sum(r["blink_rate"] for r in rows) / n, 1),
        "head_motion": round(sum(r["head_motion"] for r in rows) / n, 3),
        "away_events": sum(r["away_events"] for r in rows),
    }


def main():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        print(
            "Run the backend at least once to create the DB, or use "
            "generate_synthetic_data.py instead."
        )
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Fetch all effort labels
    labels = conn.execute(
        "SELECT session_id, ts_ms, rating_1_7 FROM effort_labels ORDER BY session_id, ts_ms"
    ).fetchall()

    if not labels:
        print("No effort labels found in the database. Nothing to export.")
        conn.close()
        return

    print(f"Found {len(labels)} effort labels across sessions.")

    output_rows = []

    for label_row in labels:
        session_id = label_row["session_id"]
        label_ts = label_row["ts_ms"]
        effort = label_row["rating_1_7"]

        start_ts = label_ts - WINDOW_MS
        end_ts = label_ts

        # Query events in the 10s window
        event_rows = conn.execute(
            "SELECT name, payload FROM events "
            "WHERE session_id = ? AND ts_ms >= ? AND ts_ms <= ?",
            (session_id, start_ts, end_ts),
        ).fetchall()

        # Query webcam features in the 10s window
        webcam_rows = conn.execute(
            "SELECT face_present, gaze_on_screen, gaze_dispersion, "
            "       blink_rate, head_motion, away_events "
            "FROM webcam_features "
            "WHERE session_id = ? AND ts_ms >= ? AND ts_ms <= ?",
            (session_id, start_ts, end_ts),
        ).fetchall()

        event_dicts = [dict(r) for r in event_rows]
        webcam_dicts = [dict(r) for r in webcam_rows]

        features = {}
        features.update(_aggregate_events(event_dicts))
        features.update(_aggregate_webcam(webcam_dicts))
        features["effort_label"] = effort

        output_rows.append(features)

    conn.close()

    df = pd.DataFrame(output_rows, columns=FEATURE_COLS + ["effort_label"])
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(df)} rows to {OUTPUT_PATH}")
    print(f"Effort-label distribution:\n{df['effort_label'].value_counts().sort_index()}")


if __name__ == "__main__":
    main()
