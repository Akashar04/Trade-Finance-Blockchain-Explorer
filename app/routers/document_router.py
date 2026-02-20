from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime

from ..deps import get_db, get_current_user
from .. import models
from ..auth import calculate_file_hash

router = APIRouter()

UPLOAD_DIR = "files"


# ==============================
# UPLOAD DOCUMENT
# ==============================

@router.post("/upload")
def upload_document(
    transaction_id: int = Form(...),
    doc_number: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Convert doc_type string to enum
    doc_type = models.DocumentType(doc_type)
    
    # 1️⃣ Validate transaction exists
    transaction = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # 2️⃣ Prevent upload if transaction completed
    if transaction.status == models.TransactionStatus.PO_COMPLETED:
        raise HTTPException(status_code=400, detail="Transaction already completed")

    # 3️⃣ Prevent duplicate document per transaction
    existing_doc = db.query(models.Document).filter(
        models.Document.transaction_id == transaction_id,
        models.Document.doc_number == doc_number,
        models.Document.doc_type == doc_type
    ).first()

    if existing_doc:
        raise HTTPException(
            status_code=400,
            detail="Document with this number already exists for this transaction"
        )

    # 4️⃣ Read file
    file_bytes = file.file.read()

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    file_hash = calculate_file_hash(file_bytes)

    # 5️⃣ Create document linked to transaction
    new_doc = models.Document(
        owner_id=current_user.id,
        transaction_id=transaction_id,
        doc_type=doc_type,
        doc_number=doc_number,
        file_url=unique_name,
        hash=file_hash
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # 6️⃣ Ledger entry
    ledger_entry = models.LedgerEntry(
        document_id=new_doc.id,
        actor_id=current_user.id,
        action=models.LedgerAction.DOCUMENT_UPLOADED,
        details={
            "transaction_id": transaction_id,
            "doc_type": doc_type.value
        }
    )

    db.add(ledger_entry)
    db.commit()

    return {
        "document_id": new_doc.id,
        "transaction_id": transaction_id,
        "hash": file_hash
    }


# ==============================
# GET DOCUMENT + LEDGER
# ==============================

@router.get("/document")
def get_document(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    document = db.query(models.Document).filter(
        models.Document.id == id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    ledger_entries = db.query(models.LedgerEntry).filter(
        models.LedgerEntry.document_id == id
    ).all()

    return {
        "document": {
            "id": document.id,
            "doc_type": document.doc_type.value if hasattr(document.doc_type, "value") else document.doc_type,
            "doc_number": document.doc_number,
            "file_url": document.file_url,
            "hash": document.hash,
            "created_at": document.created_at.isoformat() if document.created_at else None
        },
        "ledger": [
            {
                "id": entry.id,
                "action": entry.action.value if hasattr(entry.action, "value") else entry.action,
                "actor_id": entry.actor_id,
                "details": entry.details,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            }
            for entry in ledger_entries
        ]
    }

@router.post("/document/{document_id}/verify")
def verify_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    if current_user.role != models.UserRole.bank:
        raise HTTPException(status_code=403, detail="Only bank can verify documents")

    document = db.query(models.Document).filter(
        models.Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.is_verified:
        raise HTTPException(status_code=400, detail="Document already verified")

    document.is_verified = 1
    document.verified_by = current_user.id
    document.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(document)

    ledger = models.LedgerEntry(
        transaction_id=document.transaction_id,
        document_id=document.id,
        actor_id=current_user.id,
        action=models.LedgerAction.VERIFIED,
        details={"document_id": document.id}
    )

    db.add(ledger)
    db.commit()

    from ..services.audit_service import log_action
    log_action(db, current_user.id, "VERIFIED", "DOCUMENT", document.id)

    return {
        "document_id": document.id,
        "status": "VERIFIED"
    }

