from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.enums import OrganizationRole, TaskPriority, TaskStatus
from app.models.organization import Organization, OrganizationMember
from app.models.project import Project
from app.models.task import Task
from app.models.user import User


def get_or_create_user(db, *, email: str, full_name: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is not None:
        return user
    user = User(email=email, full_name=full_name, hashed_password=hash_password(password))
    db.add(user)
    db.flush()
    return user


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        owner = get_or_create_user(
            db,
            email="owner@example.com",
            full_name="Demo Owner",
            password="password123",
        )
        member = get_or_create_user(
            db,
            email="member@example.com",
            full_name="Demo Member",
            password="password123",
        )
        viewer = get_or_create_user(
            db,
            email="viewer@example.com",
            full_name="Demo Viewer",
            password="password123",
        )

        organization = db.scalar(select(Organization).where(Organization.slug == "demo-acme"))
        if organization is None:
            organization = Organization(name="Demo Acme", slug="demo-acme")
            db.add(organization)
            db.flush()

        memberships = [
            (owner, OrganizationRole.owner),
            (member, OrganizationRole.member),
            (viewer, OrganizationRole.viewer),
        ]
        for user, role in memberships:
            existing = db.scalar(
                select(OrganizationMember).where(
                    OrganizationMember.organization_id == organization.id,
                    OrganizationMember.user_id == user.id,
                )
            )
            if existing is None:
                db.add(
                    OrganizationMember(
                        organization_id=organization.id,
                        user_id=user.id,
                        role=role,
                    )
                )

        project = db.scalar(
            select(Project).where(
                Project.organization_id == organization.id,
                Project.name == "Customer Onboarding",
            )
        )
        if project is None:
            project = Project(
                organization_id=organization.id,
                name="Customer Onboarding",
                description="Demo workflow for onboarding new customers.",
            )
            db.add(project)
            db.flush()

        if not db.scalar(select(Task).where(Task.project_id == project.id)):
            now = datetime.now(UTC)
            db.add_all(
                [
                    Task(
                        organization_id=organization.id,
                        project_id=project.id,
                        assignee_id=member.id,
                        title="Prepare kickoff checklist",
                        status=TaskStatus.in_progress,
                        priority=TaskPriority.high,
                        due_at=now + timedelta(days=2),
                    ),
                    Task(
                        organization_id=organization.id,
                        project_id=project.id,
                        assignee_id=member.id,
                        title="Send overdue compliance reminder",
                        status=TaskStatus.blocked,
                        priority=TaskPriority.urgent,
                        due_at=now - timedelta(days=1),
                    ),
                    Task(
                        organization_id=organization.id,
                        project_id=project.id,
                        title="Archive signed contract",
                        status=TaskStatus.todo,
                        priority=TaskPriority.medium,
                    ),
                ]
            )

        db.commit()
        print("Demo data ready")
        print("Owner: owner@example.com / password123")
        print("Member: member@example.com / password123")
        print("Viewer: viewer@example.com / password123")
    finally:
        db.close()


if __name__ == "__main__":
    main()

