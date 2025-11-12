from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class InvestmentCreate(BaseModel):
    """
    Вход для добавления инвестиции.
    """
    symbol: str = Field(..., description="e.g. BTC", min_length=1, max_length=20)
    amount: float = Field(..., gt=0, description="Quantity of asset")
    buy_price: float = Field(..., ge=0, description="USD price at buy time")
    bought_at: Optional[datetime] = Field(None, description="Purchase timestamp (optional)")


class InvestmentRead(BaseModel):
    """
    Выходная модель инвестиции.
    """
    id: int
    symbol: str
    amount: float
    buy_price: float
    bought_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class PortfolioUpsert(BaseModel):
    """
    Вход для создания/обновления портфеля.
    """
    name: str = Field(..., description="User-defined portfolio name", min_length=1, max_length=100)


class PortfolioRead(BaseModel):
    """
    Выходная модель портфеля.
    """
    id: int
    user_id: int
    name: str
    investments: List[InvestmentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PortfolioStats(BaseModel):
    """
    Ответ статистики портфеля.
    """
    total_invested: float = Field(..., description="Σ amount * buy_price")
    current_value: float = Field(..., description="Current market value")
    pnl_abs: float = Field(..., description="Absolute P&L")
    pnl_pct: float = Field(..., description="Relative P&L, %")
