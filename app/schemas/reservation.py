from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.reservation import ReservationStatus


class ReserveRequest(BaseModel):
    book_id: str
    notes: Optional[str] = None


class ReservationResponse(BaseModel):
    id: str
    book_id: str
    student_id: str
    reservation_date: datetime
    expiry_date: datetime
    status: ReservationStatus
    queue_position: Optional[int] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class ReservationListResponse(BaseModel):
    items: list[ReservationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
