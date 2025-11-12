from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.database.connection import get_db
from cryptotracker.database.models import User
from cryptotracker.api.schemas.portfolio_schemas import (
    PortfolioCreateOrEdit, PortfolioRead, InvestmentCreate, InvestmentRead, PortfolioStats,
    PortfolioManipulations
)
from cryptotracker.api.services.portfolio_service import PortfolioService
from cryptotracker.utils.auth import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

svc = PortfolioService()


@router.post("", response_model=PortfolioManipulations) # fine
async def create_or_edit_portfolio(
    payload: PortfolioCreateOrEdit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioManipulations:
    """
    Create/edit user portfolio
    """
    try:
        p, created = await svc.upsert_portfolio(
            db,
            user_id=current_user.id,
            name=payload.name,
            create=payload.flag,
            new_name=payload.new_name,
        )
        if created:
            return PortfolioManipulations.model_validate({ **p.__dict__, "status": "created"})
        else:
            return PortfolioManipulations.model_validate({ **p.__dict__, "status": "edited"})
    except HTTPException:
        raise


@router.get("", response_model=PortfolioRead) # fine
async def get_portfolio(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioRead:
    """
    Get user portfolio
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
    Add investment into user portfolio
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


@router.get("/stats", response_model=PortfolioStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioStats:
    """
    Get portfolio stats
    """
    try:
        stats = await svc.get_stats(db=db, user_id=current_user.id)
        return stats
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio stats: {str(e)}")


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
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "investment deleted successfully"})
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete investment: {str(e)}")
