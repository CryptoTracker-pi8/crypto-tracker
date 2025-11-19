"""
CRUD helpers for user settings.
"""

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.domains.settings.models import UserSettings
from cryptotracker.domains.settings.schemas import UserSettingsUpdate

DEFAULT_THEME = "light"
DEFAULT_NOTIFICATION_MODE = "email"


async def get_or_create_user_settings(session: AsyncSession, user_id: int) -> UserSettings:
    """
    Retrieve settings for the user or create them with default values.
    """

    statement: Select[tuple[UserSettings]] = select(UserSettings).where(UserSettings.user_id == user_id)
    result = await session.execute(statement)
    settings = result.scalar_one_or_none()
    if settings is not None:
        return settings

    settings = UserSettings(
        user_id=user_id,
        theme=DEFAULT_THEME,
        notification_mode=DEFAULT_NOTIFICATION_MODE,
    )
    session.add(settings)
    await session.commit()
    await session.refresh(settings)
    return settings


async def update_user_settings(
    session: AsyncSession,
    user_id: int,
    payload: UserSettingsUpdate,
) -> UserSettings:
    """
    Update (or create) user settings with the provided payload.
    """

    settings = await get_or_create_user_settings(session=session, user_id=user_id)
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in updates.items():
        setattr(settings, field, value)

    session.add(settings)
    await session.commit()
    await session.refresh(settings)
    return settings

