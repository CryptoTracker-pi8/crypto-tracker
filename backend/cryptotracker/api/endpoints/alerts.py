from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.api.schemas.alerts_schemas import (
    AlertCreate,
    AlertDeleteResponse,
    AlertListResponse,
    AlertResponse,
)
from cryptotracker.api.services.alerts_service import AlertsService
from cryptotracker.database.connection import get_db
from cryptotracker.database.models import User
from cryptotracker.utils.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])

alerts_service = AlertsService()


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    payload: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """
    Create a new alert for the current user.
    """
    try:
        alert = await alerts_service.create_alert(db=db, user_id=current_user.id, payload=payload)
        return AlertResponse.model_validate(alert)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlertListResponse:
    """
    Get all alerts for the current user.
    """
    try:
        alerts = await alerts_service.list_alerts(db=db, user_id=current_user.id)
        return AlertListResponse(alerts=[AlertResponse.model_validate(a) for a in alerts])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")


@router.delete("/{alert_id}", response_model=AlertDeleteResponse)
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlertDeleteResponse:
    """
    Delete alert by id.
    """
    try:
        deleted = await alerts_service.delete_alert(db=db, user_id=current_user.id, alert_id=alert_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Alert not found")
        return AlertDeleteResponse(message="Alert deleted successfully", alert_id=alert_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")
