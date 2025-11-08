from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.database.models import Favorite, User


class FavoritesService:
    """
    Service for managing user favorites.
    """
    
    async def create_favorite(self, db: AsyncSession, user_id: int, currency_symbol: str) -> Favorite:
        """
        Create a new favorite for a user.
        """
        # Check if favorite already exists
        existing = await db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.currency_symbol == currency_symbol.upper()
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Currency {currency_symbol} is already in favorites")
        
        favorite = Favorite(
            user_id=user_id,
            currency_symbol=currency_symbol.upper()
        )
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        return favorite
    
    async def get_user_favorites(self, db: AsyncSession, user_id: int) -> list[Favorite]:
        """
        Get all favorites for a user.
        """
        result = await db.execute(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def delete_favorite(self, db: AsyncSession, user_id: int, currency_symbol: str) -> bool:
        """
        Delete a favorite for a user.
        """
        result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.currency_symbol == currency_symbol.upper()
            )
        )
        favorite = result.scalar_one_or_none()
        if not favorite:
            return False
        
        await db.delete(favorite)
        await db.commit()
        return True
    
    async def get_or_create_user_by_telegram_id(self, db: AsyncSession, telegram_id: int, username: str = None) -> User:
        """
        Get or create a user by Telegram ID.
        """
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        elif username and user.username != username:
            user.username = username
            await db.commit()
            await db.refresh(user)
        
        return user

