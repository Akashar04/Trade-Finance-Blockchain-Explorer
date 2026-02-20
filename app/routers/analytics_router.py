from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..deps import get_current_user
from .. import models

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

@router.get("/overview")
def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.bank:
        raise HTTPException(status_code=403, detail="Access denied")

    total = db.query(models.TradeTransaction).count()
    completed = db.query(models.TradeTransaction).filter(
        models.TradeTransaction.status == models.TransactionStatus.PO_COMPLETED
    ).count()
    pending = total - completed

    # High risk count (from latest scores)
    # This is a bit complex if we want exactly "current high risk transactions".
    # For simplicity, count High Risk scores in RiskScore table.
    high_risk_count = db.query(models.RiskScore).filter(
        models.RiskScore.risk_level == "HIGH"
    ).count()

    avg_risk = db.query(func.avg(models.RiskScore.score)).scalar() or 0

    return {
        "total_transactions": total,
        "completed_transactions": completed,
        "pending_transactions": pending,
        "high_risk_count": high_risk_count,
        "avg_risk_score": round(float(avg_risk), 1)
    }

@router.get("/risk-distribution")
def get_risk_distribution(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.bank:
        raise HTTPException(status_code=403, detail="Access denied")

    low = db.query(models.RiskScore).filter(models.RiskScore.risk_level == "LOW").count()
    medium = db.query(models.RiskScore).filter(models.RiskScore.risk_level == "MEDIUM").count()
    high = db.query(models.RiskScore).filter(models.RiskScore.risk_level == "HIGH").count()

    return {
        "low": low,
        "medium": medium,
        "high": high
    }

@router.get("/top-risk-transactions")
def get_top_risk_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [models.UserRole.bank, models.UserRole.admin, models.UserRole.auditor]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get top 5 risks. Join with User to get name? Or just return user_id.
    # Instruction says "Return top 5 highest risk transactions". 
    # RiskScore has user_id, not transaction_id directly in the model I see.
    # But wait, in transaction_router we are saving user_id=buyer_id.
    # So we can link back to user. 
    # Ideally we'd link to transaction, but let's return the RiskScore objects.
    
    top_risks = db.query(models.RiskScore).order_by(
        models.RiskScore.score.desc()
    ).limit(5).all()

    return [
        {
            "user_id": r.user_id,
            "score": r.score,
            "risk_level": r.risk_level,
            "last_updated": r.last_updated
        }
        for r in top_risks
    ]
