from aiogram import F, Router, types
from aiogram.types import InlineKeyboardMarkup

from Keyboard.history_list import generate_history_list_kb, ChannelPulseHistoryCBData, \
    generate_channel_pulse_history_kb, PulseInfoCBData
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
                "Channel List:",
                reply_markup=generate_history_list_kb(channels)
            )
        else:
            await update.answer("Channel list is empty! Add channel first!")
    # или юзер нажал кнопку "Back"
    else:
        await update.message.edit_text(
            "Channel List:",
            reply_markup=generate_history_list_kb(channels)
        )

@router.callback_query(ChannelPulseHistoryCBData.filter()) # когда юзер нажал на канал из списка
async def channel_pulse_history_list(callback_query: types.CallbackQuery, callback_data: ChannelPulseHistoryCBData, summary_repo: SummaryRepository):
    summaries = await summary_repo.get_summaries_by_channel_id(callback_data.channel_id)

    if summaries:
        await callback_query.message.edit_text(
            "Pulse History:",
            reply_markup=generate_channel_pulse_history_kb(summaries),
        )
    else:
        await callback_query.message.edit_text("Pulse history is empty! Get Pulse first!")


@router.callback_query(PulseInfoCBData.filter()) # когда юзер нажал на дату дайджеста из списка дайджестов
async def pulse_info(callback_query: types.CallbackQuery, callback_data: PulseInfoCBData, summary_repo: SummaryRepository):
    summary = await summary_repo.get_summary_by_post_id(callback_data.post_id)

    await callback_query.message.edit_text(
        f"**Topic: «{summary.topic}»**\n"
        f"*Content*: {summary.content}\n"
        f"Pulse date: {summary.summary_date.strftime('%m-%d-%Y')}",
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
        parse_mode="Markdown"
    )

