from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cryptotracker.database.base import Base


class Alert(Base):
    """
    Alert threshold for user-selected symbols.
    """

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    threshold_percent: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="alerts")

    __table_args__ = (
        {"comment": "Price alerts created by users"},
    )


class UserSettings(Base):
    """
    Per-user settings such as theme and notification mode.
    """

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    theme: Mapped[str] = mapped_column(String(20), server_default="light", nullable=False)
    notification_mode: Mapped[str] = mapped_column(String(50), server_default="email", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="settings")

    __table_args__ = (
        {"comment": "Customizable user preferences"},
    )

