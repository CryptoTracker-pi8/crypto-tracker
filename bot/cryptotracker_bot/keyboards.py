from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def alert_suggestion_kb() -> dict:
    kb = InlineKeyboardBuilder()
    kb.button(text="Поставить стоп-уведомление −10%", callback_data="set_weekly_dd_-10")
    kb.button(text="Изменить порог…", callback_data="change_threshold")
    return kb.as_markup()

def reports_kb() -> dict:
    kb = InlineKeyboardBuilder()
    kb.button(text="Ежедневный отчет", callback_data="report_daily_on")
    kb.button(text="Еженедельный отчет", callback_data="report_weekly_on")
    kb.button(text="Выключить отчеты", callback_data="reports_off")
    return kb.as_markup()

def main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/status"), KeyboardButton(text="/portfolio")],
            [KeyboardButton(text="/favorites"), KeyboardButton(text="/alert")],
            [KeyboardButton(text="/settings"), KeyboardButton(text="/help")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
