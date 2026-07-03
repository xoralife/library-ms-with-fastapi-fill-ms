from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Category(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "categories"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(CHAR(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    children = relationship("Category", backref="parent", remote_side="Category.id", lazy="selectin")
