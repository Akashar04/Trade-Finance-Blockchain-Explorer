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
    documents: List["Document"] = Relationship(back_populates="owner")
    ledger_entries: List["LedgerEntry"] = Relationship(back_populates="actor")


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    doc_number: str = Field(index=True)
    file_url: str
    hash: str

    doc_type: str  # PO, BOL, LOC, INVOICE

    owner_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates="documents")
    ledger_entries: List["LedgerEntry"] = Relationship(back_populates="document")


class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    doc_id: int = Field(foreign_key="document.id")
    actor_id: int = Field(foreign_key="user.id")

    action: str  # ISSUED, SHIPPED, RECEIVED, VERIFIED, PAID, ISSUE_LOC, ISSUE_INVOICE

    entry_metadata: Optional[str] = Field(default=None)  # JSON stored as string

    created_at: datetime = Field(default_factory=datetime.utcnow)

    document: Optional[Document] = Relationship(back_populates="ledger_entries")
    actor: Optional[User] = Relationship(back_populates="ledger_entries")
