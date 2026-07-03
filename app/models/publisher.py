from sqlalchemy import Column, String, Text
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Publisher(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "publishers"

    name = Column(String(255), nullable=False, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
