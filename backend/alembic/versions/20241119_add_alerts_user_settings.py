"""add alerts and user settings tables

Revision ID: 7a5b1b7cf24b
Revises:
Create Date: 2025-11-19
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7a5b1b7cf24b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("threshold_percent", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        comment="Price alerts created by users",
    )
    op.create_index("ix_alerts_user_id", "alerts", ["user_id"])
    op.create_index("ix_alerts_symbol", "alerts", ["symbol"])

    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("theme", sa.String(length=20), server_default="light", nullable=False),
        sa.Column("notification_mode", sa.String(length=50), server_default="email", nullable=False),
        comment="Customizable user preferences",
    )
    op.create_index("ux_user_settings_user_id", "user_settings", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ux_user_settings_user_id", table_name="user_settings")
    op.drop_table("user_settings")
    op.drop_index("ix_alerts_symbol", table_name="alerts")
    op.drop_index("ix_alerts_user_id", table_name="alerts")
    op.drop_table("alerts")

