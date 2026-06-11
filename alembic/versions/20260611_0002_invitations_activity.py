"""invitations and activity logs

Revision ID: 20260611_0002
Revises: 20260611_0001
Create Date: 2026-06-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260611_0002"
down_revision: str | None = "20260611_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activity_logs_actor_id"), "activity_logs", ["actor_id"], unique=False)
    op.create_index(
        op.f("ix_activity_logs_organization_id"),
        "activity_logs",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "organization_invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("invited_by_id", sa.Integer(), nullable=False),
        sa.Column("accepted_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["accepted_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["invited_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "email", "status", name="uq_pending_org_invitation"),
    )
    op.create_index(
        op.f("ix_organization_invitations_email"),
        "organization_invitations",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_invitations_invited_by_id"),
        "organization_invitations",
        ["invited_by_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_invitations_organization_id"),
        "organization_invitations",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_organization_invitations_organization_id"),
        table_name="organization_invitations",
    )
    op.drop_index(
        op.f("ix_organization_invitations_invited_by_id"),
        table_name="organization_invitations",
    )
    op.drop_index(op.f("ix_organization_invitations_email"), table_name="organization_invitations")
    op.drop_table("organization_invitations")
    op.drop_index(op.f("ix_activity_logs_organization_id"), table_name="activity_logs")
    op.drop_index(op.f("ix_activity_logs_actor_id"), table_name="activity_logs")
    op.drop_table("activity_logs")
