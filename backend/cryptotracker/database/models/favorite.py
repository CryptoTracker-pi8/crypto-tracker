from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cryptotracker.database.base import Base


class Favorite(Base):
    """
    Favorite cryptocurrency model for storing user's favorite currencies.
    """
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    currency_symbol: Mapped[str] = mapped_column(String(10), index=True)  # BTC, ETH, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="favorites")

    __table_args__ = (
        {"comment": "User's favorite cryptocurrencies"},
    )

