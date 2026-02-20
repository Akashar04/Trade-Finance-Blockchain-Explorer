from sqlalchemy.orm import Session
from .. import models

def log_action(db: Session, user_id: int, action: str, entity_type: str, entity_id: int):
    """
    Helper function to create an audit log entry.
    """
    try:
        log = models.AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Failed to create audit log: {e}")
        # Non-blocking error for audit logging? 
        # Usually we want to at least log to console if DB fails
        pass
