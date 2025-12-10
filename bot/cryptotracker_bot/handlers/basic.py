from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from cryptotracker_bot.api_client import api_client


async def cmd_start(message: Message):
    """
    Handle /start command.
    """
    welcome_text = """
<b>Добро пожаловать в Crypto Tracker Bot! 🚀</b>

Я помогу вам отслеживать курсы криптовалют и управлять избранными монетами.

<b>Доступные команды:</b>
/start — показать это приветственное сообщение
/help — показать справку
/status &lt;СИМВОЛ&gt; — узнать текущую цену криптовалюты
/portfolio — информация о вашем портфеле и его статистике

<b>Примеры:</b>
/status BTC — узнать цену Bitcoin
/status ETH — узнать цену Ethereum

Начните с проверки цены криптовалюты: <code>/status BTC</code>
"""
    await message.answer(welcome_text)


async def cmd_help(message: Message):
    """
    Handle /help command.
    """
    help_text = """
<b>Справка по Crypto Tracker Bot</b>

<b>Команды:</b>
• <code>/start</code> — приветственное сообщение
• <code>/help</code> — показать эту справку
• <code>/status &lt;СИМВОЛ&gt;</code> — узнать цену криптовалюты
• <code>/portfolio</code> — получить информацию о портфеле

<b>Использование:</b>
Чтобы узнать цену криптовалюты, введите:
<code>/status BTC</code>
<code>/status ETH</code>
<code>/status SOL</code>

Замените <code>СИМВОЛ</code> на тикер нужной монеты.

<b>Поддерживаемые валюты:</b>
Все основные криптовалюты — BTC, ETH, BNB, SOL и другие.
"""
    await message.answer(help_text)


async def cmd_status(message: Message):
    """
    Handle /status command.
    """
    # Extract symbol from command arguments
    args = message.text.split()[1:] if message.text else []

    if not args:
        await message.answer(
            "❌ Укажите символ криптовалюты.\n\n"
            "Пример использования: <code>/status BTC</code>\n"
            "Пример: <code>/status ETH</code>"
        )
        return

    symbol = args[0].upper()

    await message.answer(f"⏳ Подтягиваем {symbol} цену...")

    currency = await api_client.get_currency(symbol)

    if not currency:
        await message.answer(
            f"❌ Валюта <b>{symbol}</b> не найдена.\n\n"
            "Проверьте правильность символа и попробуйте снова.\n"
            "Пример: <code>/status BTC</code>"
        )
        return

    # Format price
    price = currency.get("price", 0)
    price_change = currency.get("price_change_percentage_24h")
    name = currency.get("name", symbol)

    price_text = f"${price:,.2f}"

    if price_change is not None:
        change_emoji = "📈" if price_change >= 0 else "📉"
        change_sign = "+" if price_change >= 0 else ""
        price_text += f" {change_emoji} {change_sign}{price_change:.2f}%"

    response_text = f"""
<b>{name} ({symbol})</b>

💰 Цена: <b>{price_text}</b>
"""

    if currency.get("market_cap_usd"):
        market_cap = currency["market_cap_usd"] / 1e9
        response_text += f"📊 Рыночная капитализация: ${market_cap:.2f}B\n"

    if currency.get("total_volume"):
        volume = currency["total_volume"] / 1e9
        response_text += f"💹 24ч Объем: ${volume:.2f}B\n"

    await message.answer(response_text)


def register_basic_handlers(dp: Dispatcher) -> None:
    """
    Register basic command handlers.
    """
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_status, Command("status"))

