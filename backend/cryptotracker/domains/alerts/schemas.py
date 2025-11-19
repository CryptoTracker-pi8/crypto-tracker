"""
Pydantic schemas for alert endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class AlertBase(BaseModel):
    """
    Shared alert properties.
    """

    symbol: str = Field(..., min_length=1, max_length=32)
    threshold_percent: float = Field(..., gt=0, description="Percentage change threshold.")


class AlertCreate(AlertBase):
    """
    Payload used to create a new alert.
    """


class AlertRead(AlertBase):
    """
    Response model for alert endpoints.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

