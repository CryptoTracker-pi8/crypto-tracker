"""
SQLAlchemy models related to price alerts.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from cryptotracker.db.base import Base


class Alert(Base):
    """
    Alert thresholds configured by users for specific trading symbols.
    """

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    threshold_percent: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

