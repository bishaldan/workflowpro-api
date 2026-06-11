from pydantic import BaseModel


class OrganizationAnalytics(BaseModel):
    projects: int
    tasks_total: int
    tasks_open: int
    tasks_completed: int
    tasks_overdue: int
    tasks_by_priority: dict[str, int]
    member_workload: dict[str, int]

