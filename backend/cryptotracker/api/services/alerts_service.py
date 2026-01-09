from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.api.schemas.alerts_schemas import AlertCreate, AlertDirection
from cryptotracker.api.services.coin_gecko_service import CoinGeckoService
from cryptotracker.database.models import Alert


class AlertsService:
    """
    Service for managing user alerts and evaluating thresholds.
    """

    def __init__(self, price_service: Optional[CoinGeckoService] = None) -> None:
        self.price_service = price_service if price_service is not None else CoinGeckoService()

    async def create_alert(self, db: AsyncSession, user_id: int, payload: AlertCreate) -> Alert:
        symbol = payload.symbol.upper()
        percent = Decimal(payload.percent)

        existing = await db.execute(
            select(Alert).where(
                Alert.user_id == user_id,
                Alert.symbol == symbol,
                Alert.percent == percent,
                Alert.direction == payload.direction,
                Alert.is_active.is_(True),
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Alert with the same parameters already exists")

        currency = await self.price_service.get_currency_by_symbol(symbol)
        if not currency or currency.price_usd is None:
            raise ValueError(f"Currency {symbol} not found")

        base_price = Decimal(str(currency.price_usd))

        alert = Alert(
            user_id=user_id,
            symbol=symbol,
            percent=percent,
            direction=payload.direction,
            base_price=base_price,
            is_active=True,
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def list_alerts(self, db: AsyncSession, user_id: int) -> list[Alert]:
        result = await db.execute(
            select(Alert).where(Alert.user_id == user_id).order_by(Alert.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_alert(self, db: AsyncSession, user_id: int, alert_id: int) -> bool:
        result = await db.execute(
            select(Alert).where(Alert.user_id == user_id, Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        if not alert:
            return False
        await db.delete(alert)
        await db.commit()
        return True

    @staticmethod
    def calculate_change_percent(base_price: Decimal, current_price: Decimal) -> Decimal:
        if base_price == 0:
            return Decimal("0")
        return (current_price - base_price) / base_price * Decimal("100")

    @staticmethod
    def should_trigger(direction: AlertDirection, change_percent: Decimal, threshold: Decimal) -> bool:
        if direction == "up":
            return change_percent >= threshold
        if direction == "down":
            return change_percent <= -threshold
        return abs(change_percent) >= threshold

    @staticmethod
    def normalize_symbol_list(alerts: Iterable[Alert]) -> set[str]:
        return {alert.symbol.upper() for alert in alerts}
