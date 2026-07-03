from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.fine import FineReason


class FineResponse(BaseModel):
    id: str
    borrow_record_id: str
    student_id: str
    amount: float
    reason: FineReason
    is_paid: bool
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PayFineRequest(BaseModel):
    payment_method: str  # cash, card, online
    transaction_id: Optional[str] = None


class PaymentResponse(BaseModel):
    id: str
    fine_id: str
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    payment_date: datetime

    model_config = {"from_attributes": True}


class FineListResponse(BaseModel):
    items: list[FineResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
