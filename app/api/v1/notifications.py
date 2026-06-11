from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_org_member
from app.db.session import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationRead

router = APIRouter()


@router.get("/{organization_id}/notifications", response_model=list[NotificationRead])
def list_notifications(
    organization_id: int,
    unread_only: bool = False,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Notification]:
    require_org_member(organization_id, current_user, db)
    query = select(Notification).where(
        Notification.organization_id == organization_id,
        Notification.user_id == current_user.id,
    )
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    return list(db.scalars(query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)))

