import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class ReservationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FULFILLED = "fulfilled"


class Reservation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reservations"

    book_id = Column(CHAR(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(CHAR(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    reservation_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False)
    queue_position = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    book = relationship("Book", lazy="selectin")
    student = relationship("Student", lazy="selectin")
