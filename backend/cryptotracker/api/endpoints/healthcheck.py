from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from cryptotracker.database.connection import get_engine

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    database: str


@router.get("/health-check", response_model=HealthCheckResponse)
async def healthcheck():
    db_ok = True
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return HealthCheckResponse(
        status="ok" if db_ok else "degraded",
        version="1.0.0",
        database="connected" if db_ok else "disconnected",
    )