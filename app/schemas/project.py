from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ProjectStatus


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectRead(BaseModel):
    id: int
    organization_id: int
    name: str
    description: str | None
    status: ProjectStatus
    created_at: datetime

    model_config = {"from_attributes": True}

