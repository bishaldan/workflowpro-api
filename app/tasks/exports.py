from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.export import ExportJob
from app.services.exports import generate_project_csv_export
from app.tasks.celery_app import celery_app


@celery_app.task
def process_project_export(export_job_id: int) -> dict[str, str | int]:
    db = SessionLocal()
    try:
        export_job = db.scalar(select(ExportJob).where(ExportJob.id == export_job_id))
        if export_job is None:
            return {"export_job_id": export_job_id, "status": "not_found"}
        generate_project_csv_export(db, export_job)
        db.commit()
        return {"export_job_id": export_job_id, "status": export_job.status.value}
    finally:
        db.close()
