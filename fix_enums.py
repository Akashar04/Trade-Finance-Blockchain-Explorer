import sys
import os
sys.path.append(os.getcwd())

from app.database import engine
from sqlalchemy import text

def fix_enums():
    with engine.connect() as conn:
        print("Fixing UserRole enum...")
        try:
            conn.execute(text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin';"))
            conn.execute(text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'auditor';"))
            conn.commit()
            print("Successfully added 'admin' and 'auditor' to userrole enum.")
        except Exception as e:
            print(f"Error updating enum: {e}")

if __name__ == "__main__":
    fix_enums()
