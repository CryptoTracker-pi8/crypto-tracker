from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.api.schemas.alerts_schemas import AlertCreate, AlertRead
from cryptotracker.api.services.alerts_service import AlertsService
from cryptotracker.database.connection import get_session
from cryptotracker.utils.common import get_current_user_id

router = APIRouter(prefix="/alerts", tags=["alerts"])
alerts_service = AlertsService()


@router.post("", response_model=AlertRead, status_code=201)
async def create_alert(
    payload: AlertCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> AlertRead:
    """
    Create a new alert for the authenticated user.
    """
    try:
        alert = await alerts_service.create_alert(session=session, user_id=user_id, payload=payload)
        return AlertRead.model_validate(alert)
    except Exception as exc:  # pragma: no cover - unexpected failures are surfaced
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {exc}")


@router.get("", response_model=list[AlertRead])
async def list_alerts(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> list[AlertRead]:
    """
    List all alerts for the authenticated user.
    """
    try:
        alerts = await alerts_service.list_alerts(session=session, user_id=user_id)
        return [AlertRead.model_validate(alert) for alert in alerts]
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {exc}")


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """
    Delete a specific alert belonging to the authenticated user.
    """
    try:
        deleted = await alerts_service.delete_alert(session=session, user_id=user_id, alert_id=alert_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"message": "Alert deleted successfully"}
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {exc}")

