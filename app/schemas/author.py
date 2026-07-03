from datetime import date
from typing import Optional
from pydantic import BaseModel


class AuthorBase(BaseModel):
    name: str
    biography: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None
    website: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    name: Optional[str] = None


class AuthorResponse(AuthorBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}
