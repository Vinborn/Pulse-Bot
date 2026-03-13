"""СОЗДАНИЕ РАСПОЛОЖЕНИЯ КНОПОК ДЛЯ СПИСКА КАНАЛОВ"""
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# класс ChannelCBData имеет поле channel_id которое хранит в себе tg_id определенного канала
class ChannelInfoCBData(CallbackData, prefix='ch'):
    channel_id: int

# класс ChannelDeleteCBData имеет поле channel_id для удаления из БД
class ChannelDeleteCBData(CallbackData, prefix='delete'):
    channel_id: int

def generate_channel_list_kb(channels):
    keyboard = InlineKeyboardBuilder()

    # проходимся по таблице channels и добавляем кнопки
    for channel in channels:
        # создаем кнопку с названием канала
        keyboard.row(
            InlineKeyboardButton(text=channel.title, callback_data=ChannelInfoCBData(channel_id=channel.tg_id).pack()),
            InlineKeyboardButton(text="❌", callback_data=ChannelDeleteCBData(channel_id=channel.tg_id).pack()),
        )

    return keyboard.as_markup()