from aiogram import Dispatcher, types
from aiogram.filters import Command

from cryptotracker_bot.api_client import APIClient
from cryptotracker_bot.keyboards import main_kb


_THEMES = {"light", "dark"}
_MODES = {"investor", "trader"}


async def cmd_settings(message: types.Message, api: APIClient):
    """
    Show or update user settings.
    """
    args = message.text.split()[1:] if message.text else []

    if not args:
        try:
            settings = await api.get_settings()
        except Exception as e:
            await message.answer(f"Не удалось получить настройки: {e}", reply_markup=main_kb())
            return

        theme = settings.get("theme", "light")
        mode = settings.get("notification_mode", "investor")
        updated_at = settings.get("updated_at") or "—"

        await message.answer(
            "<b>Настройки</b>\n"
            f"Тема: <b>{theme}</b>\n"
            f"Режим уведомлений: <b>{mode}</b>\n"
            f"Обновлено: <b>{updated_at}</b>\n\n"
            "Изменить:\n"
            "<code>/settings theme dark</code>\n"
            "<code>/settings mode trader</code>",
            reply_markup=main_kb(),
        )
        return

    if len(args) == 1:
        value = args[0].lower()
        if value in _THEMES:
            args = ["theme", value]
        elif value in _MODES:
            args = ["mode", value]

    updates = {}
    i = 0
    while i < len(args):
        key = args[i].lower()
        if key == "theme":
            if i + 1 >= len(args):
                await message.answer("Укажите тему: <code>/settings theme dark</code>", reply_markup=main_kb())
                return
            value = args[i + 1].lower()
            if value not in _THEMES:
                await message.answer(
                    "Тема должна быть <code>light</code> или <code>dark</code>.",
                    reply_markup=main_kb(),
                )
                return
            updates["theme"] = value
            i += 2
            continue

        if key in ("mode", "notification_mode"):
            if i + 1 >= len(args):
                await message.answer("Укажите режим: <code>/settings mode trader</code>", reply_markup=main_kb())
                return
            value = args[i + 1].lower()
            if value not in _MODES:
                await message.answer(
                    "Режим должен быть <code>investor</code> или <code>trader</code>.",
                    reply_markup=main_kb(),
                )
                return
            updates["notification_mode"] = value
            i += 2
            continue

        await message.answer(
            "Использование:\n"
            "<code>/settings</code> — показать настройки\n"
            "<code>/settings theme dark</code> — тема\n"
            "<code>/settings mode trader</code> — режим уведомлений",
            reply_markup=main_kb(),
        )
        return

    if not updates:
        await message.answer("Нет изменений. Пример: <code>/settings mode trader</code>", reply_markup=main_kb())
        return

    try:
        settings = await api.update_settings(
            theme=updates.get("theme"),
            notification_mode=updates.get("notification_mode"),
        )
    except Exception as e:
        await message.answer(f"Не удалось обновить настройки: {e}", reply_markup=main_kb())
        return

    theme = settings.get("theme", "light")
    mode = settings.get("notification_mode", "investor")
    await message.answer(
        "✅ Настройки обновлены.\n"
        f"Тема: <b>{theme}</b>\n"
        f"Режим уведомлений: <b>{mode}</b>",
        reply_markup=main_kb(),
    )


def register_settings_handler(dp: Dispatcher) -> None:
    """
    Register settings command handlers.
    """
    dp.message.register(cmd_settings, Command("settings"))
