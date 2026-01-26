from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
import jwt
import logging

from app.db.session import get_session
from app.db.models import User
from app.schemas.auth import LoginRequest, TokenResponse, SignupRequest, MessageResponse, UserResponse
from app.services.auth import authenticate_user, create_user
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

# Standard Bearer token handling
security = HTTPBearer()

def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency to extract and validate user from Authorization header.
    
    Used by protected endpoints.
    
    **Expected header format:**
    Authorization: Bearer <access_token>
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    user = session.exec(select(User).where(User.id == int(user_id))).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
):
    """
    Login endpoint - Authenticates existing user and returns access token.
    
    Refresh token is returned as HttpOnly cookie (Set-Cookie header).
    
    **Required for auth:**
    - Authorization header: `Bearer {access_token}` for protected routes
    
    **Errors:**
    - 401 User not found: Email not registered
    - 401 Invalid password: Wrong password for existing user
    """
    logger.info(f"Login attempt for email: {data.email}")
    
    auth_result = authenticate_user(session, data.email, data.password)
    
    if not auth_result["success"]:
        if auth_result["reason"] == "user_not_found":
            logger.warning(f"Login failed - user not found: {data.email}")
            raise HTTPException(status_code=401, detail="User not found")
        else:  # invalid_password
            logger.warning(f"Login failed - invalid password: {data.email}")
            raise HTTPException(status_code=401, detail="Invalid password")
    
    user = auth_result["user"]
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=7*24*60*60,  # 7 days
    )

    logger.info(f"Login successful for: {data.email}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str = Cookie(None)):
    """
    Refresh access token using stored refresh token.
    
    **How it works:**
    - Refresh token is sent automatically via HttpOnly cookie from /auth/login
    - Returns new access token (short-lived: 15 minutes)
    - Refresh token remains valid for 7 days
    
    **Errors:**
    - 401 Missing refresh token in cookie
    - 401 Refresh token expired
    - 401 Invalid refresh token
    """
    if not refresh_token:
        logger.warning("Refresh token missing from cookie")
        raise HTTPException(status_code=401, detail="Missing refresh token in cookie")

    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Refresh token expired")
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid refresh token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(payload["sub"])
    logger.info(f"Access token refreshed for user: {payload['sub']}")
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/signup", response_model=MessageResponse)
def signup(
    data: SignupRequest,
    session: Session = Depends(get_session),
):
    """
    User registration endpoint - Creates new user account.
    
    **What happens:**
    - Creates user with bcrypt-hashed password
    - Creates or reuses organization
    - Assigns role (buyer, seller, auditor, bank)
    
    **Next step:** Use /auth/login to authenticate with new credentials
    
    **Errors:**
    - 400 User already exists: Email already registered
    - 400 Invalid password: Password too long (>72 bytes)
    - 400 Invalid role: Must be buyer, seller, auditor, or bank
    """
    logger.info(f"Signup attempt for email: {data.email}")
    try:
        user = create_user(session, data)
        logger.info(f"User created successfully: {data.email}")
    except ValueError as e:
        logger.warning(f"Signup failed for email: {data.email}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Account created successfully. Please login with your credentials."}


@router.get("/user", response_model=UserResponse)
def get_user(user: User = Depends(get_current_user_from_token)):
    """
    Get current authenticated user details.
    
    **Required header:**
    - Authorization: Bearer {access_token}
    
    **Returns:**
    - User ID, name, email, role, organization
    
    **Errors:**
    - 401 Missing authorization header
    - 401 Invalid token format (must be "Bearer {token}")
    - 401 Token expired
    - 401 Invalid token
    """
    logger.info(f"Fetching user details for: {user.email}")
    return user
