from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.database.models import UserSettings
from cryptotracker.api.schemas.settings_schemas import SettingsUpdate


class SettingsService:
    """
    Service for managing user settings.
    """

    async def get_or_create(self, db: AsyncSession, user_id: int) -> UserSettings:
        result = await db.execute(select(UserSettings).where(UserSettings.user_id == user_id))
        settings = result.scalar_one_or_none()
        if settings:
            return settings

        settings = UserSettings(user_id=user_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
        return settings

    async def update(self, db: AsyncSession, user_id: int, payload: SettingsUpdate) -> UserSettings:
        settings = await self.get_or_create(db, user_id)
        if payload.theme is not None:
            settings.theme = payload.theme
        if payload.notification_mode is not None:
            settings.notification_mode = payload.notification_mode
        await db.commit()
        await db.refresh(settings)
        return settings
