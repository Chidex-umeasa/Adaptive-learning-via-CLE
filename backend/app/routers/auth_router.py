from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..db import get_db
from ..auth import hash_password, verify_password, create_access_token, require_user
from ..problems import get_all_problems

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenOut)
@limiter.limit("5/minute")
def register(request: Request, payload: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, payload.email, payload.display_name, hash_password(payload.password))
    db.commit()
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.TokenOut)
@limiter.limit("10/minute")
def login(request: Request, payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(require_user)):
    return {"id": user.id, "email": user.email, "display_name": user.display_name}


@router.get("/me/solved", response_model=list[str])
def me_solved(user: models.User = Depends(require_user), db: Session = Depends(get_db)):
    return crud.get_user_solved_problem_ids(db, user.id)


@router.get("/me/stats", response_model=schemas.UserStats)
def me_stats(user: models.User = Depends(require_user), db: Session = Depends(get_db)):
    total_problems = len(get_all_problems())
    return crud.get_user_stats(db, user.id, total_problems)
