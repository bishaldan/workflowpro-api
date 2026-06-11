from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import OrganizationRole
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationRead

router = APIRouter()


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Organization:
    existing_org = db.scalar(select(Organization).where(Organization.slug == payload.slug))
    if existing_org:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization slug already exists")

    organization = Organization(name=payload.name, slug=payload.slug)
    db.add(organization)
    db.flush()
    db.add(
        OrganizationMember(
            organization_id=organization.id,
            user_id=current_user.id,
            role=OrganizationRole.owner,
        )
    )
    db.commit()
    db.refresh(organization)
    return organization


@router.get("", response_model=list[OrganizationRead])
def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Organization]:
    return list(
        db.scalars(
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == current_user.id)
            .order_by(Organization.created_at.desc())
        )
    )

