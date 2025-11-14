from aiogram import Router, types
from aiogram.filters import Command
from cryptotracker_bot.api_client import APIClient
from aiogram import Dispatcher
from decimal import Decimal, ROUND_HALF_UP

router = Router()

def _fmt_money(x: Decimal, places: int = 2) -> str:
    q = Decimal(10) ** -places
    return f"{x.quantize(q, rounding=ROUND_HALF_UP):,}".replace(",", " ")

async def cmd_portfolio_with_args(m: types.Message, api: APIClient):
    """
    Get info about user portfolio + portfolio stats
    """
    try:
        data = await api.get_portfolio()
    except Exception as e:
        await m.answer(f"Не удалось получить портфель: {e}")
        return

    inv = (data or {}).get("investments") or []
    if not inv:
        name = (data or {}).get("name", "Портфель")
        await m.answer(f"💼 <b>{name}</b>\nПока нет позиций.")
        return

    from datetime import datetime
    def _fmt_dt(iso: str) -> str:
        try:
            return datetime.fromisoformat(iso).strftime("%d.%m.%Y %H:%M")
        except Exception:
            return iso or "—"

    lines = []
    total_invested = Decimal("0")
    for inv_item in inv:
        sym = inv_item["symbol"]
        amt = Decimal(inv_item["amount"])
        price = Decimal(inv_item["buy_price"])
        invested = amt * price
        total_invested += invested
        when = _fmt_dt(inv_item.get("bought_at", ""))

        lines.append(
            f"<b>{sym}</b> — {amt} @ {_fmt_money(price)} = {_fmt_money(invested)} USD"
            + (f"  ({when})" if inv_item.get("bought_at") else "")
        )

    name = data.get("name", f"Портфель #{data.get('id')}")

    try:
        s = await api.get_portfolio_stats()
    except Exception as e:
        await m.answer(f"Не удалось получить статистику: {e}")
        return

    if not s:
        await m.answer("Статистика недоступна.")
        return

    total_invested = Decimal(s.get("total_invested", "0"))
    current_value  = Decimal(s.get("current_value", "0"))
    pnl_abs        = Decimal(s.get("pnl_abs", "0"))
    pnl_pct        = Decimal(s.get("pnl_pct", "0"))

    sign = "🟢" if pnl_abs >= 0 else "🔴"
    stats = (
        f"\n📊 <b>Статистика портфеля</b>\n"
        f"Вложено: <b>{_fmt_money(total_invested)}</b> USD\n"
        f"Текущая стоимость: <b>{_fmt_money(current_value)}</b> USD\n"
        f"{sign} PnL: <b>{_fmt_money(pnl_abs)}</b>  (<b>{pnl_pct:+.2f}%</b>)"
        )

    await m.answer(
        "💼 <b>{}</b>\n{}\n\nИтого (по ценам покупки): <b>{}</b> USD \n {}".format(
            name, "\n".join(lines), _fmt_money(total_invested), stats
        )
    )


def register_portfolio_handler(dp: Dispatcher) -> None:
    """
    Register favorite command handlers.
    """
    dp.message.register(cmd_portfolio_with_args, Command("portfolio"))