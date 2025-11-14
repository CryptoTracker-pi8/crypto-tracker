from aiogram.utils.keyboard import InlineKeyboardBuilder

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
