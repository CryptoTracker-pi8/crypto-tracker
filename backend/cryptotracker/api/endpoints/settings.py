from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.api.schemas.settings_schemas import SettingsResponse, SettingsUpdate
from cryptotracker.api.services.settings_service import SettingsService
from cryptotracker.database.connection import get_db
from cryptotracker.database.models import User
from cryptotracker.utils.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])

settings_service = SettingsService()


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SettingsResponse:
    """
    Get current user's settings.
    """
    try:
        settings = await settings_service.get_or_create(db=db, user_id=current_user.id)
        return SettingsResponse.model_validate(settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")


@router.put("", response_model=SettingsResponse)
async def update_settings(
    payload: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SettingsResponse:
    """
    Update current user's settings.
    """
    try:
        settings = await settings_service.update(db=db, user_id=current_user.id, payload=payload)
        return SettingsResponse.model_validate(settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
