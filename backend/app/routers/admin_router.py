"""
Admin endpoints — not exposed in production without additional auth hardening.
POST /admin/retrain  — exports real DB labels → CSV → runs ml/train.py → hot-swaps model.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..features import aggregate_window

router = APIRouter(prefix="/admin", tags=["admin"])

ML_DIR = Path(__file__).resolve().parents[3] / "ml"
TRAIN_SCRIPT = ML_DIR / "train.py"
DATA_PATH = ML_DIR / "training_data.csv"

FEATURE_COLS = [
    "compile_errors", "runtime_errors", "wrong", "correct",
    "hint_open", "run_code", "pause_mean_ms", "delete_ratio",
    "face_present", "gaze_on_screen", "gaze_dispersion",
    "blink_rate", "head_motion", "away_events",
]


def _export_training_data(db: Session) -> int:
    """Build training_data.csv from real EffortLabel rows + matching feature windows."""
    labels = db.execute(select(models.EffortLabel).order_by(models.EffortLabel.session_id)).scalars().all()
    if not labels:
        return 0

    rows = []
    for lbl in labels:
        try:
            feat = aggregate_window(db, lbl.session_id, lbl.ts_ms)
            row = {col: feat.get(col, 0.0) for col in FEATURE_COLS}
            row["effort_label"] = lbl.rating_1_7
            rows.append(row)
        except Exception:
            continue

    if not rows:
        return 0

    import csv
    with open(DATA_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FEATURE_COLS + ["effort_label"])
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


@router.post("/retrain")
def retrain(db: Session = Depends(get_db)):
    """
    Export real labeled data from the DB, retrain the ML model, and hot-swap it.
    Runs synchronously — may take 10-30 seconds depending on data size.
    """
    if not TRAIN_SCRIPT.exists():
        raise HTTPException(status_code=500, detail="Training script not found")

    n_samples = _export_training_data(db)
    if n_samples < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough labeled data to retrain (found {n_samples} samples, need >= 10). "
                   "Collect more effort ratings first.",
        )

    result = subprocess.run(
        [sys.executable, str(TRAIN_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(ML_DIR),
    )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Training failed:\n{result.stderr[-2000:]}",
        )

    # Hot-swap the in-process model
    from ..ml_inference import reload_model
    model, _ = reload_model()

    return {
        "ok": True,
        "samples_used": n_samples,
        "model_loaded": model is not None,
        "stdout_tail": result.stdout[-500:] if result.stdout else "",
    }


@router.get("/retrain/status")
def retrain_status():
    """Check if a trained model artifact exists and when it was last modified."""
    from ..ml_inference import MODEL_PATH
    if not MODEL_PATH.exists():
        return {"model_exists": False, "last_trained": None}
    import datetime
    mtime = MODEL_PATH.stat().st_mtime
    last_trained = datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc).isoformat()
    return {"model_exists": True, "last_trained": last_trained}
