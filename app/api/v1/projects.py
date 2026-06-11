from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_org_member, require_org_writer
from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter()


@router.post("/{organization_id}/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    organization_id: int,
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    require_org_writer(organization_id, current_user, db)
    project = Project(
        organization_id=organization_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{organization_id}/projects", response_model=list[ProjectRead])
def list_projects(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Project]:
    require_org_member(organization_id, current_user, db)
    return list(
        db.scalars(
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.created_at.desc())
        )
    )


@router.patch("/{organization_id}/projects/{project_id}", response_model=ProjectRead)
def update_project(
    organization_id: int,
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    require_org_writer(organization_id, current_user, db)
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.organization_id == organization_id)
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project

