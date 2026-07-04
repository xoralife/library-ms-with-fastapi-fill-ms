from sqlalchemy import Boolean, Column, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Librarian(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "librarians"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    qualification = Column(String(255), nullable=True)
    hire_date = Column(Date, nullable=False)
    shift = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", lazy="selectin")
