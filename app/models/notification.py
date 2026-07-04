import enum
from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, Text
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class NotificationType(str, enum.Enum):
    DUE_REMINDER = "due_reminder"
    RESERVATION = "reservation"
    FINE = "fine"
    GENERAL = "general"


class Notification(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), default=NotificationType.GENERAL, nullable=False)
    is_read = Column(Boolean, default=False)
