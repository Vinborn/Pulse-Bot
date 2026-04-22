from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def change_language_kb():
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(
            text="English",
            callback_data='lan_en'
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            text="Ukrainian",
            callback_data='lan_ukr'
        )
    )

    return keyboard.as_markup()