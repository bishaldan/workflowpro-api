from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_org_admin, require_org_member
from app.db.session import get_db
from app.models.enums import InvitationStatus, OrganizationRole
from app.models.organization import Organization, OrganizationInvitation, OrganizationMember
from app.models.user import User
from app.schemas.organization import (
    InvitationCreate,
    InvitationRead,
    OrganizationCreate,
    OrganizationMemberRead,
    OrganizationRead,
)
from app.services.activity import log_activity

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
    log_activity(
        db,
        organization_id=organization.id,
        actor_id=current_user.id,
        action="organization.created",
        entity_type="organization",
        entity_id=organization.id,
        message=f"Created organization {organization.name}",
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


@router.get("/{organization_id}/members", response_model=list[OrganizationMemberRead])
def list_members(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[OrganizationMember]:
    require_org_member(organization_id, current_user, db)
    return list(
        db.scalars(
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
            .order_by(OrganizationMember.created_at.asc())
        )
    )


@router.post(
    "/{organization_id}/invitations",
    response_model=InvitationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    organization_id: int,
    payload: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrganizationInvitation:
    require_org_admin(organization_id, current_user, db)
    if payload.role == OrganizationRole.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner role cannot be invited")

    invited_user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if invited_user is not None:
        existing_member = db.scalar(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == invited_user.id,
            )
        )
        if existing_member is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")

    existing_invitation = db.scalar(
        select(OrganizationInvitation).where(
            OrganizationInvitation.organization_id == organization_id,
            OrganizationInvitation.email == payload.email.lower(),
            OrganizationInvitation.status == InvitationStatus.pending,
        )
    )
    if existing_invitation is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invitation already pending")

    invitation = OrganizationInvitation(
        organization_id=organization_id,
        email=payload.email.lower(),
        role=payload.role,
        invited_by_id=current_user.id,
    )
    db.add(invitation)
    db.flush()
    log_activity(
        db,
        organization_id=organization_id,
        actor_id=current_user.id,
        action="invitation.created",
        entity_type="organization_invitation",
        entity_id=invitation.id,
        message=f"Invited {invitation.email} as {invitation.role.value}",
    )
    db.commit()
    db.refresh(invitation)
    return invitation


@router.post("/{organization_id}/invitations/{invitation_id}/accept", response_model=OrganizationMemberRead)
def accept_invitation(
    organization_id: int,
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrganizationMember:
    invitation = db.scalar(
        select(OrganizationInvitation).where(
            OrganizationInvitation.id == invitation_id,
            OrganizationInvitation.organization_id == organization_id,
            OrganizationInvitation.status == InvitationStatus.pending,
        )
    )
    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    if invitation.email != current_user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invitation email mismatch")

    existing_member = db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == current_user.id,
        )
    )
    if existing_member is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")

    invitation.status = InvitationStatus.accepted
    invitation.accepted_by_id = current_user.id
    invitation.accepted_at = datetime.now(UTC)
    membership = OrganizationMember(
        organization_id=organization_id,
        user_id=current_user.id,
        role=invitation.role,
    )
    db.add(membership)
    db.flush()
    log_activity(
        db,
        organization_id=organization_id,
        actor_id=current_user.id,
        action="invitation.accepted",
        entity_type="organization_member",
        entity_id=membership.id,
        message=f"{current_user.email} joined the organization as {membership.role.value}",
    )
    db.commit()
    db.refresh(membership)
    return membership
