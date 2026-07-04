from typing import Optional
from datetime import date
from pydantic import BaseModel


class StudentBase(BaseModel):
    student_card_number: str
    department: Optional[str] = None
    semester: Optional[str] = None
    enrollment_date: date
    graduation_year: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class StudentCreate(StudentBase):
    email: str
    username: str
    password: str
    full_name: str


class StudentUpdate(BaseModel):
    department: Optional[str] = None
    semester: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class StudentSelfUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None


class StudentResponse(StudentBase):
    id: str
    user_id: str
    is_blocked: bool
    user: Optional[dict] = None

    model_config = {"from_attributes": True}
