"""
FastAPI router for managing per-user settings.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.db.session import get_db_session
from cryptotracker.domains.dependencies import get_current_user_id
from cryptotracker.domains.settings import crud
from cryptotracker.domains.settings.schemas import (
    UserSettingsRead,
    UserSettingsUpdate,
)

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=UserSettingsRead)
async def get_user_settings(
    session: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
) -> UserSettingsRead:
    """
    Return persisted settings for the current user, creating them when needed.
    """

    settings = await crud.get_or_create_user_settings(session=session, user_id=user_id)
    return UserSettingsRead.model_validate(settings)


@router.put("", response_model=UserSettingsRead)
async def update_user_settings(
    payload: UserSettingsUpdate,
    session: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
) -> UserSettingsRead:
    """
    Update the current user's settings.
    """

    settings = await crud.update_user_settings(session=session, user_id=user_id, payload=payload)
    return UserSettingsRead.model_validate(settings)

