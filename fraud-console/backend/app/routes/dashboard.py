from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import FraudFlag, Transaction
from ..services.notification import aws_configured

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    count = lambda *cond: db.scalar(select(func.count()).select_from(Transaction).where(*cond)) or 0
    return {
        "total": count(),
        "flagged": count(Transaction.is_flagged),
        "high_risk": count(Transaction.risk_level.in_(["HIGH", "CRITICAL"])),
        "pending_reviews": count(Transaction.is_flagged, Transaction.review_status == "PENDING"),
        "by_rule": dict(db.execute(select(FraudFlag.rule, func.count()).group_by(FraudFlag.rule)).all()),
        "notifier": "AWS" if aws_configured() else "MOCK",
        "high_threshold": settings.HIGH_THRESHOLD,
    }
