from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import httpx

from cryptotracker.api.services.alerts_service import AlertsService
from cryptotracker.api.services.coin_gecko_service import CoinGeckoService
from cryptotracker.config.utils import get_settings
from cryptotracker.database.connection import get_session_factory
from cryptotracker.database.models import Alert, AlertTriggerLog

_scheduler: AsyncIOScheduler | None = None
_prices_service = CoinGeckoService()


async def _send_telegram_alert(token: str, chat_id: int, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})


async def check_alerts_job() -> None:
    """
    Check active alerts and write trigger logs on threshold hits.
    """
    async_session = get_session_factory()
    async with async_session() as db:
        result = await db.execute(
            select(Alert)
            .where(Alert.is_active.is_(True))
            .options(selectinload(Alert.user))
        )
        alerts = list(result.scalars().all())
        if not alerts:
            return

        symbols = AlertsService.normalize_symbol_list(alerts)
        prices: dict[str, Decimal] = {}
        for symbol in symbols:
            try:
                currency = await _prices_service.get_currency_by_symbol(symbol)
            except Exception:
                continue
            if not currency or currency.price_usd is None:
                continue
            prices[symbol] = Decimal(str(currency.price_usd))

        now = datetime.now(timezone.utc)
        changed = False

        settings = get_settings()
        bot_token = settings.TELEGRAM_BOT_TOKEN

        for alert in alerts:
            current_price = prices.get(alert.symbol.upper())
            if current_price is None:
                continue

            if alert.base_price is None:
                alert.base_price = current_price
                changed = True
                continue

            base_price = Decimal(str(alert.base_price))
            change_pct = AlertsService.calculate_change_percent(base_price, current_price)
            threshold = Decimal(str(alert.percent))

            if AlertsService.should_trigger(alert.direction, change_pct, threshold):
                db.add(
                    AlertTriggerLog(
                        alert_id=alert.id,
                        price=current_price,
                        change_percent=change_pct,
                    )
                )
                if bot_token and alert.user and alert.user.telegram_id:
                    direction = alert.direction
                    direction_label = "up/down" if direction == "both" else direction
                    message = (
                        f"Alert #{alert.id}: {alert.symbol} moved {change_pct:.2f}% "
                        f"({direction_label}), price {current_price}."
                    )
                    await _send_telegram_alert(bot_token, alert.user.telegram_id, message)
                alert.base_price = current_price
                alert.last_triggered_at = now
                changed = True

        if changed:
            await db.commit()


def start_alerts_scheduler() -> None:
    """
    Start APScheduler for periodic alert checks.
    """
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    settings = get_settings()
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        check_alerts_job,
        IntervalTrigger(seconds=settings.ALERT_CHECK_INTERVAL_SECONDS),
        id="alerts-check",
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()


def stop_alerts_scheduler() -> None:
    """
    Stop the scheduler on shutdown.
    """
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
