from typing import Optional
from pydantic import BaseModel, field_validator
from app.schemas.author import AuthorResponse
from app.schemas.publisher import PublisherResponse
from app.schemas.category import CategoryResponse
from app.models.book import BookStatus


class BookBase(BaseModel):
    title: str
    isbn: str
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    author_id: Optional[str] = None
    publisher_id: Optional[str] = None
    category_id: Optional[str] = None
    language: str = "English"
    edition: Optional[str] = None
    publish_year: Optional[int] = None
    page_count: Optional[int] = None
    shelf_location: Optional[str] = None
    total_copies: int = 1
    cover_image: Optional[str] = None
    description: Optional[str] = None

    @field_validator("total_copies")
    @classmethod
    def validate_copies(cls, v: int) -> int:
        if v < 1:
            raise ValueError("total_copies must be at least 1")
        return v


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    title: Optional[str] = None
    isbn: Optional[str] = None


class BookResponse(BookBase):
    id: str
    available_copies: int
    status: BookStatus
    author: Optional[AuthorResponse] = None
    publisher: Optional[PublisherResponse] = None
    category: Optional[CategoryResponse] = None

    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    items: list[BookResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
