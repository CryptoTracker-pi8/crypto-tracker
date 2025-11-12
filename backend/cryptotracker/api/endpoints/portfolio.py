from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from cryptotracker.database.connection import get_db
from cryptotracker.database.models import User
from cryptotracker.api.schemas.portfolio_schemas import (
    PortfolioUpsert, PortfolioRead, InvestmentCreate, InvestmentRead, PortfolioStats
)
from cryptotracker.api.services.portfolio_service import PortfolioService
from cryptotracker.utils.auth import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

svc = PortfolioService()


@router.post("", response_model=PortfolioRead, status_code=status.HTTP_201_CREATED)
async def upsert_portfolio(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioRead:
    """
    Создать/обновить портфель пользователя (по имени).
    """
    try:
        portfolio = await svc.upsert_portfolio(
            db=db,
            user_id=current_user.id,
            name=f"{current_user.username or 'user'+str(current_user.telegram_id)} portfolio"
        )
        return PortfolioRead.model_validate(portfolio)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upsert portfolio: {str(e)}")
    # return {"response": "portfolio created/updated, u wanna lose all your money =)?"}


@router.get("", response_model=PortfolioRead)
async def get_portfolio(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioRead:
    """
    Получить текущий портфель пользователя.
    """
    try:
        portfolio = await svc.get_portfolio(db=db, user_id=current_user.id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return PortfolioRead.model_validate(portfolio)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")


@router.post("/investments", response_model=InvestmentRead, status_code=status.HTTP_201_CREATED)
async def add_investment(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    investment_data: InvestmentCreate = None
) -> InvestmentRead:
    """
    Добавить инвестицию в портфель пользователя (портфель создастся при необходимости).
    """
    try:
        investment = await svc.add_investment(db=db, user_id=current_user.id, **investment_data.model_dump())
        return InvestmentRead.model_validate(investment)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add investment: {str(e)}")
    # return {"response": "investment added"}


@router.get("/stats", response_model=PortfolioStats)
# @router.get("/stats", response_model=None)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioStats:
    """
    Посчитать P&L портфеля пользователя.
    """
    try:
        stats = await svc.calculate_portfolio_stats(db=db, user_id=current_user.id)
        return PortfolioStats.model_validate(stats)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio stats: {str(e)}")
    # return {"response": "buy btc u fucking animal"}


@router.delete("/investments/{inv_id}", response_model=None)
async def delete_investment(
    inv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> str:
    """
    Delete investment by id.
    """
    try:
        success = await svc.delete_investment(db=db, user_id=current_user.id, inv_id=inv_id)
        if not success:
            raise HTTPException(status_code=404, detail="Investment not found")
        return
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete investment: {str(e)}")
    # return {"response": "investment deleted, u lose all your money =) u are so goddamn pathetic"}
