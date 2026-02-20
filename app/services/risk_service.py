from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import models

COUNTRY_RISK = {
    "USA": 10,
    "UK": 10,
    "India": 30,
    "China": 30,
    "Russia": 80,
    "Iran": 90,
    "Unknown": 50
}

def calculate_risk(transaction, documents, db: Session):
    score = 0
    reasons = []

    # 1. Transaction Amount Risk
    amount = float(transaction.amount)
    if amount > 1000000:
        score += 40
        reasons.append("Very high transaction amount (>1M)")
    elif amount > 100000:
        score += 20
        reasons.append("High transaction amount (>100k)")

    # 2. Missing Documents
    required_docs = {"PO", "INVOICE", "BILL_OF_LADING"}
    uploaded_types = {doc.doc_type.value for doc in documents}
    missing = required_docs - uploaded_types
    if missing:
        score += 30
        reasons.append(f"Missing critical documents: {', '.join(missing)}")

    # 3. Unverified Documents
    unverified_count = sum(1 for doc in documents if not doc.is_verified)
    if unverified_count > 0:
        score += 20
        reasons.append(f"Contains {unverified_count} unverified documents")

    # 4. Country Risk (Mock Simulation - assume we get country from Buyer logic or param)
    # Ideally this comes from User profile or Transaction details. 
    # For now, we simulate based on ID parity or random logic if fields missing, 
    # but let's just say we check a static 'country' if it existed, or mock it.
    # Mock: Even IDs are 'USA' (Low), Odd IDs are 'High Risk' for demo
    simulated_country = "USA" if transaction.id % 2 == 0 else "HighRiskCountry"
    
    country_risk_score = COUNTRY_RISK.get(simulated_country, 50)
    if simulated_country not in ["USA", "UK"]:
        score += 20
        reasons.append(f"High risk country detected: {simulated_country}")

    # 5. Velocity Check (Multiple POs in last 24h)
    # Count transactions by same buyer in last 24h
    if transaction.buyer_id:
        listing_time = datetime.utcnow() - timedelta(days=1)
        recent_tx_count = db.query(models.TradeTransaction).filter(
            models.TradeTransaction.buyer_id == transaction.buyer_id,
            models.TradeTransaction.created_at >= listing_time
        ).count()
        
        if recent_tx_count > 5:
            score += 25
            reasons.append(f"High velocity: {recent_tx_count} transactions in 24h")

    # Cap Score
    score = min(score, 100)

    # Classification
    if score <= 30:
        risk_level = "LOW"
    elif score <= 70:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return score, risk_level, reasons
