from sqlmodel import Session, select
from passlib.context import CryptContext
from app.db.models import User, Organization

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # Bcrypt has a maximum password length of 72 bytes
    # Truncate at the byte level, then decode safely to avoid breaking multi-byte UTF-8 characters
    password_bytes = password.encode("utf-8")[:72]
    safe_password = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Apply same 72-byte truncation for consistency
    password_bytes = plain_password.encode("utf-8")[:72]
    safe_password = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.verify(safe_password, hashed_password)


def authenticate_user(session: Session, email: str, password: str):
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user
def create_user(session, data):
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()
    if existing_user:
        raise ValueError("User already exists")

    # Get or create organization
    organization = session.exec(
        select(Organization).where(Organization.name == data.org)
    ).first()

    if not organization:
        organization = Organization(name=data.org)
        session.add(organization)
        session.commit()
        session.refresh(organization)

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        organization_id=organization.id,
    )

    session.add(user)
    session.commit()

    return user