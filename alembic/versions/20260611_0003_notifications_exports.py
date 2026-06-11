"""notifications and export jobs

Revision ID: 20260611_0003
Revises: 20260611_0002
Create Date: 2026-06-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260611_0003"
down_revision: str | None = "20260611_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "export_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("requested_by_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_export_jobs_id"), "export_jobs", ["id"], unique=False)
    op.create_index(
        op.f("ix_export_jobs_organization_id"),
        "export_jobs",
        ["organization_id"],
        unique=False,
    )
    op.create_index(op.f("ix_export_jobs_project_id"), "export_jobs", ["project_id"], unique=False)
    op.create_index(
        op.f("ix_export_jobs_requested_by_id"),
        "export_jobs",
        ["requested_by_id"],
        unique=False,
    )
    op.create_index(op.f("ix_export_jobs_status"), "export_jobs", ["status"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=60), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(
        op.f("ix_notifications_organization_id"),
        "notifications",
        ["organization_id"],
        unique=False,
    )
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_organization_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_export_jobs_status"), table_name="export_jobs")
    op.drop_index(op.f("ix_export_jobs_requested_by_id"), table_name="export_jobs")
    op.drop_index(op.f("ix_export_jobs_project_id"), table_name="export_jobs")
    op.drop_index(op.f("ix_export_jobs_organization_id"), table_name="export_jobs")
    op.drop_index(op.f("ix_export_jobs_id"), table_name="export_jobs")
    op.drop_table("export_jobs")

