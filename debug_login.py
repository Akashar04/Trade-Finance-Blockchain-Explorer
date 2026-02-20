from sqlalchemy import create_engine, inspect, text
from app.database import engine, SessionLocal
from app import models
from sqlalchemy.orm import sessionmaker

def check_db():
    # engine is already imported
    inspector = inspect(engine)

    print("--- UserRole Enum ---")
    with engine.connect() as conn:
        try:
            # Check Postgres enum values
            result = conn.execute(text("SELECT unnest(enum_range(NULL::userrole))"))
            print([row[0] for row in result])
        except Exception as e:
            print(f"Error checking enum: {e}")

    print("\n--- Users Table ---")
    columns = inspector.get_columns('users')
    for col in columns:
        print(f"Column: {col['name']} - Type: {col['type']} - Nullable: {col['nullable']}")

    print("\n--- Audit Logs Table ---")
    if 'audit_logs' in inspector.get_table_names():
        print("Dropping existing audit_logs table...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE audit_logs CASCADE"))
            conn.commit()
    
    print("Recreating tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Tables recreated.")

    print("\n--- Testing Login with Default User ---")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        # Check if audit log insert works
        print("Attempting to insert AuditLog...")
        try:
            log = models.AuditLog(
                user_id=1,
                action="TEST_LOGIN",
                entity_type="USER",
                entity_id=1
            )
            db.add(log)
            db.commit()
            print("AuditLog insert SUCCESS")
        except Exception as e:
            print(f"AuditLog insert FAILED: {e}")
            db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
