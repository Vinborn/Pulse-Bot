from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class PostLimitCBData(CallbackData, prefix='limit_'):
    limit: int

def post_limit_kb():
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(
        text="👟 3 posts",
        callback_data=PostLimitCBData(limit=3).pack()
    ))
    keyboard.row(InlineKeyboardButton(
        text="⏱️ 7 posts",
        callback_data=PostLimitCBData(limit=7).pack()
    ))
    keyboard.row(InlineKeyboardButton(
        text="📊 10 posts",
        callback_data=PostLimitCBData(limit=10).pack()
    ))

    return keyboard.as_markup()