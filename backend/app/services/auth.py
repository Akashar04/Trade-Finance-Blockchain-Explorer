from sqlmodel import Session, select

from app.db.models import User, Organization
import logging

logger = logging.getLogger(__name__)

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Bcrypt has a 72-byte limit on the input password provided to it.
    However, we are simply passing the password to bcrypt directly as requested.
    
    Args:
        password: Plain text password from signup form
        
    Returns:
        Hashed password string
    """
    # bcrypt.hashpw requires bytes for both password and salt
    # We return a string for storage compatibility
    cwd = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(cwd, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain text password against hashed password.
    
    Uses bcrypt's timing-safe comparison.
    
    Args:
        plain_password: Plain text password from login form
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # bcrypt.checkpw requires bytes
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def authenticate_user(session: Session, email: str, password: str) -> dict:
    """
    Authenticate user by email and password.
    
    Returns detailed error reason for Swagger clarity.
    
    Args:
        session: Database session
        email: User email
        password: Plain text password from login form (NOT hashed)
        
    Returns:
        {
            "success": bool,
            "user": User | None,
            "reason": "user_not_found" | "invalid_password" | None
        }
    """
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        return {"success": False, "user": None, "reason": "user_not_found"}
    
    if not verify_password(password, user.hashed_password):
        return {"success": False, "user": None, "reason": "invalid_password"}

    return {"success": True, "user": user, "reason": None}


def create_user(session, data):
    """
    Create a new user with hashed password.
    
    Args:
        session: Database session
        data: SignupRequest with name, email, password, org, role
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If user already exists or validation fails
    """
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

    # Hash password ONCE during signup
    hashed_password = hash_password(data.password)

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hashed_password,  # Store hashed password
        role=data.role,
        organization_id=organization.id,
    )

    session.add(user)
    session.commit()

    logger.info(f"User created: {data.email} with role {data.role}")
    return user
