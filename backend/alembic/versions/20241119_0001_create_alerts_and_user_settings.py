"""
Create alerts and user_settings tables.
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa

revision = "20241119_0001"
down_revision = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """
    Apply the alerts and user_settings schema changes.
    """

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("threshold_percent", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_alerts_user_id", "alerts", ["user_id"])

    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("theme", sa.String(length=32), nullable=False, server_default="light"),
        sa.Column("notification_mode", sa.String(length=32), nullable=False, server_default="email"),
        sa.UniqueConstraint("user_id", name="uq_user_settings_user_id"),
    )


def downgrade() -> None:
    """
    Revert the alerts and user_settings schema changes.
    """

    op.drop_table("user_settings")

    op.drop_index("ix_alerts_user_id", table_name="alerts")
    op.drop_table("alerts")

