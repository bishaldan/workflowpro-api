from datetime import datetime

from pydantic import BaseModel


class ActivityLogRead(BaseModel):
    id: int
    organization_id: int
    actor_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}

