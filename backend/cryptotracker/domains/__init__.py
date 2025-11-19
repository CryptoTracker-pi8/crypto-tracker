"""
Domain routers exposed by the application.
"""

from cryptotracker.domains.alerts import router as alerts_router
from cryptotracker.domains.healthcheck.router import router as healthcheck_router
from cryptotracker.domains.settings import router as settings_router

router_list = [
    healthcheck_router,
    alerts_router,
    settings_router,
]
