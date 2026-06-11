import csv
from datetime import UTC, datetime
from io import StringIO

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ExportJobStatus, NotificationType
from app.models.export import ExportJob
from app.models.project import Project
from app.models.task import Task
from app.services.notifications import create_notification


def generate_project_csv_export(db: Session, export_job: ExportJob) -> ExportJob:
    export_job.status = ExportJobStatus.processing
    project = db.scalar(
        select(Project).where(
            Project.id == export_job.project_id,
            Project.organization_id == export_job.organization_id,
        )
    )
    if project is None:
        export_job.status = ExportJobStatus.failed
        export_job.error_message = "Project not found"
        export_job.completed_at = datetime.now(UTC)
        return export_job

    tasks = db.scalars(
        select(Task)
        .where(Task.project_id == project.id, Task.organization_id == export_job.organization_id)
        .order_by(Task.created_at.asc())
    )
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "title", "status", "priority", "assignee_id", "due_at", "created_at"])
    for task in tasks:
        writer.writerow(
            [
                task.id,
                task.title,
                task.status.value,
                task.priority.value,
                task.assignee_id or "",
                task.due_at.isoformat() if task.due_at else "",
                task.created_at.isoformat(),
            ]
        )

    export_job.status = ExportJobStatus.completed
    export_job.filename = f"project-{project.id}-tasks.csv"
    export_job.content = buffer.getvalue()
    export_job.completed_at = datetime.now(UTC)
    create_notification(
        db,
        organization_id=export_job.organization_id,
        user_id=export_job.requested_by_id,
        type_=NotificationType.export_completed,
        title="Project export ready",
        body=f"CSV export for {project.name} is ready to download.",
    )
    return export_job

