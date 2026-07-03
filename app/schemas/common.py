from pydantic import BaseModel
from typing import Generic, List, Optional, TypeVar, Any

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = {"arbitrary_types_allowed": True}
