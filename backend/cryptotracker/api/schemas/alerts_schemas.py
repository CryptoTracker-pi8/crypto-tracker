from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


AlertDirection = Literal["up", "down", "both"]


class AlertCreate(BaseModel):
    symbol: str = Field(..., description="Currency symbol (e.g., BTC)", min_length=1, max_length=20)
    percent: Decimal = Field(..., gt=0, description="Percentage change threshold (e.g., 1.5)")
    direction: AlertDirection = Field("both", description="Trigger direction: up, down, or both")


class AlertResponse(BaseModel):
    id: int
    symbol: str
    percent: Decimal
    direction: AlertDirection
    is_active: bool
    base_price: Decimal | None
    last_triggered_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse] = Field(default_factory=list)


class AlertDeleteResponse(BaseModel):
    message: str
    alert_id: int
