from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from cryptotracker_bot.api_client import api_client


async def cmd_start(message: Message):
    """
    Handle /start command.
    """
    welcome_text = """
<b>Welcome to Crypto Tracker Bot! 🚀</b>

I can help you track cryptocurrency prices and manage your favorites.

<b>Available commands:</b>
/start - Show this welcome message
/help - Show help information
/status &lt;SYMBOL&gt; - Get current price for a cryptocurrency

<b>Examples:</b>
/status BTC - Get Bitcoin price
/status ETH - Get Ethereum price

Start by checking a currency price with /status BTC
"""
    await message.answer(welcome_text)


async def cmd_help(message: Message):
    """
    Handle /help command.
    """
    help_text = """
<b>Crypto Tracker Bot Help</b>

<b>Commands:</b>
• <code>/start</code> - Welcome message
• <code>/help</code> - Show this help
• <code>/status &lt;SYMBOL&gt;</code> - Get currency price

<b>Usage:</b>
To check a cryptocurrency price, use:
<code>/status BTC</code>
<code>/status ETH</code>
<code>/status SOL</code>

Replace SYMBOL with the currency symbol you want to check.

<b>Supported currencies:</b>
All major cryptocurrencies are supported (BTC, ETH, BNB, SOL, etc.)
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
            "❌ Please provide a currency symbol.\n\n"
            "Usage: <code>/status BTC</code>\n"
            "Example: <code>/status ETH</code>"
        )
        return

    symbol = args[0].upper()

    await message.answer(f"⏳ Fetching {symbol} price...")

    currency = await api_client.get_currency(symbol)

    if not currency:
        await message.answer(
            f"❌ Currency <b>{symbol}</b> not found.\n\n"
            "Please check the symbol and try again.\n"
            "Example: <code>/status BTC</code>"
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

💰 Price: <b>{price_text}</b>
"""

    if currency.get("market_cap_usd"):
        market_cap = currency["market_cap_usd"] / 1e9
        response_text += f"📊 Market Cap: ${market_cap:.2f}B\n"

    if currency.get("total_volume"):
        volume = currency["total_volume"] / 1e9
        response_text += f"💹 24h Volume: ${volume:.2f}B\n"

    await message.answer(response_text)


def register_basic_handlers(dp: Dispatcher) -> None:
    """
    Register basic command handlers.
    """
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_status, Command("status"))

