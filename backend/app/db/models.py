from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class Organization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    users: List["User"] = Relationship(back_populates="organization")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str                                # NEW
    email: str = Field(index=True, unique=True)
    hashed_password: str

    role: str                                # NEW
    is_active: bool = Field(default=True)

    organization_id: Optional[int] = Field(
        default=None, foreign_key="organization.id"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    organization: Optional[Organization] = Relationship(back_populates="users")
