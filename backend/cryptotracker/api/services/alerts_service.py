from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.api.schemas.alerts_schemas import AlertCreate
from cryptotracker.database.models import Alert


class AlertsService:
    """
    Service layer for CRUD operations on alerts.
    """

    async def create_alert(
        self,
        session: AsyncSession,
        user_id: int,
        payload: AlertCreate,
    ) -> Alert:
        """
        Persist a new alert for the given user.
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

    async def list_alerts(self, session: AsyncSession, user_id: int) -> list[Alert]:
        """
        Fetch all alerts for a user ordered by creation date.
        """
        result = await session.execute(
            select(Alert).where(Alert.user_id == user_id).order_by(Alert.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_alert(self, session: AsyncSession, user_id: int, alert_id: int) -> bool:
        """
        Delete a user's alert by ID.
        """
        result = await session.execute(
            select(Alert).where(Alert.id == alert_id, Alert.user_id == user_id)
        )
        alert = result.scalar_one_or_none()
        if not alert:
            return False

        await session.delete(alert)
        await session.commit()
        return True

