from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.database.connection import get_db
from cryptotracker.database.models import User
from cryptotracker.domains.favorites.service import FavoritesService


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
