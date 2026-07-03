from typing import Optional
from pydantic import BaseModel


class SettingUpdate(BaseModel):
    value: str


class SettingResponse(BaseModel):
    id: str
    key: str
    value: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class SettingsListResponse(BaseModel):
    items: list[SettingResponse]
