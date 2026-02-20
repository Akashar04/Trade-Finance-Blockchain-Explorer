from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    bank = "bank"
    corporate = "corporate"
    auditor = "auditor"
    admin = "admin"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    org_name: str
    role: UserRole


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    org_name: str
    role: UserRole

    model_config = {
        "from_attributes": True
    }

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    role: str


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    org_name: str
    role: str

    class Config:
        from_attributes = True


class RiskScoreResponse(BaseModel):
    transaction_id: int
    score: float
    risk_level: str
    reasons: list[str]

