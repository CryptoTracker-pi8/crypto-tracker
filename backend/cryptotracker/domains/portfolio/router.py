from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from cryptotracker.database.connection import get_db
from cryptotracker.database.models import User
from cryptotracker.domains.portfolio.schemas import (
    PortfolioUpsert, PortfolioRead, InvestmentCreate, InvestmentRead, PortfolioStats
)
from cryptotracker.domains.portfolio.service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

svc = PortfolioService()


# @router.post("", response_model=PortfolioRead, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=None)
async def upsert_portfolio():
    """
    Создать/обновить портфель пользователя (по имени).
    """
    return {"response": "portfolio created/updated, u wanna lose all your money =)?"}


# @router.get("", response_model=PortfolioRead)
@router.get("", response_model=None)
async def get_portfolio():
    """
    Получить текущий портфель пользователя.
    """
    return {"response": "hello"}


# @router.post("/investments", response_model=InvestmentRead, status_code=status.HTTP_201_CREATED)
@router.post("/investments", response_model=None)
async def add_investment():
    """
    Добавить инвестицию в портфель пользователя (портфель создастся при необходимости).
    """
    return {"response": "investment added"}


# @router.get("/stats", response_model=PortfolioStats)
@router.get("/stats", response_model=None)
async def get_stats():
    """
    Посчитать P&L портфеля пользователя.
    """
    return {"response": "buy btc u fucking animal"}


# @router.delete("/investments/{inv_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/investments", response_model=None)
async def delete_investment():
    """
    Удалить инвестицию по ID (проверяем принадлежность пользователю).
    """
    return {"response": "investment deleted, u lose all your money =) u are so goddamn pathetic"}
