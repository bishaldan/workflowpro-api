from datetime import datetime

from pydantic import BaseModel

from app.models.enums import NotificationType


class NotificationRead(BaseModel):
    id: int
    organization_id: int
    user_id: int
    type: NotificationType
    title: str
    body: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}

