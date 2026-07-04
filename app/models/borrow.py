import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class BorrowStatus(str, enum.Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"
    DAMAGED = "damaged"


class BorrowRecord(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "borrow_records"

    book_id = Column(String(36), ForeignKey("books.id", ondelete="RESTRICT"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="RESTRICT"), nullable=False, index=True)
    librarian_id = Column(String(36), ForeignKey("librarians.id", ondelete="RESTRICT"), nullable=False)
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    renewal_count = Column(Integer, default=0)
    max_renewals = Column(Integer, default=2)
    status = Column(Enum(BorrowStatus), default=BorrowStatus.BORROWED, nullable=False)
    notes = Column(Text, nullable=True)

    book = relationship("Book", lazy="selectin")
    student = relationship("Student", lazy="selectin")
    librarian = relationship("Librarian", lazy="selectin")
