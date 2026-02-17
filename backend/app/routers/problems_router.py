from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..db import get_db
from ..problems import get_problem, get_all_problems
from ..sequencer import select_next_problem, evaluate_submission
from ..features import aggregate_window, heuristic_load_score

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=list[schemas.ProblemListItem])
def list_problems():
    return [
        {"id": p["id"], "title": p["title"], "difficulty": p["difficulty"], "category": p["category"]}
        for p in get_all_problems()
    ]


@router.get("/{problem_id}", response_model=schemas.ProblemOut)
def get_problem_detail(problem_id: str):
    p = get_problem(problem_id)
    if not p:
        raise HTTPException(status_code=404, detail="Problem not found")
    return p


@router.get("/next/{session_id}", response_model=schemas.ProblemOut)
def get_next_problem(session_id: str, db: Session = Depends(get_db)):
    solved = crud.get_solved_problem_ids(db, session_id)

    current_load = None
    try:
        feat = aggregate_window(db, session_id, int(__import__("time").time() * 1000))
        _, _, label, _ = heuristic_load_score(feat)
        current_load = label
    except Exception:
        pass

    problem = select_next_problem(solved, current_load)
    if not problem:
        raise HTTPException(status_code=404, detail="All problems solved")
    return problem


@router.post("/submit", response_model=schemas.SubmissionOut)
def submit_solution(payload: schemas.SubmissionIn, db: Session = Depends(get_db)):
    result = evaluate_submission(payload.problem_id, payload.code)

    crud.add_submission(
        db,
        session_id=payload.session_id,
        problem_id=payload.problem_id,
        code=payload.code,
        correct=result["correct"],
        tests_passed=result["tests_passed"],
        tests_total=result["tests_total"],
    )
    db.commit()

    next_problem_id = None
    if result["correct"]:
        solved = crud.get_solved_problem_ids(db, payload.session_id)
        nxt = select_next_problem(solved, None)
        if nxt:
            next_problem_id = nxt["id"]

    return {
        "correct": result["correct"],
        "tests_passed": result["tests_passed"],
        "tests_total": result["tests_total"],
        "errors": result.get("errors", []),
        "next_problem_id": next_problem_id,
    }
