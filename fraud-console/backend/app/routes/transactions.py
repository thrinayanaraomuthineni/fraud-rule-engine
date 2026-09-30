from datetime import timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import FraudFlag, Transaction, utcnow
from ..rules import engine, risk_level
from ..schemas import TransactionIn, TransactionOut
from ..services.notification import notify_high_risk

router = APIRouter(prefix="/api/transactions", tags=["transactions"])
Status = Optional[Literal["PENDING", "REVIEWED", "CLEARED"]]


def get_or_404(db: Session, tx_id: int) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(404, f"Transaction {tx_id} not found")
    return tx


def score(db: Session, tx: Transaction, notifier=None) -> Transaction:
    """Run the rule engine, persist flags/score, and alert if the HIGH threshold is crossed."""
    history = db.scalars(
        select(Transaction)
        .where(
            Transaction.account_id == tx.account_id,
            Transaction.id != tx.id,
            Transaction.timestamp <= tx.timestamp,
        )
        .order_by(Transaction.timestamp)
    ).all()
    results = [r for r in engine.evaluate(tx, history) if r.triggered]
    tx.flags = [FraudFlag(rule=r.rule, reason=r.reason, risk=r.risk) for r in results]
    tx.risk_score = min(100, sum(r.risk for r in results))
    tx.risk_level = risk_level(tx.risk_score)
    tx.is_flagged = bool(results)
    if tx.risk_score >= settings.HIGH_THRESHOLD and tx.notification_status in (None, "FAILED"):
        tx.notification_status = notify_high_risk(tx, notifier)
    db.commit()
    db.refresh(tx)
    return tx


def _search(db, q, status, flagged, limit):
    stmt = select(Transaction).order_by(Transaction.timestamp.desc()).limit(limit)
    if flagged:
        stmt = stmt.where(Transaction.is_flagged)
    if status:
        stmt = stmt.where(Transaction.review_status == status)
    if q and q.strip():
        term = q.strip()
        cond = or_(Transaction.account_id.ilike(f"%{term}%"), Transaction.location.ilike(f"%{term}%"))
        digits = term.upper().removeprefix("TX-")
        if digits.isdigit():
            cond = or_(cond, Transaction.id == int(digits))
        stmt = stmt.where(cond)
    return db.scalars(stmt).all()


@router.get("", response_model=list[TransactionOut])
def list_transactions(q: Optional[str] = None, status: Status = None,
                      limit: int = Query(300, ge=1, le=1000), db: Session = Depends(get_db)):
    return _search(db, q, status, False, limit)


@router.get("/flagged", response_model=list[TransactionOut])
def list_flagged(q: Optional[str] = None, status: Status = None,
                 limit: int = Query(300, ge=1, le=1000), db: Session = Depends(get_db)):
    return _search(db, q, status, True, limit)


@router.get("/{tx_id}", response_model=TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, tx_id)


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(body: TransactionIn, db: Session = Depends(get_db)):
    data = body.model_dump()
    ts = data.pop("timestamp") or utcnow()
    if ts.tzinfo:
        ts = ts.astimezone(timezone.utc).replace(tzinfo=None)
    data["currency"] = data["currency"].upper()
    tx = Transaction(**data, timestamp=ts)
    db.add(tx)
    db.flush()
    return score(db, tx)


@router.post("/{tx_id}/evaluate", response_model=TransactionOut)
def evaluate_transaction(tx_id: int, db: Session = Depends(get_db)):
    return score(db, get_or_404(db, tx_id))
