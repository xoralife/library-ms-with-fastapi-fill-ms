import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text, Numeric
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class FineReason(str, enum.Enum):
    OVERDUE = "overdue"
    LOST = "lost"
    DAMAGED = "damaged"


class Fine(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "fines"

    borrow_record_id = Column(String(36), ForeignKey("borrow_records.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(Enum(FineReason), nullable=False)
    is_paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)

    borrow_record = relationship("BorrowRecord", lazy="selectin")
    student = relationship("Student", lazy="selectin")


class Payment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "payments"

    fine_id = Column(String(36), ForeignKey("fines.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(Enum("cash", "card", "online", name="payment_method"), nullable=False)
    transaction_id = Column(String(255), nullable=True)
    payment_date = Column(DateTime, nullable=False)
    received_by = Column(String(36), ForeignKey("librarians.id", ondelete="SET NULL"), nullable=True)

    fine = relationship("Fine", lazy="selectin")
