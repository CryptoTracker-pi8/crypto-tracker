from uvicorn import run
from fastapi import FastAPI
from cryptotracker.utils.common.hostname import get_hostname
from cryptotracker.config.default import DefaultSettings
from cryptotracker.config.utils import get_settings
from cryptotracker.domains import router_list

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
    )
    settings = get_settings()
    bind_routes(application, settings)
    application.state.settings = settings
    return application


app = get_app()
