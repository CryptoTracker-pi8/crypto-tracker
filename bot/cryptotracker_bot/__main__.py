import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from .api_client import APIClient

from cryptotracker_bot.config import get_settings
from cryptotracker_bot.handlers import register_handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Main function to start the bot.
    """
    settings = get_settings()

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    async def api_inject_mw(handler, event, data):
        tg_id = getattr(getattr(event, "from_user", None), "id", None)
        data["api"] = APIClient(tg_user_id=str(tg_id) if tg_id else None)
        return await handler(event, data)

    dp.message.middleware(api_inject_mw)
    dp.callback_query.middleware(api_inject_mw)

    # Register handlers
    register_handlers(dp)

    logger.info("Bot started")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

