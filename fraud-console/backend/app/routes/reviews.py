from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import utcnow
from ..schemas import ReviewIn, TransactionOut
from .transactions import get_or_404

router = APIRouter(prefix="/api/transactions", tags=["reviews"])


@router.patch("/{tx_id}/review", response_model=TransactionOut)
def review_transaction(tx_id: int, body: ReviewIn, db: Session = Depends(get_db)):
    tx = get_or_404(db, tx_id)
    tx.review_status = body.status
    if body.note is not None:
        tx.reviewer_note = body.note.strip() or None
    tx.reviewed_at = None if body.status == "PENDING" else utcnow()
    db.commit()
    db.refresh(tx)
    return tx
