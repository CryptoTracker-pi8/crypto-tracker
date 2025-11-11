from backend.cryptotracker.api.endpoints.favorites import router as favorites_router
from backend.cryptotracker.api.endpoints.currencies import router as currencies_router
from backend.cryptotracker.api.endpoints.healthcheck import router as healthcheck_router

router_list = [
    healthcheck_router,
    currencies_router,
    favorites_router,
]
