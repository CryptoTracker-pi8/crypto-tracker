from fastapi import APIRouter


router = APIRouter()

@router.get("/health-check")
async def healthcheck():
    return {"status": "ok"}
