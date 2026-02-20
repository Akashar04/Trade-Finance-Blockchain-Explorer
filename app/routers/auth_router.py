from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..deps import get_db
from ..auth import hash_password

router = APIRouter()


@router.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        org_name=user.org_name,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

from fastapi import Response
from ..auth import verify_password, create_access_token, create_refresh_token


@router.post("/login", response_model=schemas.TokenResponse)
def login(user: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({
        "user_id": db_user.id,
        "role": db_user.role
    })

    refresh_token = create_refresh_token({
        "user_id": db_user.id
    })

    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True
    )

    from ..services.audit_service import log_action
    log_action(db, db_user.id, "LOGIN", "USER", db_user.id)

    return {"accessToken": access_token, "role": db_user.role}

from ..deps import get_current_user

@router.get("/user")
def get_user(current_user: models.User = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email,
        "org": current_user.org_name,
        "role": current_user.role
    }