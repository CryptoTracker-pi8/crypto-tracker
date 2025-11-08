from cryptotracker.domains.currencies.router import router as currencies_router
from cryptotracker.domains.favorites.router import router as favorites_router
from cryptotracker.domains.healthcheck.router import router as healthcheck_router

router_list = [
    healthcheck_router,
    currencies_router,
    favorites_router,
]
