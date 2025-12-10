from aiogram import Dispatcher

from cryptotracker_bot.handlers.basic import register_basic_handlers
from cryptotracker_bot.handlers.portfolio import register_portfolio_handler


def register_handlers(dp: Dispatcher) -> None:
    """
    Register all bot handlers.
    """
    register_basic_handlers(dp)
    register_portfolio_handler(dp)

