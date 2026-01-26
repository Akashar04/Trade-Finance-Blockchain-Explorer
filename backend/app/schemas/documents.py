from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class DocumentResponse(BaseModel):
    id: int
    doc_number: str
    file_url: str
    hash: str
    doc_type: str
    owner_id: int
    created_at: datetime
    
    owner_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class LedgerEntryResponse(BaseModel):
    id: int
    doc_id: int
    actor_id: int
    action: str
    entry_metadata: Optional[str] = None
    created_at: datetime
    
    actor_name: Optional[str] = None

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    ledger_entries: List[LedgerEntryResponse]

class ActionRequest(BaseModel):
    doc_id: int
    action: str
    metadata: Optional[str] = None  # JSON string if needed
