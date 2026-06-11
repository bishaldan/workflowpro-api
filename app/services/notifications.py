from sqlalchemy.orm import Session

from app.models.enums import NotificationType
from app.models.notification import Notification


def create_notification(
    db: Session,
    *,
    organization_id: int,
    user_id: int,
    type_: NotificationType,
    title: str,
    body: str,
) -> Notification:
    notification = Notification(
        organization_id=organization_id,
        user_id=user_id,
        type=type_,
        title=title,
        body=body,
    )
    db.add(notification)
    return notification

