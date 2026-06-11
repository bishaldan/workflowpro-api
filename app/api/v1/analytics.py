from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_org_member
from app.db.session import get_db
from app.models.enums import TaskPriority, TaskStatus
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.analytics import OrganizationAnalytics

router = APIRouter()


@router.get("/{organization_id}/analytics", response_model=OrganizationAnalytics)
def read_analytics(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrganizationAnalytics:
    require_org_member(organization_id, current_user, db)
    now = datetime.now(UTC)

    projects = db.scalar(
        select(func.count()).select_from(Project).where(Project.organization_id == organization_id)
    )
    tasks_total = db.scalar(
        select(func.count()).select_from(Task).where(Task.organization_id == organization_id)
    )
    tasks_completed = db.scalar(
        select(func.count())
        .select_from(Task)
        .where(Task.organization_id == organization_id, Task.status == TaskStatus.done)
    )
    tasks_overdue = db.scalar(
        select(func.count())
        .select_from(Task)
        .where(
            Task.organization_id == organization_id,
            Task.status != TaskStatus.done,
            Task.due_at < now,
        )
    )

    priority_rows = db.execute(
        select(Task.priority, func.count())
        .where(Task.organization_id == organization_id)
        .group_by(Task.priority)
    ).all()
    workload_rows = db.execute(
        select(User.email, func.count())
        .join(Task, Task.assignee_id == User.id)
        .where(Task.organization_id == organization_id)
        .group_by(User.email)
    ).all()

    tasks_by_priority = {priority.value: 0 for priority in TaskPriority}
    tasks_by_priority.update({priority.value: count for priority, count in priority_rows})

    return OrganizationAnalytics(
        projects=projects or 0,
        tasks_total=tasks_total or 0,
        tasks_open=(tasks_total or 0) - (tasks_completed or 0),
        tasks_completed=tasks_completed or 0,
        tasks_overdue=tasks_overdue or 0,
        tasks_by_priority=tasks_by_priority,
        member_workload={email: count for email, count in workload_rows},
    )

