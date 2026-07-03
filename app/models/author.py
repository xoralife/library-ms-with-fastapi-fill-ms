from sqlalchemy import Column, Date, String, Text
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Author(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "authors"

    name = Column(String(255), nullable=False, index=True)
    biography = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)
    nationality = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
