from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import schemas, crud, models
from ..db import get_db
from ..features import aggregate_window, heuristic_load_score
import csv
import io

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sessions", response_model=list[schemas.SessionSummary])
def list_sessions(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return crud.get_all_sessions_summary(db, limit=limit, offset=offset)


@router.get("/sessions/{session_id}/timeline")
def session_timeline(session_id: str, db: Session = Depends(get_db)):
    events = db.execute(
        select(models.Event).where(models.Event.session_id == session_id).order_by(models.Event.ts_ms)
    ).scalars().all()

    if not events:
        return {"points": []}

    start_ts = events[0].ts_ms
    end_ts = events[-1].ts_ms
    step = 5000  # 5s intervals

    points = []
    t = start_ts
    while t <= end_ts:
        feat = aggregate_window(db, session_id, t)
        score, conf, label, action = heuristic_load_score(feat)
        points.append({
            "ts_ms": t,
            "seconds": round((t - start_ts) / 1000, 1),
            "load_score": round(score, 3),
            "label": label,
            "confidence": round(conf, 3),
        })
        t += step

    return {"session_id": session_id, "points": points}


@router.get("/aggregate", response_model=schemas.AggregateStats)
def aggregate_stats(db: Session = Depends(get_db)):
    return crud.get_aggregate_stats(db)


@router.get("/feature_correlations")
def feature_correlations(db: Session = Depends(get_db)):
    labels = db.execute(select(models.EffortLabel)).scalars().all()
    if not labels:
        return {"correlations": {}, "sample_size": 0}

    feature_names = [
        "compile_errors", "runtime_errors", "wrong", "correct",
        "hint_open", "pause_mean_ms", "delete_ratio",
        "face_present", "gaze_on_screen", "blink_rate", "head_motion", "away_events",
    ]
    feature_sums = {f: 0.0 for f in feature_names}
    effort_sum = 0.0
    n = 0

    data = []
    for lbl in labels:
        feat = aggregate_window(db, lbl.session_id, lbl.ts_ms)
        data.append((feat, lbl.rating_1_7))
        for f in feature_names:
            feature_sums[f] += feat.get(f, 0)
        effort_sum += lbl.rating_1_7
        n += 1

    if n < 2:
        return {"correlations": {f: 0.0 for f in feature_names}, "sample_size": n}

    # Compute Pearson r for each feature vs effort
    effort_mean = effort_sum / n
    feature_means = {f: feature_sums[f] / n for f in feature_names}

    correlations = {}
    for f in feature_names:
        cov = 0.0
        var_f = 0.0
        var_e = 0.0
        for feat, rating in data:
            fv = feat.get(f, 0) - feature_means[f]
            ev = rating - effort_mean
            cov += fv * ev
            var_f += fv * fv
            var_e += ev * ev
        denom = (var_f * var_e) ** 0.5
        correlations[f] = round(cov / denom, 3) if denom > 0 else 0.0

    return {"correlations": correlations, "sample_size": n}


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    events = db.execute(select(models.Event).order_by(models.Event.ts_ms)).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["session_id", "ts_ms", "event_name", "payload"])
    for e in events:
        writer.writerow([e.session_id, e.ts_ms, e.name, str(e.payload)])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=adaptive_load_events.csv"},
    )
