from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession
from .db import Base, engine, get_db
from .settings import settings
from . import schemas, crud, models
from .features import aggregate_window, heuristic_load_score
from .auth import get_current_user
from .routers.auth_router import router as auth_router
from .routers.problems_router import router as problems_router
from .routers.experiments_router import router as experiments_router
from .routers.analytics_router import router as analytics_router

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(problems_router)
app.include_router(experiments_router)
app.include_router(analytics_router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/sessions", response_model=schemas.SessionOut)
def create_session(
    payload: schemas.SessionCreate,
    db: DBSession = Depends(get_db),
    user: models.User | None = Depends(get_current_user),
):
    user_id = user.id if user else None
    crud.upsert_session(db, payload.session_id, payload.consent_telemetry, payload.consent_webcam, user_id=user_id)
    db.commit()
    return {"session_id": payload.session_id}


@app.post("/events/batch")
def ingest_events(payload: schemas.EventsBatchIn, db: DBSession = Depends(get_db)):
    crud.add_events(db, payload.session_id, [e.model_dump() for e in payload.events])
    db.commit()
    return {"ingested": len(payload.events)}


@app.post("/webcam/batch")
def ingest_webcam(payload: schemas.WebcamBatchIn, db: DBSession = Depends(get_db)):
    feats = [f.model_dump() for f in payload.features]
    crud.add_webcam_features(db, payload.session_id, feats)
    db.commit()
    return {"ingested": len(payload.features)}


@app.post("/labels/effort")
def ingest_effort_label(payload: schemas.EffortLabelIn, db: DBSession = Depends(get_db)):
    if not (1 <= payload.rating_1_7 <= 7):
        raise HTTPException(status_code=400, detail="rating_1_7 must be 1..7")
    crud.add_effort_label(db, payload.session_id, payload.ts_ms, payload.rating_1_7)
    db.commit()
    return {"ok": True}


@app.get("/load/{session_id}", response_model=schemas.LoadEstimateOut)
def get_load(session_id: str, end_ts_ms: int, use_ml: bool = True, db: DBSession = Depends(get_db)):
    feat = aggregate_window(db, session_id, end_ts_ms)
    if use_ml:
        try:
            from .ml_inference import predict_load
            score, conf, label, action = predict_load(feat)
        except Exception:
            score, conf, label, action = heuristic_load_score(feat)
    else:
        score, conf, label, action = heuristic_load_score(feat)
    return {
        "load_score": score,
        "label": label,
        "confidence": conf,
        "recommended_action": action,
    }

