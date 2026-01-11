from datetime import datetime, timedelta
import jwt
from app.core.config import settings


def create_access_token(subject: str) -> str:
    payload = {
        "sub": subject,
        "exp": datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(subject: str) -> str:
    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
