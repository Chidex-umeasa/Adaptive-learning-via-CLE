from sqlalchemy.orm import Session
from sqlalchemy import select, func
from . import models


def upsert_session(db: Session, session_id: str, consent_telemetry: bool, consent_webcam: bool, user_id: str | None = None):
    s = db.get(models.Session, session_id)
    if s:
        s.consent_telemetry = consent_telemetry
        s.consent_webcam = consent_webcam
        if user_id:
            s.user_id = user_id
        return s
    s = models.Session(id=session_id, consent_telemetry=consent_telemetry, consent_webcam=consent_webcam, user_id=user_id)
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


# --- Auth ---

def create_user(db: Session, email: str, display_name: str, password_hash: str) -> models.User:
    user = models.User(email=email, display_name=display_name, password_hash=password_hash)
    db.add(user)
    return user


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.execute(select(models.User).where(models.User.email == email)).scalar_one_or_none()


# --- Submissions ---

def add_submission(db: Session, session_id: str, problem_id: str, code: str, correct: bool, tests_passed: int, tests_total: int) -> models.Submission:
    sub = models.Submission(
        session_id=session_id, problem_id=problem_id, code=code,
        correct=correct, tests_passed=tests_passed, tests_total=tests_total,
    )
    db.add(sub)
    return sub


def get_session_submissions(db: Session, session_id: str) -> list[models.Submission]:
    return db.execute(select(models.Submission).where(models.Submission.session_id == session_id)).scalars().all()


def get_solved_problem_ids(db: Session, session_id: str) -> set[str]:
    rows = db.execute(
        select(models.Submission.problem_id).where(
            models.Submission.session_id == session_id,
            models.Submission.correct == True,
        )
    ).scalars().all()
    return set(rows)


# --- Experiments ---

def create_experiment(db: Session, name: str, config: dict) -> models.Experiment:
    exp = models.Experiment(name=name, config=config)
    db.add(exp)
    return exp


def get_active_experiment(db: Session) -> models.Experiment | None:
    return db.execute(select(models.Experiment).where(models.Experiment.active == True)).scalar_one_or_none()


def assign_experiment(db: Session, session_id: str, experiment_id: str, variant: str) -> models.ExperimentAssignment:
    a = models.ExperimentAssignment(session_id=session_id, experiment_id=experiment_id, variant=variant)
    db.add(a)
    return a


def get_session_variant(db: Session, session_id: str) -> str | None:
    a = db.execute(
        select(models.ExperimentAssignment).where(models.ExperimentAssignment.session_id == session_id)
    ).scalar_one_or_none()
    return a.variant if a else None


# --- Analytics ---

def get_all_sessions_summary(db: Session, limit: int = 100, offset: int = 0) -> list[dict]:
    sessions = db.execute(
        select(models.Session).order_by(models.Session.created_at.desc()).limit(limit).offset(offset)
    ).scalars().all()

    results = []
    for s in sessions:
        event_count = db.execute(
            select(func.count()).select_from(models.Event).where(models.Event.session_id == s.id)
        ).scalar()
        sub_count = db.execute(
            select(func.count()).select_from(models.Submission).where(models.Submission.session_id == s.id)
        ).scalar()
        solved_count = db.execute(
            select(func.count()).select_from(models.Submission).where(
                models.Submission.session_id == s.id, models.Submission.correct == True
            )
        ).scalar()

        results.append({
            "session_id": s.id,
            "user_email": s.user.email if s.user else None,
            "created_at": s.created_at.isoformat(),
            "event_count": event_count,
            "mean_load": None,
            "problems_attempted": sub_count,
            "problems_solved": solved_count,
        })
    return results


def get_aggregate_stats(db: Session) -> dict:
    return {
        "total_sessions": db.execute(select(func.count()).select_from(models.Session)).scalar(),
        "total_events": db.execute(select(func.count()).select_from(models.Event)).scalar(),
        "total_users": db.execute(select(func.count()).select_from(models.User)).scalar(),
        "mean_load_score": None,
    }
