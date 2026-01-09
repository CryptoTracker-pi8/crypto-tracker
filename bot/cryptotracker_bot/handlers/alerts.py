from decimal import Decimal, InvalidOperation
from aiogram import Dispatcher, types
from aiogram.filters import Command

from cryptotracker_bot.api_client import APIClient
from cryptotracker_bot.keyboards import main_kb


_DIRECTION_ALIASES = {
    "up": "up",
    "down": "down",
    "both": "both",
    "±": "both",
    "+-": "both",
    "+": "up",
    "-": "down",
}


def _parse_percent(raw: str) -> Decimal | None:
    cleaned = raw.strip().replace("%", "").replace(",", ".")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return None
    if value <= 0:
        return None
    return value


def _format_direction(direction: str) -> str:
    if direction == "up":
        return "⬆️"
    if direction == "down":
        return "⬇️"
    return "⬆️⬇️"


async def cmd_alert(message: types.Message, api: APIClient):
    """
    Create/list/delete alerts.
    """
    args = message.text.split()[1:] if message.text else []

    if not args:
        await message.answer(
            "Использование:\n"
            "<code>/alert BTC 1.5</code> — создать алерт ±1.5%\n"
            "<code>/alert BTC 1.5 up</code> — только рост\n"
            "<code>/alert list</code> — список алертов\n"
            "<code>/alert delete 3</code> — удалить алерт по id",
            reply_markup=main_kb(),
        )
        return

    action = args[0].lower()

    if action in ("list", "ls"):
        try:
            alerts = await api.list_alerts()
        except Exception as e:
            await message.answer(f"Не удалось получить алерты: {e}", reply_markup=main_kb())
            return

        if not alerts:
            await message.answer(
                "🔔 Алертов пока нет. Добавьте: <code>/alert BTC 1.5</code>",
                reply_markup=main_kb(),
            )
            return

        lines = []
        for item in alerts:
            alert_id = item.get("id")
            symbol = (item.get("symbol") or "").upper()
            percent = item.get("percent")
            direction = item.get("direction", "both")
            is_active = item.get("is_active", True)
            status = "✅" if is_active else "⏸"
            lines.append(
                f"{status} <b>#{alert_id}</b> {symbol} — {percent}% {_format_direction(direction)}"
            )

        text = "🔔 <b>Ваши алерты</b>\n" + "\n".join(lines)
        text += "\n\nУдалить: <code>/alert delete ID</code>"
        await message.answer(text, reply_markup=main_kb())
        return

    if action in ("delete", "del", "remove", "rm"):
        if len(args) < 2:
            await message.answer("Укажите id алерта: <code>/alert delete 3</code>", reply_markup=main_kb())
            return
        try:
            alert_id = int(args[1])
        except ValueError:
            await message.answer(
                "ID должен быть числом. Пример: <code>/alert delete 3</code>",
                reply_markup=main_kb(),
            )
            return

        try:
            await api.delete_alert(alert_id)
        except Exception as e:
            await message.answer(f"Не удалось удалить алерт: {e}", reply_markup=main_kb())
            return
        await message.answer(f"🗑️ Алерт <b>#{alert_id}</b> удален.", reply_markup=main_kb())
        return

    if len(args) < 2:
        await message.answer(
            "Укажите символ и процент.\n"
            "Пример: <code>/alert BTC 1.5</code> или <code>/alert BTC 1.5 up</code>",
            reply_markup=main_kb(),
        )
        return

    symbol = args[0].upper()
    percent = _parse_percent(args[1])
    if percent is None:
        await message.answer("Неверный процент. Пример: <code>/alert BTC 1.5</code>", reply_markup=main_kb())
        return

    direction_raw = args[2].lower() if len(args) >= 3 else "both"
    direction = _DIRECTION_ALIASES.get(direction_raw)
    if not direction:
        await message.answer(
            "Направление должно быть: <code>up</code>, <code>down</code> или <code>both</code>.",
            reply_markup=main_kb(),
        )
        return

    try:
        created = await api.create_alert(symbol, str(percent), direction)
    except Exception as e:
        await message.answer(f"Не удалось создать алерт: {e}", reply_markup=main_kb())
        return

    alert_id = created.get("id")
    await message.answer(
        f"🔔 Алерт создан: <b>#{alert_id}</b> {symbol} — {percent}% {_format_direction(direction)}",
        reply_markup=main_kb(),
    )


def register_alerts_handler(dp: Dispatcher) -> None:
    """
    Register alert command handlers.
    """
    dp.message.register(cmd_alert, Command("alert"))
