from enum import StrEnum


class OrganizationRole(StrEnum):
    owner = "owner"
    admin = "admin"
    member = "member"
    viewer = "viewer"


class InvitationStatus(StrEnum):
    pending = "pending"
    accepted = "accepted"
    revoked = "revoked"


class ExportJobStatus(StrEnum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class NotificationType(StrEnum):
    task_assigned = "task_assigned"
    overdue_summary = "overdue_summary"
    export_completed = "export_completed"


class ProjectStatus(StrEnum):
    active = "active"
    archived = "archived"


class TaskPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TaskStatus(StrEnum):
    todo = "todo"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"
