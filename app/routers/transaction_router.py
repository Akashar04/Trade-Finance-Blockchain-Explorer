from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from .. import models
from ..services.risk_service import calculate_risk
import uuid
import os
from ..config import UPLOAD_DIR
from ..auth import calculate_file_hash


router = APIRouter(
    prefix="/transaction",
    tags=["transaction"]
)

# ==============================
# CREATE PO
# ==============================

@router.post("/create_po")
def create_purchase_order(
    doc_number: str = Form(...),
    amount: float = Form(...),
    currency: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    if current_user.role != models.UserRole.corporate:
        raise HTTPException(status_code=403, detail="Only corporate can create PO")

    existing_doc = db.query(models.Document).filter(
        models.Document.doc_number == doc_number,
        models.Document.doc_type == models.DocumentType.PO
    ).first()

    if existing_doc:
        raise HTTPException(status_code=400, detail="PO with this number already exists")

    transaction = models.TradeTransaction(
        buyer_id=current_user.id,
        amount=amount,
        currency=currency,
        status=models.TransactionStatus.PO_CREATED
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    file_bytes = file.file.read()
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    file_hash = calculate_file_hash(file_bytes)

    document = models.Document(
        owner_id=current_user.id,
        transaction_id=transaction.id,
        doc_type=models.DocumentType.PO,
        doc_number=doc_number,
        file_url=unique_name,
        hash=file_hash
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    ledger = models.LedgerEntry(
        transaction_id=transaction.id,
        document_id=document.id,
        actor_id=current_user.id,
        action=models.LedgerAction.PO_CREATED,
        details={"transaction_id": transaction.id}
    )

    db.add(ledger)
    db.commit()

    from ..services.audit_service import log_action
    log_action(db, current_user.id, "PO_CREATED", "TRANSACTION", transaction.id)

    return {
        "transaction_id": transaction.id,
        "status": transaction.status.value
    }


# ==============================
# APPROVE
# ==============================

@router.post("/{transaction_id}/approve")
def approve_transaction(transaction_id: int,
                        db: Session = Depends(get_db),
                        current_user: models.User = Depends(get_current_user)):

    if current_user.role != models.UserRole.bank:
        raise HTTPException(status_code=403, detail="Only bank can approve PO")

    transaction = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.status != models.TransactionStatus.PO_CREATED:
        raise HTTPException(status_code=400, detail="Invalid transaction state")

    transaction.status = models.TransactionStatus.PO_APPROVED
    db.commit()
    db.refresh(transaction)

    db.add(models.LedgerEntry(
        transaction_id=transaction.id,
        actor_id=current_user.id,
        action=models.LedgerAction.PO_APPROVED,
        details={"transaction_id": transaction.id}
    ))
    db.commit()

    return {
        "transaction_id": transaction.id,
        "status": transaction.status.value
    }


# ==============================
# SHIP
# ==============================

@router.post("/{transaction_id}/ship")
def ship_transaction(transaction_id: int,
                     db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):

    if current_user.role != models.UserRole.corporate:
        raise HTTPException(status_code=403, detail="Only corporate can ship")

    transaction = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.status != models.TransactionStatus.PO_APPROVED:
        raise HTTPException(status_code=400, detail="Must be approved first")

    transaction.status = models.TransactionStatus.PO_SHIPPED
    db.commit()
    db.refresh(transaction)

    db.add(models.LedgerEntry(
        transaction_id=transaction.id,
        actor_id=current_user.id,
        action=models.LedgerAction.PO_SHIPPED,
        details={"transaction_id": transaction.id}
    ))
    db.commit()

    return {
        "transaction_id": transaction.id,
        "status": transaction.status.value
    }


# ==============================
# COMPLETE (WITH DOC CHECK + RISK)
# ==============================

# ==============================
# COMPLETE (WITH DOC CHECK + RISK)
# ==============================

@router.post("/{transaction_id}/complete")
def complete_transaction(transaction_id: int,
                         db: Session = Depends(get_db),
                         current_user: models.User = Depends(get_current_user)):

    # Fix 500 Error: Wrap in try/except and fix is_verified check
    try:
        if current_user.role != models.UserRole.bank:
            raise HTTPException(status_code=403, detail="Only bank can complete")

        transaction = db.query(models.TradeTransaction).filter(
            models.TradeTransaction.id == transaction_id
        ).first()

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if transaction.status != models.TransactionStatus.PO_SHIPPED:
            raise HTTPException(status_code=400, detail="Must be shipped first")

        required_docs = {
            models.DocumentType.PO,
            models.DocumentType.INVOICE,
            models.DocumentType.BILL_OF_LADING
        }

        # Fix: Compare is_verified to 1 (Integer) instead of True (Boolean)
        documents = db.query(models.Document).filter(
            models.Document.transaction_id == transaction.id,
            models.Document.is_verified == 1
        ).all()

        uploaded_types = {doc.doc_type for doc in documents}
        missing_docs = required_docs - uploaded_types

        if missing_docs:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required documents: {[doc.value for doc in missing_docs]}"
            )

        transaction.status = models.TransactionStatus.PO_COMPLETED
        db.commit()
        db.refresh(transaction)

        db.add(models.LedgerEntry(
            transaction_id=transaction.id,
            actor_id=current_user.id,
            action=models.LedgerAction.PO_COMPLETED,
            details={"transaction_id": transaction.id}
        ))
        db.commit()

        # 🔵 Risk Calculation
        all_docs = db.query(models.Document).filter(
            models.Document.transaction_id == transaction.id
        ).all()

        score, risk_level, reasons = calculate_risk(transaction, all_docs, db)

        db.add(models.RiskScore(
            user_id=transaction.buyer_id,
            score=score,
            risk_level=risk_level,
            rationale=reasons
        ))
        db.commit()

        from ..services.audit_service import log_action
        log_action(db, current_user.id, "PO_COMPLETED", "TRANSACTION", transaction.id)

        return {
            "transaction_id": transaction.id,
            "status": transaction.status.value,
            "risk_score": score,
            "risk_level": risk_level,
            "reasons": reasons
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        # In production, log this error
        print(f"CRITICAL ERROR in complete_transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Use proper backend logs. Error: {str(e)}")


# ==============================
# LIST TRANSACTIONS (CORPORATE)
# ==============================

@router.get("/my/list")
def list_my_transactions(db: Session = Depends(get_db),
                         current_user: models.User = Depends(get_current_user)):
    
    if current_user.role != models.UserRole.corporate:
        raise HTTPException(status_code=403, detail="Only corporate can access")
    
    transactions = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.buyer_id == current_user.id
    ).all()

    return [
        {
            "id": tx.id,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "status": tx.status.value,
            "created_at": tx.created_at.isoformat() if tx.created_at else None
        }
        for tx in transactions
    ]


# ==============================
# LIST PENDING TRANSACTIONS (BANK)
# ==============================

@router.get("/bank/pending")
def list_pending_transactions(db: Session = Depends(get_db),
                              current_user: models.User = Depends(get_current_user)):
    
    if current_user.role != models.UserRole.bank:
        raise HTTPException(status_code=403, detail="Only bank can access")
    
    transactions = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.status.in_([
            models.TransactionStatus.PO_CREATED,
            models.TransactionStatus.PO_SHIPPED
        ])
    ).all()

    return [
        {
            "id": tx.id,
            "buyer_id": tx.buyer_id,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "status": tx.status.value,
            "created_at": tx.created_at.isoformat() if tx.created_at else None
        }
        for tx in transactions
    ]


# ==============================
# TRANSACTION SUMMARY
# ==============================


# ==============================
# LIST ALL TRANSACTIONS (ADMIN/AUDITOR)
# ==============================

@router.get("/all")
def list_all_transactions(db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    
    if current_user.role not in [models.UserRole.admin, models.UserRole.auditor]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    transactions = db.query(models.TradeTransaction).all()

    return [
        {
            "id": tx.id,
            "buyer_id": tx.buyer_id,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "status": tx.status.value,
            "created_at": tx.created_at.isoformat() if tx.created_at else None
        }
        for tx in transactions
    ]


@router.get("/{transaction_id}")
def get_transaction_summary(transaction_id: int,
                            db: Session = Depends(get_db),
                            current_user: models.User = Depends(get_current_user)):

    transaction = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    documents = db.query(models.Document).filter(
        models.Document.transaction_id == transaction_id
    ).all()

    ledger_entries = db.query(models.LedgerEntry).filter(
        models.LedgerEntry.transaction_id == transaction_id
    ).order_by(models.LedgerEntry.created_at.asc()).all()

    response_data = {
        "transaction": {
            "id": transaction.id,
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status.value
        },
        "documents": [
            {
                "id": doc.id,
                "doc_type": doc.doc_type.value,
                "doc_number": doc.doc_number,
                "is_verified": doc.is_verified
            }
            for doc in documents
        ],
        "ledger": [
            {
                "action": entry.action.value,
                "actor_id": entry.actor_id,
                "details": entry.details,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            }
            for entry in ledger_entries
        ]
    }

    # Fetch latest risk score for this buyer
    risk_entry = db.query(models.RiskScore).filter(
        models.RiskScore.user_id == transaction.buyer_id
    ).order_by(models.RiskScore.last_updated.desc()).first()

    if risk_entry:
        response_data["risk_info"] = {
            "score": float(risk_entry.score),
            "level": risk_entry.risk_level,
            "reasons": risk_entry.rationale
        }
    
    return response_data

@router.post("/generate-risk/{transaction_id}")
def generate_risk_manual(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    if current_user.role != models.UserRole.bank:
        raise HTTPException(status_code=403, detail="Only bank allowed")

    transaction = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    documents = db.query(models.Document).filter(
        models.Document.transaction_id == transaction.id
    ).all()

    from ..services.risk_service import calculate_risk
    score, risk_level, reasons = calculate_risk(transaction, documents, db)

    # Check if risk score exists for this transaction (or just add new one? Model has user_id, arguably should be transaction linked but we follow existing pattern instructions say 'Store: score, risk_level, rationale')
    # existing code used user_id=transaction.buyer_id. I will keep that but it seems odd for transaction risk. 
    # Requirement: "Store: score, risk_level, rationale (JSON array)"
    
    # Let's check if we should update or add. Logic below just adds.
    risk = models.RiskScore(
        user_id=transaction.buyer_id,
        score=score,
        risk_level=risk_level,
        rationale=reasons
    )

    db.add(risk)
    db.commit()

    return {
        "transaction_id": transaction.id,
        "score": score,
        "risk_level": risk_level,
        "reasons": reasons
    }
