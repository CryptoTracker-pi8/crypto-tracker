"""
SQLAlchemy model for user interface preferences and notification modes.
"""

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from cryptotracker.db.base import Base


class UserSettings(Base):
    """
    Stores customizable preferences for a specific user.
    """

    __tablename__ = "user_settings"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_settings_user_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    theme: Mapped[str] = mapped_column(String(32), nullable=False, default="light")
    notification_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="email")

