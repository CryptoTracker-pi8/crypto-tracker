from aiogram import Dispatcher

from cryptotracker_bot.handlers.basic import register_basic_handlers


def register_handlers(dp: Dispatcher) -> None:
    """
    Register all bot handlers.
    """
    register_basic_handlers(dp)

