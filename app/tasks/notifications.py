from app.tasks.celery_app import celery_app


@celery_app.task
def send_task_assignment_email(email: str, task_title: str) -> dict[str, str]:
    # Placeholder for a real provider such as SES, SendGrid, or Postmark.
    return {"email": email, "task_title": task_title, "status": "queued"}

