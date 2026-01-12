from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlmodel import Session
import jwt

from app.db.session import get_session
from app.schemas.auth import LoginRequest, TokenResponse, SignupRequest, MessageResponse
from app.services.auth import authenticate_user, create_user
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
):
    user = authenticate_user(session, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict",
    )

    return {"access_token": access_token}


@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(payload["sub"])
    return {"access_token": new_access_token}


@router.post("/signup", response_model=MessageResponse)
def signup(
    data: SignupRequest,
    session: Session = Depends(get_session),
):
    try:
        create_user(session, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Signup successful"}
