from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Numeric, TIMESTAMP, JSON, CHAR, Text
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime


# ==============================
# ENUMS
# ==============================

class UserRole(str, enum.Enum):
    bank = "bank"
    corporate = "corporate"
    auditor = "auditor"
    admin = "admin"


class DocumentType(str, enum.Enum):
    PO = "PO"
    INVOICE = "INVOICE"
    BILL_OF_LADING = "BILL_OF_LADING"
    LOC = "LOC"
    COO = "COO"
    INSURANCE_CERT = "INSURANCE_CERT"


class TransactionStatus(str, enum.Enum):
    PO_CREATED = "PO_CREATED"
    PO_APPROVED = "PO_APPROVED"
    PO_SHIPPED = "PO_SHIPPED"
    PO_COMPLETED = "PO_COMPLETED"


class LedgerAction(str, enum.Enum):
    PO_CREATED = "PO_CREATED"
    PO_APPROVED = "PO_APPROVED"
    PO_SHIPPED = "PO_SHIPPED"
    PO_COMPLETED = "PO_COMPLETED"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    VERIFIED = "VERIFIED"



# ==============================
# TABLES
# ==============================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(Enum(UserRole))
    org_name = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class TradeTransaction(Base):
    __tablename__ = "trade_transactions"

    id = Column(Integer, primary_key=True, index=True)

    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))

    amount = Column(Numeric)
    currency = Column(CHAR(3))

    status = Column(Enum(TransactionStatus), default=TransactionStatus.PO_CREATED)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)

    documents = relationship("Document", backref="transaction", cascade="all, delete")
    ledger_entries = relationship("LedgerEntry", backref="transaction", cascade="all, delete")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    transaction_id = Column(Integer, ForeignKey("trade_transactions.id"))

    doc_type = Column(Enum(DocumentType))
    doc_number = Column(String)

    file_url = Column(String)
    hash = Column(String)

    issued_at = Column(TIMESTAMP, default=datetime.utcnow)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # 🔵 NEW FIELDS
    is_verified = Column(Integer, default=0)  # 0 = False, 1 = True
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(TIMESTAMP, nullable=True)


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(Integer, ForeignKey("trade_transactions.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    actor_id = Column(Integer, ForeignKey("users.id"))

    action = Column(Enum(LedgerAction))
    details = Column(JSON)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Numeric)
    risk_level = Column(String)  # LOW, MEDIUM, HIGH
    rationale = Column(JSON)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
