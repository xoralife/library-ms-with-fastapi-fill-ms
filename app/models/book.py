import enum
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class BookStatus(str, enum.Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ARCHIVED = "archived"


class Book(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "books"

    title = Column(String(500), nullable=False, index=True)
    isbn = Column(String(20), unique=True, nullable=False)
    barcode = Column(String(100), unique=True, nullable=True)
    qr_code = Column(String(500), nullable=True)
    author_id = Column(String(36), ForeignKey("authors.id", ondelete="SET NULL"), nullable=True)
    publisher_id = Column(String(36), ForeignKey("publishers.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    language = Column(String(50), default="English")
    edition = Column(String(50), nullable=True)
    publish_year = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    shelf_location = Column(String(100), nullable=True)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    cover_image = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(BookStatus), default=BookStatus.AVAILABLE, nullable=False)

    author = relationship("Author", lazy="selectin")
    publisher = relationship("Publisher", lazy="selectin")
    category = relationship("Category", lazy="selectin")
