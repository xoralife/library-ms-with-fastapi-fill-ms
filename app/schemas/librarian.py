from typing import Optional
from datetime import date
from pydantic import BaseModel


class LibrarianBase(BaseModel):
    employee_id: str
    phone: Optional[str] = None
    qualification: Optional[str] = None
    hire_date: date
    shift: Optional[str] = None


class LibrarianCreate(LibrarianBase):
    email: str
    username: str
    password: str
    full_name: str


class LibrarianUpdate(BaseModel):
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    shift: Optional[str] = None
    is_active: Optional[bool] = None


class LibrarianResponse(LibrarianBase):
    id: str
    user_id: str
    is_active: bool
    user: Optional[dict] = None

    model_config = {"from_attributes": True}
