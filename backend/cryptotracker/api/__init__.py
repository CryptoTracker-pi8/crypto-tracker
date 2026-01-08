from cryptotracker.api.endpoints.favorites import router as favorites_router
from cryptotracker.api.endpoints.currencies import router as currencies_router
from cryptotracker.api.endpoints.healthcheck import router as healthcheck_router
from cryptotracker.api.endpoints.portfolio import router as portfolio_router
from cryptotracker.api.endpoints.alerts import router as alerts_router
from cryptotracker.api.endpoints.settings import router as settings_router

router_list = [
    healthcheck_router,
    currencies_router,
    favorites_router,
    portfolio_router,
    alerts_router,
    settings_router,
]
