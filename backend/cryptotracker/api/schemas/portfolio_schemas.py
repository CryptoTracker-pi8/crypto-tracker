from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class InvestmentCreate(BaseModel):
    symbol: str = Field(..., description="e.g. BTC", min_length=1, max_length=20)
    amount: Decimal = Field(..., gt=0, description="Quantity of asset")
    buy_price: Decimal = Field(..., ge=0, description="USD price at buy time")
    bought_at: Optional[datetime] = Field(None, description="Purchase timestamp (optional)")


class InvestmentRead(BaseModel):
    id: int
    symbol: str
    amount: Decimal
    buy_price: Decimal
    bought_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class PortfolioCreateOrEdit(BaseModel):
    name: str = Field(..., description="User-defined portfolio name", min_length=1, max_length=100)
    flag: bool = Field(False, description="True = create new; False = edit exist")
    new_name: str | None = Field(None, description="New name for already existing portfolio", min_length=1, max_length=100)


class PortfolioRead(BaseModel):
    id: int
    user_id: int
    name: str
    investments: List[InvestmentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class PortfolioManipulations(BaseModel):
    id: int
    user_id: int
    name: str
    investments: List[InvestmentRead] = Field(default_factory=list)
    status: str

    model_config = ConfigDict(from_attributes=True)


class PortfolioStats(BaseModel):
    total_invested: Decimal = Field(..., description="Σ amount * buy_price")
    current_value: Decimal = Field(..., description="Current market value")
    pnl_abs: Decimal = Field(..., description="Absolute P&L")
    pnl_pct: Decimal = Field(..., description="Relative P&L, %")
