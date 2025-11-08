from os import environ
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """
    Bot configuration settings.
    """
    BOT_TOKEN: str = environ.get("BOT_TOKEN", "")
    API_BASE_URL: str = environ.get("API_BASE_URL", "http://localhost:8080/api/v1")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


_settings: BotSettings | None = None


def get_settings() -> BotSettings:
    """
    Get bot settings (singleton).
    """
    global _settings
    if _settings is None:
        _settings = BotSettings()
    return _settings

