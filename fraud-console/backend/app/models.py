from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    """Naive UTC datetime (all timestamps are stored as UTC)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[str] = mapped_column(String(32), index=True)
    amount: Mapped[float]
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    timestamp: Mapped[datetime] = mapped_column(index=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    location: Mapped[str] = mapped_column(String(80))
    risk_score: Mapped[int] = mapped_column(default=0)
    risk_level: Mapped[str] = mapped_column(String(10), default="LOW")
    is_flagged: Mapped[bool] = mapped_column(default=False, index=True)
    review_status: Mapped[str] = mapped_column(String(10), default="PENDING", index=True)
    reviewer_note: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_at: Mapped[Optional[datetime]]
    notification_status: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    flags: Mapped[list["FraudFlag"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by="FraudFlag.id"
    )


class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), index=True)
    rule: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(Text)
    risk: Mapped[int]
