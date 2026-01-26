import sys
import os
from sqlmodel import Session, create_engine, select
from datetime import datetime
import json

# Add backend to path
sys.path.append(os.getcwd())

from app.db.models import User, Document, LedgerEntry
from app.core.config import settings

# Setup DB
engine = create_engine(settings.DATABASE_URL)

def debug_insert():
    with Session(engine) as session:
        # Get a user
        user = session.exec(select(User)).first()
        if not user:
            print("No user found, cannot test.")
            return

        print(f"Testing with user: {user.email} (id={user.id})")

        # Mock data
        doc_number = "TEST-DOC-001"
        safe_filename = "TEST-DOC-001_test.pdf"
        file_hash = "dummyhash123"
        seller_id = 999
        
        # Try creating a User to see if DB works
        print("Creating Test User...")
        try:
            import random
            rand_email = f"debug_{random.randint(1000,9999)}@test.com"
            test_user = User(
                name="Debug User",
                email=rand_email,
                hashed_password="hash",
                role="buyer",
                organization_id=user.organization_id # Reuse org
            )
            session.add(test_user)
            session.commit()
            print("User created successfully!")
            
            # Now try Document again? 
            # No, let's just exit to confirm User works.
            return
            
        except Exception as e:
            print(f"User creation failed: {e}")
            import traceback
            traceback.print_exc()
            print("Committed. Refreshing...")
            session.refresh(document)
            print(f"Document ID: {document.id}")
            
            # Ledger Entry
            metadata = json.dumps({"seller_id": seller_id})
            print(f"Creating LedgerEntry with metadata: {metadata}")
            
            entry = LedgerEntry(
                doc_id=document.id,
                actor_id=user.id,
                action="ISSUED",
                entry_metadata=metadata
            )
            session.add(entry)
            session.commit()
            print("LedgerEntry committed.")
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_insert()
