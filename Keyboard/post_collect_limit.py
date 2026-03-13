from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class PostLimitCBData(CallbackData, prefix='limit_'):
    limit: int

def post_limit_kb():
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(
        text="👟 1 post",
        callback_data=PostLimitCBData(limit=1).pack()
    ))
    keyboard.row(InlineKeyboardButton(
        text="⏱️ 5 posts",
        callback_data=PostLimitCBData(limit=5).pack()
    ))
    keyboard.row(InlineKeyboardButton(
        text="📊 10 posts",
        callback_data=PostLimitCBData(limit=10).pack()
    ))

    return keyboard.as_markup()