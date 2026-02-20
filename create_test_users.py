import sys
import os
sys.path.append(os.getcwd())

from app.database import engine, SessionLocal
from app.models import Base, User, UserRole
from app.auth import hash_password

def create_test_users():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if users already exist
    existing_bank = db.query(User).filter(User.email == "bank@example.com").first()
    existing_corp = db.query(User).filter(User.email == "corporate@example.com").first()
    existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
    
    if not existing_bank:
        bank_user = User(
            name="Bank Officer",
            email="bank@example.com",
            password=hash_password("password123"),
            role=UserRole.bank,
            org_name="Global Bank Corp"
        )
        db.add(bank_user)
        print("✓ Created bank@example.com")
    else:
        print("• bank@example.com already exists")
    
    if not existing_corp:
        corp_user = User(
            name="Corporate Buyer",
            email="corporate@example.com",
            password=hash_password("password123"),
            role=UserRole.corporate,
            org_name="TechCorp Industries"
        )
        db.add(corp_user)
        print("✓ Created corporate@example.com")
    else:
        print("• corporate@example.com already exists")
    
    if not existing_admin:
        admin_user = User(
            name="System Administrator",
            email="admin@example.com",
            password=hash_password("password123"),
            role=UserRole.admin,
            org_name="Trade Finance System"
        )
        db.add(admin_user)
        print("✓ Created admin@example.com")
    else:
        print("• admin@example.com already exists")
    
    db.commit()
    db.close()
    print("\nTest users ready!")

if __name__ == "__main__":
    create_test_users()
