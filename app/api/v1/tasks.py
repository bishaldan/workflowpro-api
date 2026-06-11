from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_org_member, require_org_writer
from app.db.session import get_db
from app.models.enums import NotificationType, TaskPriority, TaskStatus
from app.models.organization import OrganizationMember
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.activity import log_activity
from app.services.notifications import create_notification

router = APIRouter()


@router.post("/{organization_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    organization_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    require_org_writer(organization_id, current_user, db)
    project = db.scalar(
        select(Project).where(
            Project.id == payload.project_id,
            Project.organization_id == organization_id,
        )
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if payload.assignee_id is not None:
        assignee_member = db.scalar(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == payload.assignee_id,
            )
        )
        if assignee_member is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee is not a member")

    task = Task(organization_id=organization_id, **payload.model_dump())
    db.add(task)
    db.flush()
    log_activity(
        db,
        organization_id=organization_id,
        actor_id=current_user.id,
        action="task.created",
        entity_type="task",
        entity_id=task.id,
        message=f"Created task {task.title}",
    )
    if task.assignee_id is not None:
        create_notification(
            db,
            organization_id=organization_id,
            user_id=task.assignee_id,
            type_=NotificationType.task_assigned,
            title="New task assigned",
            body=f"You were assigned to {task.title}.",
        )
    db.commit()
    db.refresh(task)
    return task


@router.get("/{organization_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    organization_id: int,
    project_id: int | None = None,
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
    search: str | None = Query(default=None, min_length=2, max_length=80),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Task]:
    require_org_member(organization_id, current_user, db)
    query = select(Task).where(Task.organization_id == organization_id)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    if status_filter is not None:
        query = query.where(Task.status == status_filter)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if assignee_id is not None:
        query = query.where(Task.assignee_id == assignee_id)
    if search is not None:
        query = query.where(Task.title.ilike(f"%{search}%"))
    return list(db.scalars(query.order_by(Task.created_at.desc()).offset(offset).limit(limit)))


@router.patch("/{organization_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    organization_id: int,
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    require_org_writer(organization_id, current_user, db)
    task = db.scalar(select(Task).where(Task.id == task_id, Task.organization_id == organization_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if payload.assignee_id is not None:
        assignee_member = db.scalar(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == payload.assignee_id,
            )
        )
        if assignee_member is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee is not a member")

    original_assignee_id = task.assignee_id
    original_status = task.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    if task.status != original_status:
        log_activity(
            db,
            organization_id=organization_id,
            actor_id=current_user.id,
            action="task.status_changed",
            entity_type="task",
            entity_id=task.id,
            message=f"Changed task {task.title} status to {task.status.value}",
        )
    if task.assignee_id is not None and task.assignee_id != original_assignee_id:
        create_notification(
            db,
            organization_id=organization_id,
            user_id=task.assignee_id,
            type_=NotificationType.task_assigned,
            title="Task reassigned to you",
            body=f"You were assigned to {task.title}.",
        )
    db.commit()
    db.refresh(task)
    return task
