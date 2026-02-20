from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..deps import get_current_user
from .. import models

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/analytics")
def get_admin_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [models.UserRole.admin, models.UserRole.auditor]:
        raise HTTPException(status_code=403, detail="Access denied")

    total = db.query(models.TradeTransaction).count()
    
    completed = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.status == models.TransactionStatus.PO_COMPLETED
    ).count()

    pending = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.status != models.TransactionStatus.PO_COMPLETED
    ).count()

    # Risk analytics
    # "High Risk" defined as >= 70 (as per requirement example) or "HIGH" level
    # Using 'HIGH' string from RiskScore.risk_level as it is consistent with other parts
    # But prompt example used score >= 70. I'll check both or adhere to prompt logic.
    # Prompt: high_risk = db.query(RiskScore).filter(RiskScore.score >= 70).count()
    high_risk = db.query(models.RiskScore).filter(
        models.RiskScore.score >= 70
    ).count()

    avg_score = db.query(func.avg(models.RiskScore.score)).scalar() or 0

    return {
        "total_transactions": total,
        "completed_transactions": completed,
        "pending_transactions": pending,
        "high_risk_count": high_risk,
        "avg_risk_score": round(float(avg_score), 1)
    }

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [models.UserRole.admin, models.UserRole.auditor]:
        raise HTTPException(status_code=403, detail="Access denied")

    logs = db.query(models.AuditLog).order_by(
        models.AuditLog.timestamp.desc()
    ).all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]
