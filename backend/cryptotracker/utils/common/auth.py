from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cryptotracker.database.connection import get_session
from cryptotracker.database.models import User


async def get_current_user_id(
    session: AsyncSession = Depends(get_session),
    x_telegram_id: int | None = Header(None, alias="X-Telegram-ID"),
    x_telegram_username: str | None = Header(None, alias="X-Telegram-Username"),
) -> int:
    """
    Resolve the current user's ID from headers, creating the user on the fly if necessary.
    """
    if not x_telegram_id:
        raise HTTPException(status_code=401, detail="X-Telegram-ID header is required")

    result = await session.execute(select(User).where(User.telegram_id == x_telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=x_telegram_id, username=x_telegram_username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    elif x_telegram_username and user.username != x_telegram_username:
        user.username = x_telegram_username
        await session.commit()
        await session.refresh(user)

    return user.id

