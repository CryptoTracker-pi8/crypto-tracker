from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


Theme = Literal["light", "dark"]
NotificationMode = Literal["investor", "trader"]


class SettingsResponse(BaseModel):
    theme: Theme
    notification_mode: NotificationMode
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class SettingsUpdate(BaseModel):
    theme: Theme | None = Field(None, description="UI theme")
    notification_mode: NotificationMode | None = Field(None, description="Notification frequency mode")
