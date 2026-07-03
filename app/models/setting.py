from sqlalchemy import Column, String, Text
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Setting(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "settings"

    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
