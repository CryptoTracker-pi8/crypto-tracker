from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.database.connection import get_db
from cryptotracker.database.models import User
from backend.cryptotracker.api.schemas.favorites_schemas import (
    FavoriteCreate,
    FavoriteDeleteResponse,
    FavoriteListResponse,
    FavoriteResponse,
)
from backend.cryptotracker.api.services.favorite_service import FavoritesService

router = APIRouter(prefix="/favorites", tags=["favorites"])

# Initialize service
favorites_service = FavoritesService()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    x_telegram_id: int = Header(None, alias="X-Telegram-ID"),
) -> User:
    """
    Get current user from Telegram ID header.
    For MVP, we'll use Telegram ID for authentication.
    """
    if not x_telegram_id:
        raise HTTPException(status_code=401, detail="X-Telegram-ID header is required")
    
    user = await favorites_service.get_or_create_user_by_telegram_id(db, x_telegram_id)
    return user


@router.post("", response_model=FavoriteResponse, status_code=201)
async def create_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a currency to favorites.
    """
    try:
        favorite = await favorites_service.create_favorite(
            db=db,
            user_id=current_user.id,
            currency_symbol=favorite_data.currency_symbol
        )
        return FavoriteResponse(
            id=favorite.id,
            currency_symbol=favorite.currency_symbol,
            created_at=favorite.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create favorite: {str(e)}")


@router.get("", response_model=FavoriteListResponse)
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all favorites for the current user.
    """
    try:
        favorites = await favorites_service.get_user_favorites(db=db, user_id=current_user.id)
        return FavoriteListResponse(
            favorites=[
                FavoriteResponse(
                    id=fav.id,
                    currency_symbol=fav.currency_symbol,
                    created_at=fav.created_at
                )
                for fav in favorites
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch favorites: {str(e)}")


@router.delete("/{currency_symbol}", response_model=FavoriteDeleteResponse)
async def delete_favorite(
    currency_symbol: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a currency from favorites.
    """
    try:
        deleted = await favorites_service.delete_favorite(
            db=db,
            user_id=current_user.id,
            currency_symbol=currency_symbol
        )
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Favorite {currency_symbol} not found")
        return FavoriteDeleteResponse(
            message="Favorite deleted successfully",
            currency_symbol=currency_symbol.upper()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete favorite: {str(e)}")

