from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_org_member, require_org_writer
from app.db.session import get_db
from app.models.enums import ExportJobStatus
from app.models.export import ExportJob
from app.models.project import Project
from app.models.user import User
from app.schemas.export import ExportJobCreate, ExportJobRead
from app.services.activity import log_activity
from app.services.exports import generate_project_csv_export

router = APIRouter()


@router.post("/{organization_id}/exports", response_model=ExportJobRead, status_code=status.HTTP_201_CREATED)
def create_export_job(
    organization_id: int,
    payload: ExportJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExportJob:
    require_org_writer(organization_id, current_user, db)
    project = db.scalar(
        select(Project).where(
            Project.id == payload.project_id,
            Project.organization_id == organization_id,
        )
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    export_job = ExportJob(
        organization_id=organization_id,
        project_id=project.id,
        requested_by_id=current_user.id,
    )
    db.add(export_job)
    db.flush()
    log_activity(
        db,
        organization_id=organization_id,
        actor_id=current_user.id,
        action="export.requested",
        entity_type="export_job",
        entity_id=export_job.id,
        message=f"Requested CSV export for project {project.name}",
    )
    generate_project_csv_export(db, export_job)
    db.commit()
    db.refresh(export_job)
    return export_job


@router.get("/{organization_id}/exports/{export_id}", response_model=ExportJobRead)
def read_export_job(
    organization_id: int,
    export_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExportJob:
    require_org_member(organization_id, current_user, db)
    export_job = db.scalar(
        select(ExportJob).where(
            ExportJob.id == export_id,
            ExportJob.organization_id == organization_id,
        )
    )
    if export_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    return export_job


@router.get("/{organization_id}/exports/{export_id}/download")
def download_export_job(
    organization_id: int,
    export_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    require_org_member(organization_id, current_user, db)
    export_job = db.scalar(
        select(ExportJob).where(
            ExportJob.id == export_id,
            ExportJob.organization_id == organization_id,
        )
    )
    if export_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    if export_job.status != ExportJobStatus.completed or export_job.content is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Export is not ready")

    return Response(
        content=export_job.content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{export_job.filename}"'},
    )

