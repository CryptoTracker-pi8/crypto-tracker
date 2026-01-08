from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cryptotracker.database.base import Base


class Alert(Base):
    """
    User alert for a symbol and percentage change threshold.
    """
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    percent: Mapped[Numeric] = mapped_column(Numeric(10, 4), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), default="both", server_default="both")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    base_price: Mapped[Numeric | None] = mapped_column(Numeric(24, 8), nullable=True)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="alerts")
    triggers: Mapped[list["AlertTriggerLog"]] = relationship(
        "AlertTriggerLog", back_populates="alert", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_alerts_user_symbol", "user_id", "symbol"),
    )


class AlertTriggerLog(Base):
    """
    Log of alert triggers for audit and user notifications.
    """
    __tablename__ = "alert_trigger_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(
        ForeignKey("alerts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    price: Mapped[Numeric] = mapped_column(Numeric(24, 8), nullable=False)
    change_percent: Mapped[Numeric] = mapped_column(Numeric(10, 4), nullable=False)

    alert: Mapped["Alert"] = relationship("Alert", back_populates="triggers")
