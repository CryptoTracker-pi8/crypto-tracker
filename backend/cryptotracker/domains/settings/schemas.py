"""
Pydantic schemas for user settings endpoints.
"""

from pydantic import BaseModel, ConfigDict, Field


class UserSettingsBase(BaseModel):
    """
    Shared properties for user settings.
    """

    theme: str = Field(..., min_length=2, max_length=32)
    notification_mode: str = Field(..., min_length=2, max_length=32)


class UserSettingsUpdate(BaseModel):
    """
    Partial update payload for the user settings resource.
    """

    theme: str | None = Field(default=None, min_length=2, max_length=32)
    notification_mode: str | None = Field(default=None, min_length=2, max_length=32)


class UserSettingsRead(UserSettingsBase):
    """
    Response schema returned to API consumers.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

