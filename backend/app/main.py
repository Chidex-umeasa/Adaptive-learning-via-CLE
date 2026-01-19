from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .settings import settings
from . import schemas, crud
from .features import aggregate_window, heuristic_load_score

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create tables for MVP (later: Alembic)
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/sessions", response_model=schemas.SessionOut)
def create_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
    crud.upsert_session(db, payload.session_id, payload.consent_telemetry, payload.consent_webcam)
    db.commit()
    return {"session_id": payload.session_id}

@app.post("/events/batch")
def ingest_events(payload: schemas.EventsBatchIn, db: Session = Depends(get_db)):
    # you can enforce consent checks here if you want
    crud.add_events(db, payload.session_id, [e.model_dump() for e in payload.events])
    db.commit()
    return {"ingested": len(payload.events)}

@app.post("/webcam/batch")
def ingest_webcam(payload: schemas.WebcamBatchIn, db: Session = Depends(get_db)):
    feats = [f.model_dump() for f in payload.features]
    crud.add_webcam_features(db, payload.session_id, feats)
    db.commit()
    return {"ingested": len(payload.features)}

@app.post("/labels/effort")
def ingest_effort_label(payload: schemas.EffortLabelIn, db: Session = Depends(get_db)):
    if not (1 <= payload.rating_1_7 <= 7):
        raise HTTPException(status_code=400, detail="rating_1_7 must be 1..7")
    crud.add_effort_label(db, payload.session_id, payload.ts_ms, payload.rating_1_7)
    db.commit()
    return {"ok": True}

@app.get("/load/{session_id}", response_model=schemas.LoadEstimateOut)
def get_load(session_id: str, end_ts_ms: int, db: Session = Depends(get_db)):
    feat = aggregate_window(db, session_id, end_ts_ms)
    score, conf, label, action = heuristic_load_score(feat)
    return {
        "load_score": score,
        "label": label,
        "confidence": conf,
        "recommended_action": action
    }

