import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from cryptotracker.config.default import DefaultSettings
from cryptotracker.config.utils import get_settings
from cryptotracker.api import router_list
from cryptotracker.database.connection import init_db
from fastapi import Request
from fastapi.responses import JSONResponse


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for app startup and shutdown.
    """
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")

    yield

    # Shutdown
    logger.info("Shutting down application.")

def bind_routes(application: FastAPI, setting: DefaultSettings) -> None:
    """
    Bind all routes to application.
    """
    for router in router_list:
        application.include_router(router, prefix=setting.PATH_PREFIX)



def get_app() -> FastAPI:
    """
    Creates application and all dependable objects.
    """
    description = "Микросервис для отслеживания курса криптовалют."


    application = FastAPI(
        title="Crypto Tracker",
        description=description,
        docs_url="/swagger",
        openapi_url="/openapi",
        version="1.0.0",
        lifespan=lifespan,
    )
    settings = get_settings()
    bind_routes(application, settings)
    application.state.settings = settings
    
    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception occurred")

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
            },
        )
    return application


app = get_app()
