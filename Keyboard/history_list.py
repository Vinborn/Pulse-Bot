from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Database import Summary


class ChannelPulseHistoryCBData(CallbackData, prefix="ch_pulse_history"):
    channel_id: int

class PulseInfoCBData(CallbackData, prefix="pulse_info"):
    channel_id: int
    post_id: int

def generate_history_list_kb(channels):
    keyboard = InlineKeyboardBuilder()

    # проходимся по таблице channels и добавляем кнопки
    for channel in channels:
        # создаем кнопку с названием канала
        keyboard.row(
            InlineKeyboardButton(text=channel.title, callback_data=ChannelPulseHistoryCBData(channel_id=channel.tg_id).pack())
        )

    return keyboard.as_markup()

def generate_channel_pulse_history_kb(summaries: list[Summary]):
    keyboard = InlineKeyboardBuilder()

    for summary in summaries:
        keyboard.row(
            InlineKeyboardButton(
                text=summary.summary_date.strftime("%m/%d/%Y"),
                callback_data=PulseInfoCBData(channel_id=summary.channel_id, post_id=summary.last_included_post_id).pack()
            )
        )

    keyboard.row(InlineKeyboardButton(text="Back", callback_data="history_list"))
    return keyboard.as_markup()