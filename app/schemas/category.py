from typing import List, Optional
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: str
    children: List["CategoryResponse"] = []

    model_config = {"from_attributes": True}
