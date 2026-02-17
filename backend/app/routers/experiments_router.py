from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..db import get_db
from ..ab_testing import ABEngine

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("", response_model=schemas.ExperimentOut)
def create_experiment(payload: schemas.ExperimentCreate, db: Session = Depends(get_db)):
    exp = crud.create_experiment(db, payload.name, payload.config)
    db.commit()
    db.refresh(exp)
    return {"id": exp.id, "name": exp.name, "config": exp.config, "active": exp.active}


@router.get("/{experiment_id}", response_model=schemas.ExperimentOut)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    from ..models import Experiment
    exp = db.get(Experiment, experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {"id": exp.id, "name": exp.name, "config": exp.config, "active": exp.active}


@router.get("/{experiment_id}/results", response_model=schemas.ExperimentResultsOut)
def get_experiment_results(experiment_id: str, db: Session = Depends(get_db)):
    from ..models import Experiment, ExperimentAssignment, Submission
    from sqlalchemy import select, func

    exp = db.get(Experiment, experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    assignments = db.execute(
        select(ExperimentAssignment).where(ExperimentAssignment.experiment_id == experiment_id)
    ).scalars().all()

    variants: dict = {}
    for a in assignments:
        if a.variant not in variants:
            variants[a.variant] = {"sessions": 0, "total_submissions": 0, "correct_submissions": 0}
        variants[a.variant]["sessions"] += 1

        subs = db.execute(
            select(Submission).where(Submission.session_id == a.session_id)
        ).scalars().all()
        variants[a.variant]["total_submissions"] += len(subs)
        variants[a.variant]["correct_submissions"] += sum(1 for s in subs if s.correct)

    for v in variants.values():
        total = v["total_submissions"]
        v["completion_rate"] = round(v["correct_submissions"] / total, 3) if total > 0 else 0.0

    return {"experiment_id": experiment_id, "variants": variants}
