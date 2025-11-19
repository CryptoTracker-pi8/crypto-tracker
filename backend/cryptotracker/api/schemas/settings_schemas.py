from pydantic import BaseModel, Field


class UserSettingsUpdate(BaseModel):
    """
    Payload for updating user settings.
    """

    theme: str | None = Field(None, description="UI theme (light, dark, etc.)", min_length=1, max_length=20)
    notification_mode: str | None = Field(
        None,
        description="Preferred notification channel",
        min_length=1,
        max_length=50,
    )


class UserSettingsRead(BaseModel):
    """
    Settings read model.
    """

    id: int = Field(..., description="Settings ID")
    user_id: int = Field(..., description="Owner user ID")
    theme: str = Field(..., description="Active UI theme")
    notification_mode: str = Field(..., description="Notification preference")

    class Config:
        from_attributes = True

