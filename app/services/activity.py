from sqlalchemy.orm import Session

from app.models.activity import ActivityLog


def log_activity(
    db: Session,
    *,
    organization_id: int,
    actor_id: int | None,
    action: str,
    entity_type: str,
    message: str,
    entity_id: int | None = None,
) -> ActivityLog:
    activity = ActivityLog(
        organization_id=organization_id,
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        message=message,
    )
    db.add(activity)
    return activity

