"""
Async SQLAlchemy session and engine factories.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from cryptotracker.config.utils import get_settings

settings = get_settings()

async_engine = create_async_engine(
    settings.database_uri,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a scoped AsyncSession.
    """

    async with async_session_factory() as session:
        yield session

