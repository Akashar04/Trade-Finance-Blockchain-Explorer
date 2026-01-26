from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from typing import List
import shutil
from pathlib import Path
import hashlib
import json

from app.db.session import get_session
from app.db.models import User, Document, LedgerEntry, Organization
from app.api.routes.auth import get_current_user_from_token
from app.schemas.documents import DocumentResponse, DocumentDetailResponse, ActionRequest, LedgerEntryResponse

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=DocumentDetailResponse)
def upload_document(
    file: UploadFile = File(...),
    doc_number: str = Form(...),
    seller_id: int = Form(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """
    Buyer uploads a Purchase Order (PO) to initiate trade.
    """
    # 1. Save file
    safe_filename = f"{doc_number}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Calculate hash
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
        
    # 3. Create Document
    # Only Buyer can start flow with PO? User request implies "As as buyer... upload PO"
    # But let's allow upload, policy check logic can be added if needed.
    if current_user.role != "buyer":
         raise HTTPException(status_code=403, detail="Only buyers can initiate trade with PO upload")

    print(f"DEBUG: Creating Document: doc_number={doc_number}, file_url={safe_filename}, hash={file_hash}, owner_id={current_user.id}")
    document = Document(
        doc_number=doc_number,
        file_url=safe_filename,
        hash=file_hash,
        doc_type="PO",
        owner_id=current_user.id
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    print(f"DEBUG: Document Created: id={document.id}")
    
    # 4. Create Ledger Entry (ISSUED)
    # Metadata includes seller_id so seller knows it's for them
    metadata = json.dumps({"seller_id": seller_id})
    print(f"DEBUG: Creating LedgerEntry: doc_id={document.id}, actor_id={current_user.id}, metadata={metadata}")
    
    entry = LedgerEntry(
        doc_id=document.id,
        actor_id=current_user.id,
        action="ISSUED",
        entry_metadata=metadata
    )
    session.add(entry)
    session.commit()
    
    # Refresh to get relationships
    session.refresh(document)
    return document

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """
    List all documents relevant to the user.
    Simplicity: Show all documents for now, or filter by involvement.
    Real world: Filter where user is owner OR user is referenced in ledger/metadata.
    """
    # Filter documents based on role
    query = select(Document)
    if current_user.role == "buyer":
        # Buyers only see their own documents
        query = query.where(Document.owner_id == current_user.id)
        
    documents = session.exec(query).all()
    
    response_list = []
    for doc in documents:
        # Create Pydantic model from DB object
        doc_resp = DocumentResponse.model_validate(doc)
        # Enrich with owner name
        doc_resp.owner_name = doc.owner.name if doc.owner else "Unknown"
        response_list.append(doc_resp)
        
    return response_list

@router.get("/{id}", response_model=DocumentDetailResponse)
def get_document(
    id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_from_token),
):
    print(f"DEBUG: Fetching document with ID: {id}")
    document = session.get(Document, id)
    if not document:
        print(f"DEBUG: Document {id} NOT FOUND in DB.")
        raise HTTPException(status_code=404, detail=f"Document {id} not found")
        
    # Create Pydantic response
    doc_resp = DocumentDetailResponse.model_validate(document)
    
    # Enrich entries with actor name
    for i, entry in enumerate(document.ledger_entries):
        if entry.actor:
            # We need to ensure the response model has actor_name
            # Since ledger_entries in doc_resp are already verified via model_validate, 
            # they are LedgerEntryResponse objects, so we can set actor_name.
            doc_resp.ledger_entries[i].actor_name = entry.actor.name
            
    doc_resp.owner_name = document.owner.name if document.owner else "Unknown"

    # Sort entries by time
    doc_resp.ledger_entries.sort(key=lambda x: x.created_at)
    
    return doc_resp

@router.post("/action", response_model=LedgerEntryResponse)
def perform_action(
    req: ActionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """
    Handle state transitions based on Role and Document Type.
    """
    doc = session.get(Document, req.doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    role = current_user.role
    doc_type = doc.doc_type
    action = req.action
    
    # Policy Check
    allowed = False
    
    # buyer PO AMEND
    if role == "buyer" and doc_type == "PO" and action == "AMEND":
        allowed = True

    # buyer BOL RECEIVED
    elif role == "buyer" and doc_type == "BOL" and action == "RECEIVED":
        allowed = True
        
    # seller BOL SHIPPED
    elif role == "seller" and doc_type == "BOL" and action == "SHIPPED":
        allowed = True
        
    # seller PO ISSUE_BOL
    elif role == "seller" and doc_type == "PO" and action == "ISSUE_BOL":
        allowed = True
    # seller LOC ISSUE_BOL (If flow was PO -> LOC)
    elif role == "seller" and doc_type == "LOC" and action == "ISSUE_BOL":
        allowed = True
    
    # seller BOL ISSUE_INVOICE
    elif role == "seller" and doc_type == "BOL" and action == "ISSUE_INVOICE":
        allowed = True
        
    # auditor PO VERIFY
    elif role == "auditor" and doc_type == "PO" and action == "VERIFY":
        allowed = True
        
    # auditor LOC VERIFY
    elif role == "auditor" and doc_type == "LOC" and action == "VERIFY":
        allowed = True
        
    # bank INVOICE PAID
    elif role == "bank" and doc_type == "INVOICE" and action == "PAID":
        allowed = True
        
    # bank PO ISSUE_LOC
    elif role == "bank" and doc_type == "PO" and action == "ISSUE_LOC":
        allowed = True

    # Corrections for ambiguous requirements
    # bank LOC ISSUE_LOC (If they re-issue or amend?)
    elif role == "bank" and doc_type == "LOC" and action == "ISSUE_LOC":
        allowed = True
    
    if not allowed:
        raise HTTPException(status_code=403, detail=f"Action '{action}' not allowed for role '{role}' on document '{doc_type}'")
        
    # Create Ledger Entry
    entry = LedgerEntry(
        doc_id=doc.id,
        actor_id=current_user.id,
        action=action,
        entry_metadata=req.metadata
    )
    session.add(entry)
    
    # State Transitions (Simulating lifecycle linear flow)
    print(f"DEBUG: Processing action {action} on doc_type {doc.doc_type}")
    
    if action == "ISSUE_LOC" and doc.doc_type == "PO":
        print(f"DEBUG: Transitioning Doc {doc.id} from PO to LOC")
        doc.doc_type = "LOC"
        session.add(doc)
        
    elif action == "ISSUE_BOL" and (doc.doc_type == "PO" or doc.doc_type == "LOC"):
        print(f"DEBUG: Transitioning Doc {doc.id} from {doc.doc_type} to BOL")
        doc.doc_type = "BOL"
        session.add(doc)
        
    elif action == "ISSUE_INVOICE" and doc.doc_type == "BOL":
        print(f"DEBUG: Transitioning Doc {doc.id} from BOL to INVOICE")
        doc.doc_type = "INVOICE"
        session.add(doc)

    session.commit()
    session.refresh(entry)
    
    return entry
