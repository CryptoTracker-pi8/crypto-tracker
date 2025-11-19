from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.api.schemas.settings_schemas import UserSettingsRead, UserSettingsUpdate
from cryptotracker.api.services.settings_service import UserSettingsService
from cryptotracker.database.connection import get_session
from cryptotracker.utils.common import get_current_user_id

router = APIRouter(prefix="/settings", tags=["settings"])
settings_service = UserSettingsService()


@router.get("", response_model=UserSettingsRead)
async def get_settings(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> UserSettingsRead:
    """
    Retrieve settings for the authenticated user (create defaults if none exist).
    """
    try:
        settings = await settings_service.get_or_create_settings(session=session, user_id=user_id)
        return UserSettingsRead.model_validate(settings)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to load settings: {exc}")


@router.put("", response_model=UserSettingsRead)
async def update_settings(
    payload: UserSettingsUpdate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> UserSettingsRead:
    """
    Update the authenticated user's settings.
    """
    try:
        settings = await settings_service.update_settings(session=session, user_id=user_id, payload=payload)
        return UserSettingsRead.model_validate(settings)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {exc}")

