from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_org_member, require_org_writer
from app.db.session import get_db
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

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

    task = Task(organization_id=organization_id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{organization_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    organization_id: int,
    project_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Task]:
    require_org_member(organization_id, current_user, db)
    query = select(Task).where(Task.organization_id == organization_id)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    return list(db.scalars(query.order_by(Task.created_at.desc())))


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

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

