from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class FlagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rule: str
    reason: str
    risk: int


class TransactionIn(BaseModel):
    account_id: str = Field(min_length=1, max_length=32)
    amount: float = Field(gt=0)
    currency: str = Field("INR", min_length=3, max_length=3)
    timestamp: Optional[datetime] = None  # defaults to now
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location: str = Field(min_length=1, max_length=80)


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    account_id: str
    amount: float
    currency: str
    timestamp: datetime
    latitude: float
    longitude: float
    location: str
    risk_score: int
    risk_level: str
    is_flagged: bool
    review_status: str
    reviewer_note: Optional[str]
    reviewed_at: Optional[datetime]
    notification_status: Optional[str]
    created_at: datetime
    flags: list[FlagOut]


class ReviewIn(BaseModel):
    status: Literal["PENDING", "REVIEWED", "CLEARED"]
    note: Optional[str] = Field(None, max_length=2000)
