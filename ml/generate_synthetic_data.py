#!/usr/bin/env python3
"""
Generate synthetic training data for the Adaptive Load Tutor ML pipeline.

Produces 500+ rows with 14 features and an effort_label (1-7).
Distributions are correlated so that:
  - High effort (5-7): more errors, more hints, longer pauses, more head motion,
    lower gaze_on_screen
  - Low effort (1-3): more correct answers, shorter pauses, higher gaze_on_screen,
    lower head motion
  - Medium effort (3-5): mixed signals
"""

import os
import numpy as np
import pandas as pd

SEED = 42
N_SAMPLES = 600  # total rows (200 per band)

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


def _clamp(val, lo, hi):
    return max(lo, min(hi, val))


def generate_band(rng: np.random.Generator, label_lo: int, label_hi: int, n: int):
    """Generate *n* rows for an effort-label band [label_lo, label_hi]."""
    rows = []
    for _ in range(n):
        label = rng.integers(label_lo, label_hi + 1)
        t = (label - 1) / 6.0  # 0 = lowest effort, 1 = highest effort

        # --- telemetry counts (Poisson-like, shifted by effort) ---
        compile_errors = int(_clamp(rng.poisson(0.3 + 2.5 * t), 0, 10))
        runtime_errors = int(_clamp(rng.poisson(0.2 + 1.8 * t), 0, 8))
        wrong = int(_clamp(rng.poisson(0.2 + 2.0 * t), 0, 8))
        correct = int(_clamp(rng.poisson(2.5 - 1.8 * t), 0, 8))
        hint_open = int(_clamp(rng.poisson(0.3 + 2.0 * t), 0, 10))
        run_code = int(_clamp(rng.poisson(2.0 + 1.5 * t), 0, 15))

        # --- typing behaviour ---
        pause_mean_ms = _clamp(rng.normal(300 + 900 * t, 120), 50, 3000)
        delete_ratio = _clamp(rng.normal(0.08 + 0.25 * t, 0.06), 0.0, 1.0)

        # --- webcam features ---
        face_present = _clamp(rng.normal(0.90 - 0.15 * t, 0.08), 0.0, 1.0)
        gaze_on_screen = _clamp(rng.normal(0.88 - 0.30 * t, 0.10), 0.0, 1.0)
        gaze_dispersion = _clamp(rng.normal(0.15 + 0.35 * t, 0.08), 0.0, 1.0)
        blink_rate = _clamp(rng.normal(15 + 8 * t, 3), 3, 40)
        head_motion = _clamp(rng.normal(0.2 + 0.9 * t, 0.18), 0.0, 3.0)
        away_events = int(_clamp(rng.poisson(0.3 + 2.0 * t), 0, 10))

        rows.append(
            {
                "compile_errors": compile_errors,
                "runtime_errors": runtime_errors,
                "wrong": wrong,
                "correct": correct,
                "hint_open": hint_open,
                "run_code": run_code,
                "pause_mean_ms": round(pause_mean_ms, 1),
                "delete_ratio": round(delete_ratio, 4),
                "face_present": round(face_present, 3),
                "gaze_on_screen": round(gaze_on_screen, 3),
                "gaze_dispersion": round(gaze_dispersion, 3),
                "blink_rate": round(blink_rate, 1),
                "head_motion": round(head_motion, 3),
                "away_events": away_events,
                "effort_label": label,
            }
        )
    return rows


def main():
    rng = np.random.default_rng(SEED)

    rows = []
    rows.extend(generate_band(rng, 1, 3, N_SAMPLES // 3))   # low effort
    rows.extend(generate_band(rng, 3, 5, N_SAMPLES // 3))   # medium effort
    rows.extend(generate_band(rng, 5, 7, N_SAMPLES // 3))   # high effort

    df = pd.DataFrame(rows)
    # shuffle
    df = df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

    out_path = os.path.join(os.path.dirname(__file__), "training_data.csv")
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
    print(f"Effort-label distribution:\n{df['effort_label'].value_counts().sort_index()}")
    print(f"\nFeature summary:\n{df.describe().round(2)}")


if __name__ == "__main__":
    main()
