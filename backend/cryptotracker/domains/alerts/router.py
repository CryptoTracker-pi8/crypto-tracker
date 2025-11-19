"""
FastAPI router for alert related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.db.session import get_db_session
from cryptotracker.domains.alerts import crud
from cryptotracker.domains.alerts.schemas import AlertCreate, AlertRead
from cryptotracker.domains.dependencies import get_current_user_id

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert_endpoint(
    payload: AlertCreate,
    session: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
) -> AlertRead:
    """
    Create a new alert for the authenticated user.
    """

    alert = await crud.create_alert(session=session, user_id=user_id, payload=payload)
    return AlertRead.model_validate(alert)


@router.get("", response_model=list[AlertRead])
async def list_alerts_endpoint(
    session: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
) -> list[AlertRead]:
    """
    List all alerts registered by the authenticated user.
    """

    alerts = await crud.list_alerts(session=session, user_id=user_id)
    return [AlertRead.model_validate(alert) for alert in alerts]


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_endpoint(
    alert_id: int,
    session: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
) -> None:
    """
    Delete a user alert by its identifier.
    """

    deleted = await crud.delete_alert(session=session, alert_id=alert_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

