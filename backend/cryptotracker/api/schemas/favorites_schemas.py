from datetime import datetime

from pydantic import BaseModel, Field


class FavoriteCreate(BaseModel):
    """
    Schema for creating a favorite.
    """
    currency_symbol: str = Field(..., description="Currency symbol (e.g., BTC, ETH)", min_length=1, max_length=10)


class FavoriteResponse(BaseModel):
    """
    Schema for favorite response.
    """
    id: int = Field(..., description="Favorite ID")
    currency_symbol: str = Field(..., description="Currency symbol")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    """
    Response schema for favorite list.
    """
    favorites: list[FavoriteResponse] = Field(..., description="List of favorites")


class FavoriteDeleteResponse(BaseModel):
    """
    Response schema for favorite deletion.
    """
    message: str = Field(..., description="Success message")
    currency_symbol: str = Field(..., description="Deleted currency symbol")

