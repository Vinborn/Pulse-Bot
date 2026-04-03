from aiogram import F, Router, types
from aiogram.types import InlineKeyboardMarkup

from Keyboard.history_list import generate_history_list_kb, ChannelPulseHistoryCBData, \
    generate_ch_pulse_history_kb, PulseInfoCBData, TurnPageCBData
from Repositories.subscription import UserSubscriptionRepository
from Repositories.summary import SummaryRepository

router = Router()

@router.callback_query(F.data == "history_list")
@router.message(F.text.upper() == "HISTORY")
async def history(update: types.Message | types.CallbackQuery, subscription_repo: UserSubscriptionRepository):
    user_id = update.from_user.id
    # получаем список каналов
    channels = await subscription_repo.get_sub_channels(user_id)

    if isinstance(update, types.Message):
        if channels:
            await update.answer(
                "Це архів знань. Тут зібрані всі дайджести, які я готував для тебе раніше. Що саме хочеш переглянути?",
                reply_markup=generate_history_list_kb(channels)
            )
        else:
            await update.answer("Список каналів порожній! Спочатку додайте канал.")
    # или юзер нажал кнопку "Back"
    else:
        await update.message.edit_text(
            "Це архів знань. Тут зібрані всі дайджести, які я готував для тебе раніше. Що саме хочеш переглянути?",
            reply_markup=generate_history_list_kb(channels)
        )
        await update.answer()

@router.callback_query(TurnPageCBData.filter()) # когда юзер нажал кнопку Next/Prev
@router.callback_query(ChannelPulseHistoryCBData.filter()) # когда юзер нажал на канал из списка
async def channel_pulse_history_list(callback_query: types.CallbackQuery, callback_data: ChannelPulseHistoryCBData | TurnPageCBData, summary_repo: SummaryRepository):
    summaries = await summary_repo.get_summaries_by_channel_id(callback_data.channel_id)
    current_page = 0

    if isinstance(callback_data, TurnPageCBData):
        current_page = callback_data.current_page

    if summaries:
        await callback_query.message.edit_text(
            "Всі дайджести відсортованні по даті створення. Яку дату хочеш переглянути?",
            reply_markup=generate_ch_pulse_history_kb(summaries=summaries, channel_id=callback_data.channel_id, curr_page=current_page)
        )
        await callback_query.answer()
    else:
        await callback_query.message.edit_text("Дайджестів поки немає! Створіть нові дайджести")
        await callback_query.answer()

@router.callback_query(PulseInfoCBData.filter()) # когда юзер нажал на дату дайджеста из списка дайджестов
async def pulse_info(callback_query: types.CallbackQuery, callback_data: PulseInfoCBData, summary_repo: SummaryRepository):
    summary = await summary_repo.get_summary_by_post_id(callback_data.post_id)

    await callback_query.message.edit_text(
        f"📌 <b>«{summary.topic}»</b>\n"
        f"{summary.content}\n"
        f"📅 <i>Дата дайджесту: {summary.summary_date.strftime('%m-%d-%Y')}</i>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Back",
                        callback_data=f"ch_pulse_history:{callback_data.channel_id}"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )
    await callback_query.answer()