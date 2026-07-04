from sqlalchemy import Boolean, Column, Date, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Student(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "students"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_card_number = Column(String(50), unique=True, nullable=False)
    department = Column(String(100), nullable=True)
    semester = Column(String(20), nullable=True)
    enrollment_date = Column(Date, nullable=False)
    graduation_year = Column(String(4), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    is_blocked = Column(Boolean, default=False)

    user = relationship("User", lazy="selectin")
