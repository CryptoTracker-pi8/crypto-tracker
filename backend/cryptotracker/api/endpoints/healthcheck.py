from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    version: str


@router.get("/health-check", response_model=HealthCheckResponse)
async def healthcheck():
    return HealthCheckResponse(
        status="ok",
        version="1.0.0"
    )