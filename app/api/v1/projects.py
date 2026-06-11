from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_org_member, require_org_writer
from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.activity import log_activity

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
    db.flush()
    log_activity(
        db,
        organization_id=organization_id,
        actor_id=current_user.id,
        action="project.created",
        entity_type="project",
        entity_id=project.id,
        message=f"Created project {project.name}",
    )
    db.commit()
    db.refresh(project)
    return project


@router.get("/{organization_id}/projects", response_model=list[ProjectRead])
def list_projects(
    organization_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Project]:
    require_org_member(organization_id, current_user, db)
    return list(
        db.scalars(
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.created_at.desc())
            .offset(offset)
            .limit(limit)
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

    original_status = project.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    if project.status != original_status:
        log_activity(
            db,
            organization_id=organization_id,
            actor_id=current_user.id,
            action="project.status_changed",
            entity_type="project",
            entity_id=project.id,
            message=f"Changed project {project.name} status to {project.status.value}",
        )
    db.commit()
    db.refresh(project)
    return project
