from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

class ChannelPulseHistoryCBData(CallbackData, prefix="ch_pulse_history"):
    channel_id: int

class PulseInfoCBData(CallbackData, prefix="pulse_info"):
    channel_id: int
    post_id: int

class TurnPageCBData(CallbackData, prefix="turn_page"):
    current_page: int
    channel_id: int

def generate_history_list_kb(channels):
    keyboard = InlineKeyboardBuilder()

    # проходимся по таблице channels и добавляем кнопки
    for channel in channels:
        # создаем кнопку с названием канала
        keyboard.row(
            InlineKeyboardButton(text=channel.title, callback_data=ChannelPulseHistoryCBData(channel_id=channel.tg_id).pack())
        )

    return keyboard.as_markup()

def generate_ch_pulse_history_kb(summaries, channel_id:int, curr_page:int) -> InlineKeyboardMarkup:
    all_buttons = [
        InlineKeyboardButton(
            text=summary.summary_date.strftime("%m/%d/%Y"),
            callback_data=PulseInfoCBData(channel_id=summary.channel_id,
                                          post_id=summary.last_included_post_id).pack()
        )
        for summary in summaries
    ]
    keyboard = InlineKeyboardBuilder()

    # створюється grid 2х3 (2 колонки по 3 ряди)
    buttons_for_grid = 6
    start_index = curr_page * buttons_for_grid
    end_index = (curr_page+1) * buttons_for_grid

    keyboard.add(*all_buttons[start_index:end_index])
    keyboard.adjust(2)

    # Визначаємо максимальну кількість сторінок
    sum_number = len(summaries)
    max_pages = sum_number // buttons_for_grid

    # Ряд кнопок для перегортання сторінок списку
    turn_row = turn_buttons(channel_id=channel_id, current_page=curr_page, max_pages=max_pages)
    keyboard.row(*turn_row)

    keyboard.row(InlineKeyboardButton(text="Back to Channels", callback_data="history_list"))
    return keyboard.as_markup()

def turn_buttons(channel_id: int, current_page: int, max_pages: int) -> list[InlineKeyboardButton]:
    buttons = []
    if current_page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="← Prev", callback_data=TurnPageCBData(channel_id=channel_id, current_page=current_page - 1).pack()
            )
        )

    if current_page < max_pages:
        buttons.append(
            InlineKeyboardButton(
                text="Next →",
                callback_data=TurnPageCBData(channel_id=channel_id, current_page=current_page + 1).pack()
            )
        )

    return buttons