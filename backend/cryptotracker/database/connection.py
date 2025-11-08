from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cryptotracker.config.utils import get_settings
from cryptotracker.database.base import Base

# Global engine and session factory
_engine = None
_async_session = None


def get_engine():
    """
    Get or create database engine.
    """
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(settings.database_uri, echo=True)
    return _engine


def get_session_factory():
    """
    Get or create session factory.
    """
    global _async_session
    if _async_session is None:
        engine = get_engine()
        _async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return _async_session


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session.
    """
    async_session = get_session_factory()
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database - create all tables.
    """
    engine = get_engine()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()

