from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.borrow import BorrowStatus


class IssueBookRequest(BaseModel):
    book_id: str
    student_id: str
    notes: Optional[str] = None


class ReturnBookRequest(BaseModel):
    borrow_record_id: str
    notes: Optional[str] = None


class RenewBookRequest(BaseModel):
    borrow_record_id: str


class LostDamagedRequest(BaseModel):
    borrow_record_id: str
    status: BorrowStatus  # lost or damaged
    notes: Optional[str] = None


class BorrowRecordResponse(BaseModel):
    id: str
    book_id: str
    student_id: str
    librarian_id: str
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    renewal_count: int
    status: BorrowStatus
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class BorrowListResponse(BaseModel):
    items: list[BorrowRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
