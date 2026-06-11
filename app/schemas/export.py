from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ExportJobStatus


class ExportJobCreate(BaseModel):
    project_id: int


class ExportJobRead(BaseModel):
    id: int
    organization_id: int
    project_id: int
    requested_by_id: int
    status: ExportJobStatus
    filename: str | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}

