from aiogram import Dispatcher

from cryptotracker_bot.handlers.basic import register_basic_handlers
from cryptotracker_bot.handlers.favorites import register_favorites_handler
from cryptotracker_bot.handlers.alerts import register_alerts_handler
from cryptotracker_bot.handlers.portfolio import register_portfolio_handler
from cryptotracker_bot.handlers.settings import register_settings_handler


def register_handlers(dp: Dispatcher) -> None:
    """
    Register all bot handlers.
    """
    register_basic_handlers(dp)
    register_favorites_handler(dp)
    register_alerts_handler(dp)
    register_portfolio_handler(dp)
    register_settings_handler(dp)
