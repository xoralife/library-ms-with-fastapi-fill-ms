from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel


class ActivityLogResponse(BaseModel):
    id: str
    user_id: str
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[Any] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
