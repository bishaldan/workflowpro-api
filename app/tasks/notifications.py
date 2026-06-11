from datetime import UTC, datetime

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.enums import NotificationType, OrganizationRole, TaskStatus
from app.models.organization import OrganizationMember
from app.models.task import Task
from app.services.notifications import create_notification
from app.tasks.celery_app import celery_app


@celery_app.task
def send_task_assignment_email(email: str, task_title: str) -> dict[str, str]:
    # Placeholder for a real provider such as SES, SendGrid, or Postmark.
    return {"email": email, "task_title": task_title, "status": "queued"}


@celery_app.task
def create_overdue_task_summaries() -> dict[str, int]:
    db = SessionLocal()
    notifications_created = 0
    try:
        overdue_tasks = db.scalars(
            select(Task).where(
                Task.status != TaskStatus.done,
                Task.due_at.is_not(None),
                Task.due_at < datetime.now(UTC),
            )
        ).all()
        tasks_by_user: dict[tuple[int, int], int] = {}
        for task in overdue_tasks:
            if task.assignee_id is None:
                continue
            key = (task.organization_id, task.assignee_id)
            tasks_by_user[key] = tasks_by_user.get(key, 0) + 1

        for (organization_id, user_id), count in tasks_by_user.items():
            create_notification(
                db,
                organization_id=organization_id,
                user_id=user_id,
                type_=NotificationType.overdue_summary,
                title="Overdue task summary",
                body=f"You have {count} overdue task(s).",
            )
            notifications_created += 1

        owner_memberships = db.scalars(
            select(OrganizationMember).where(OrganizationMember.role == OrganizationRole.owner)
        ).all()
        for membership in owner_memberships:
            organization_count = sum(
                1 for task in overdue_tasks if task.organization_id == membership.organization_id
            )
            if organization_count:
                create_notification(
                    db,
                    organization_id=membership.organization_id,
                    user_id=membership.user_id,
                    type_=NotificationType.overdue_summary,
                    title="Organization overdue summary",
                    body=f"Your organization has {organization_count} overdue task(s).",
                )
                notifications_created += 1

        db.commit()
        return {"notifications_created": notifications_created}
    finally:
        db.close()
