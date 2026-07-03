from typing import Optional, Any
from datetime import date, datetime
from pydantic import BaseModel


class ReportQueryParams(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class DashboardResponse(BaseModel):
    total_books: int = 0
    total_students: int = 0
    total_librarians: int = 0
    total_borrowed: int = 0
    total_available: int = 0
    total_overdue: int = 0
    total_fines_collected: float = 0.0
    recent_activities: list[Any] = []
