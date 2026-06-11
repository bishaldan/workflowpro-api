from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_org_member
from app.db.session import get_db
from app.models.activity import ActivityLog
from app.models.user import User
from app.schemas.activity import ActivityLogRead

router = APIRouter()


@router.get("/{organization_id}/activity", response_model=list[ActivityLogRead])
def list_activity(
    organization_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ActivityLog]:
    require_org_member(organization_id, current_user, db)
    return list(
        db.scalars(
            select(ActivityLog)
            .where(ActivityLog.organization_id == organization_id)
            .order_by(ActivityLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    )

