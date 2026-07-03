from typing import Optional
from pydantic import BaseModel


class PublisherBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class PublisherCreate(PublisherBase):
    pass


class PublisherUpdate(PublisherBase):
    name: Optional[str] = None


class PublisherResponse(PublisherBase):
    id: str
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}
