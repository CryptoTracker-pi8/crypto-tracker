from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CurrencyPrice(BaseModel):
    """
    Currency price schema.
    """
    symbol: str = Field(..., description="Currency symbol (e.g., BTC, ETH)")
    name: str = Field(..., description="Currency name")
    price_usd: float = Field(..., description="Price in USD", alias="price")
    price_change_24h: Optional[float] = Field(None, description="Price change in 24h (%)", alias="price_change_percentage_24h")
    market_cap: Optional[float] = Field(None, description="Market capitalization", alias="market_cap_usd")
    volume_24h: Optional[float] = Field(None, description="24h trading volume", alias="total_volume")
    
    class Config:
        populate_by_name = True


class CurrencyHistoryPoint(BaseModel):
    """
    Currency history point schema.
    """
    timestamp: datetime = Field(..., description="Timestamp")
    price: float = Field(..., description="Price in USD")


class CurrencyListResponse(BaseModel):
    """
    Response schema for currency list.
    """
    currencies: list[CurrencyPrice] = Field(..., description="List of currencies")


class CurrencyDetailResponse(BaseModel):
    """
    Response schema for currency detail.
    """
    currency: CurrencyPrice = Field(..., description="Currency details")


class CurrencyHistoryResponse(BaseModel):
    """
    Response schema for currency history.
    """
    symbol: str = Field(..., description="Currency symbol")
    history: list[CurrencyHistoryPoint] = Field(..., description="Price history")

