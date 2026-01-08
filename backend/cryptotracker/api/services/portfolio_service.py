from __future__ import annotations
from typing import Optional, Sequence
from datetime import datetime, timezone

from fastapi import HTTPException, status
from decimal import Decimal

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from cryptotracker.database.models import Portfolio, Investment, User
from cryptotracker.api.schemas.portfolio_schemas import PortfolioStats
from cryptotracker.api.services.coin_gecko_service import CoinGeckoService


class PortfolioService:

    def __init__(self, prices: CoinGeckoService | None = None) -> None:
        self.prices = prices if prices is not None else CoinGeckoService()


    async def get_or_create_user_by_telegram_id(
        self, db: AsyncSession, telegram_id: int, username: Optional[str] = None
    ) -> User:
        res = await db.execute(select(User).where(User.telegram_id == telegram_id))
        user = res.scalar_one_or_none()
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        elif username and user.username != username:
            user.username = username
            await db.commit()
            await db.refresh(user)
        return user


    async def _get_portfolio_by_user(
        self, db: AsyncSession, user_id: int
    ) -> Optional[Portfolio]:
        res = await db.execute(
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .options(selectinload(Portfolio.investments))
        )
        return res.scalar_one_or_none()

    async def upsert_portfolio(self, db: AsyncSession, *, user_id: int, name: str, create: bool, new_name: str | None = None) -> tuple[Portfolio, bool]:

        # create
        if create:
            p = await self._get_portfolio_by_user(db, user_id)
            if p:
                raise HTTPException(409, "Portfolio already exists")
            p = Portfolio(user_id=user_id, name=name)
            db.add(p)
            await db.commit()
            await db.refresh(p)
            return p, True

        # edit
        p = await self._get_portfolio_by_user(db, user_id)
        if not p:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if new_name is None or not new_name.strip():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="new_name is required")
        if len(new_name) > 100:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="new_name is too long")
        p.name = new_name.strip()
        await db.commit()
        await db.refresh(p)
        return p, False

    async def get_portfolio(self, db: AsyncSession, user_id: int) -> Optional[Portfolio]:
        return await self._get_portfolio_by_user(db, user_id)


    async def add_investment(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        symbol: str,
        amount: float,
        buy_price: float,
        bought_at: Optional[datetime] = None,
    ) -> Investment:
        p = await self._get_portfolio_by_user(db, user_id)
        if not p:
            p, _ = await self.upsert_portfolio(
                db,
                user_id=user_id,
                name="My Portfolio",
                create=True,
            )

        normalized_bought_at = bought_at
        if normalized_bought_at and normalized_bought_at.tzinfo is not None:
            normalized_bought_at = normalized_bought_at.astimezone(timezone.utc).replace(tzinfo=None)

        inv = Investment(
            portfolio_id=p.id,
            symbol=symbol.upper(),
            amount=amount,
            buy_price=buy_price,
            bought_at=normalized_bought_at or datetime.now(timezone.utc).replace(tzinfo=None),
        )
        db.add(inv)
        await db.commit()
        await db.refresh(inv)
        return inv

    async def delete_investment(self, db: AsyncSession, *, user_id: int, inv_id: int) -> bool:
        res = await db.execute(
            select(Investment)
            .join(Portfolio, Investment.portfolio_id == Portfolio.id)
            .where(Investment.id == inv_id, Portfolio.user_id == user_id)
        )
        inv = res.scalar_one_or_none()
        if not inv:
            return False
        await db.delete(inv)
        await db.commit()
        return True


    async def get_stats(self, db: AsyncSession, user_id: int) -> PortfolioStats:
        p = await self._get_portfolio_by_user(db, user_id)
        if not p:
            return PortfolioStats(total_invested=0, current_value=0, pnl_abs=0, pnl_pct=0)

        res = await db.execute(
            select(Investment).where(Investment.portfolio_id == p.id).order_by(Investment.id)
        )
        investments: Sequence[Investment] = res.scalars().all()

        total_invested = sum(i.amount * i.buy_price for i in investments)

        current_value = Decimal(0)
        for i in investments:
            try:
                cp = await self.prices.get_currency_by_symbol(i.symbol)
                price_usd = Decimal(str(cp.price_usd or 0))
            except Exception:
                price_usd = 0.0
            current_value += i.amount * price_usd

        pnl_abs = current_value - total_invested
        pnl_pct = (pnl_abs / total_invested * 100) if total_invested > 0 else 0.0

        return PortfolioStats(
            total_invested=round(total_invested, 2),
            current_value=round(current_value, 2),
            pnl_abs=round(pnl_abs, 2),
            pnl_pct=round(pnl_pct, 2),
        )
