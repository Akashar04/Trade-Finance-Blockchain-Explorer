import hashlib
import json
from typing import Optional, Dict, List
from sqlmodel import Session, select
from app.db.models import Document, LedgerEntry, User


def compute_file_hash(file_content: bytes) -> str:
    """Compute SHA-256 hash of file content"""
    return hashlib.sha256(file_content).hexdigest()


def create_document(
    session: Session,
    doc_number: str,
    file_url: str,
    file_hash: str,
    doc_type: str,
    owner_id: int,
) -> Document:
    """Create a new document in database"""
    document = Document(
        doc_number=doc_number,
        file_url=file_url,
        hash=file_hash,
        doc_type=doc_type,
        owner_id=owner_id,
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def create_ledger_entry(
    session: Session,
    doc_id: int,
    actor_id: int,
    action: str,
    metadata: Optional[Dict] = None,
) -> LedgerEntry:
    """Create a new ledger entry"""
    metadata_str = json.dumps(metadata) if metadata else None
    entry = LedgerEntry(
        doc_id=doc_id,
        actor_id=actor_id,
        action=action,
        entry_metadata=metadata_str,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def get_document_with_ledger(session: Session, doc_id: int) -> Optional[Document]:
    """Get document with all its ledger entries"""
    statement = (
        select(Document)
        .where(Document.id == doc_id)
    )
    return session.exec(statement).first()


def get_user_documents(session: Session, user_id: int) -> List[Document]:
    """Get all documents for a user"""
    statement = select(Document).where(Document.owner_id == user_id)
    return session.exec(statement).all()


# Access control mapping: role -> document_type -> allowed_actions
ACCESS_MAPPING = {
    "buyer": {
        "BOL": ["RECEIVED"],
    },
    "seller": {
        "BOL": ["SHIPPED"],
        "PO": ["ISSUE_BOL"],
        "BOL": ["ISSUE_INVOICE"],
    },
    "auditor": {
        "PO": ["VERIFY"],
        "LOC": ["VERIFY"],
    },
    "bank": {
        "INVOICE": ["PAID"],
        "LOC": ["ISSUE_LOC"],
    },
}


def validate_action(user_role: str, doc_type: str, action: str) -> bool:
    """Validate if user can perform this action on document"""
    if user_role not in ACCESS_MAPPING:
        return False

    role_perms = ACCESS_MAPPING[user_role]
    if doc_type not in role_perms:
        return False

    return action in role_perms[doc_type]


def get_last_ledger_state(session: Session, doc_id: int) -> Optional[str]:
    """Get the last action performed on a document"""
    statement = (
        select(LedgerEntry)
        .where(LedgerEntry.doc_id == doc_id)
        .order_by(LedgerEntry.created_at.desc())
    )
    last_entry = session.exec(statement).first()
    return last_entry.action if last_entry else None
