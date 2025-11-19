from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.api.schemas.settings_schemas import UserSettingsUpdate
from cryptotracker.database.models import UserSettings


class UserSettingsService:
    """
    Service utilities for managing user settings.
    """

    async def get_or_create_settings(self, session: AsyncSession, user_id: int) -> UserSettings:
        """
        Retrieve settings for a user or create defaults if missing.
        """
        result = await session.execute(select(UserSettings).where(UserSettings.user_id == user_id))
        settings = result.scalar_one_or_none()

        if settings:
            return settings

        settings = UserSettings(user_id=user_id)
        session.add(settings)
        await session.commit()
        await session.refresh(settings)
        return settings

    async def update_settings(
        self,
        session: AsyncSession,
        user_id: int,
        payload: UserSettingsUpdate,
    ) -> UserSettings:
        """
        Update settings fields that were provided in the payload.
        """
        settings = await self.get_or_create_settings(session, user_id)
        updated = False

        if payload.theme is not None and payload.theme != settings.theme:
            settings.theme = payload.theme
            updated = True
        if (
            payload.notification_mode is not None
            and payload.notification_mode != settings.notification_mode
        ):
            settings.notification_mode = payload.notification_mode
            updated = True

        if updated:
            session.add(settings)
            await session.commit()
            await session.refresh(settings)

        return settings

