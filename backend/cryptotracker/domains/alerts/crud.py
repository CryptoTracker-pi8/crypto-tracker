"""
CRUD helpers for alert entities.
"""

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.domains.alerts.models import Alert
from cryptotracker.domains.alerts.schemas import AlertCreate


async def create_alert(
    session: AsyncSession,
    user_id: int,
    payload: AlertCreate,
) -> Alert:
    """
    Persist and return a new alert for the provided user.
    """

    alert = Alert(
        user_id=user_id,
        symbol=payload.symbol.upper(),
        threshold_percent=payload.threshold_percent,
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return alert


async def list_alerts(session: AsyncSession, user_id: int) -> list[Alert]:
    """
    Fetch all alerts associated with the given user.
    """

    statement: Select[tuple[Alert]] = select(Alert).where(Alert.user_id == user_id).order_by(Alert.created_at.desc())
    result = await session.execute(statement)
    alerts: Sequence[Alert] = result.scalars().all()
    return list(alerts)


async def delete_alert(session: AsyncSession, alert_id: int, user_id: int) -> bool:
    """
    Delete an alert that belongs to the given user.

    Returns True if the alert was deleted, otherwise False.
    """

    statement: Select[tuple[Alert]] = select(Alert).where(
        Alert.id == alert_id,
        Alert.user_id == user_id,
    )
    result = await session.execute(statement)
    alert = result.scalar_one_or_none()
    if alert is None:
        return False

    await session.delete(alert)
    await session.commit()
    return True

