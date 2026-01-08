from aiogram import Dispatcher, types
from aiogram.filters import Command

from cryptotracker_bot.api_client import APIClient
from cryptotracker_bot.keyboards import main_kb


async def cmd_favorites(message: types.Message, api: APIClient):
    """
    Show or manage favorites.
    """
    args = message.text.split()[1:] if message.text else []

    if not args:
        try:
            favorites = await api.get_favorites()
        except Exception as e:
            await message.answer(f"Не удалось получить избранное: {e}", reply_markup=main_kb())
            return

        if not favorites:
            await message.answer(
                "⭐ Избранных валют пока нет.\nДобавить: <code>/favorites add BTC</code>",
                reply_markup=main_kb(),
            )
            return

        lines = []
        for fav in favorites:
            if isinstance(fav, dict):
                symbol = fav.get("currency_symbol") or fav.get("symbol") or str(fav)
            else:
                symbol = str(fav)
            lines.append(f"• <b>{symbol.upper()}</b>")

        text = "⭐ <b>Избранное</b>\n" + "\n".join(lines)
        text += "\n\nДобавить: <code>/favorites add BTC</code>\nУдалить: <code>/favorites delete BTC</code>"
        await message.answer(text, reply_markup=main_kb())
        return

    action = args[0].lower()

    if action in ("add", "+", "plus"):
        if len(args) < 2:
            await message.answer("Укажите символ: <code>/favorites add BTC</code>", reply_markup=main_kb())
            return
        symbol = args[1].upper()
        try:
            await api.add_favorite(symbol)
        except Exception as e:
            await message.answer(f"Не удалось добавить в избранное: {e}", reply_markup=main_kb())
            return
        await message.answer(f"⭐ <b>{symbol}</b> добавлена в избранное.", reply_markup=main_kb())
        return

    if action in ("delete", "del", "remove", "rm", "-"):
        if len(args) < 2:
            await message.answer("Укажите символ: <code>/favorites delete BTC</code>", reply_markup=main_kb())
            return
        symbol = args[1].upper()
        try:
            await api.delete_favorite(symbol)
        except Exception as e:
            await message.answer(f"Не удалось удалить из избранного: {e}", reply_markup=main_kb())
            return
        await message.answer(f"🗑️ <b>{symbol}</b> удалена из избранного.", reply_markup=main_kb())
        return

    if len(args) == 1:
        symbol = args[0].upper()
        try:
            await api.add_favorite(symbol)
        except Exception as e:
            await message.answer(f"Не удалось добавить в избранное: {e}", reply_markup=main_kb())
            return
        await message.answer(f"⭐ <b>{symbol}</b> добавлена в избранное.", reply_markup=main_kb())
        return

    await message.answer(
        "Использование:\n"
        "<code>/favorites</code> — список\n"
        "<code>/favorites add BTC</code> — добавить\n"
        "<code>/favorites delete BTC</code> — удалить",
        reply_markup=main_kb(),
    )


def register_favorites_handler(dp: Dispatcher) -> None:
    """
    Register favorites command handlers.
    """
    dp.message.register(cmd_favorites, Command("favorites"))
