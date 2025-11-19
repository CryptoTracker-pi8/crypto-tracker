from datetime import datetime

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    """
    Payload for creating a new alert.
    """

    symbol: str = Field(..., min_length=1, max_length=20, description="Asset symbol (e.g., BTC)")
    threshold_percent: float = Field(..., description="Percentage change that triggers the alert")


class AlertRead(BaseModel):
    """
    Alert details returned to clients.
    """

    id: int = Field(..., description="Alert ID")
    symbol: str = Field(..., description="Asset symbol")
    threshold_percent: float = Field(..., description="Trigger percentage")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True

