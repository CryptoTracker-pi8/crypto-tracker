from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Numeric, DateTime, func, Index, UniqueConstraint
from cryptotracker.database.base import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    investments: Mapped[list["Investment"]] = relationship(
        back_populates="portfolio",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        # один портфель на пользователя
        UniqueConstraint("user_id", name="uq_portfolios_user"),
    )


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(24, 8), nullable=False)
    buy_price: Mapped[Numeric] = mapped_column(Numeric(24, 8), nullable=False)
    bought_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    portfolio: Mapped["Portfolio"] = relationship(back_populates="investments")

    __table_args__ = (
        # полезный индекс для выборок по портфелю и тикеру
        Index("ix_investments_portfolio_symbol", "portfolio_id", "symbol"),
    )
