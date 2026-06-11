from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import InvitationStatus, OrganizationRole


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(min_length=2, max_length=180, pattern=r"^[a-z0-9-]+$")


class OrganizationRead(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationMemberRead(BaseModel):
    user_id: int
    role: OrganizationRole

    model_config = {"from_attributes": True}


class InvitationCreate(BaseModel):
    email: EmailStr
    role: OrganizationRole = OrganizationRole.member


class InvitationRead(BaseModel):
    id: int
    organization_id: int
    email: EmailStr
    role: OrganizationRole
    status: InvitationStatus

    model_config = {"from_attributes": True}
