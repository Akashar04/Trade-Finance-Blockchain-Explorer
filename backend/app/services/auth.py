from sqlmodel import Session, select
from passlib.context import CryptContext
from app.db.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(session: Session, email: str, password: str):
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user
