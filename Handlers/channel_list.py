"""ЛОГИКА ВЗАЕМОДЕЙСТВИЯ СО СПИСКОМ КАНАЛОВ"""
from aiogram import F, Router, types
from aiogram.types import InlineKeyboardMarkup

from Keyboard.channel_list import generate_channel_list_kb, ChannelInfoCBData, ChannelDeleteCBData
from Repositories.channel import ChannelRepository
from Repositories.subscription import UserSubscriptionRepository

router = Router()

@router.callback_query(F.data == "channel_list")
@router.message(F.text.upper() == "CHANNEL LIST")
async def channel_list(update: types.Message | types.CallbackQuery, subscription_repo: UserSubscriptionRepository):
    user_id = update.from_user.id
    # получаем список каналов
    channels = await subscription_repo.get_sub_channels(user_id)

    # если юзер из главного меню отправил сообщение "CHANNEL LIST"
    if isinstance(update, types.Message):
        if channels:
            await update.answer(
            "Channel List:",
                reply_markup=generate_channel_list_kb(channels)
            )
        else:
            await update.answer("Channel list is empty! Add channel first!")
    # или юзер нажал кнопку "Back"
    else:
        await update.message.edit_text(
            "Channel List:",
            reply_markup=generate_channel_list_kb(channels)
        )

@router.callback_query(ChannelInfoCBData.filter()) # когда юзер нажал на канал из списка
async def channel_info(callback: types.CallbackQuery, callback_data: ChannelInfoCBData, channel_repo: ChannelRepository):
    # достаем нужний канал по id
    channel = await channel_repo.get_channel_by_id(callback_data.channel_id)

    # переписиваем прошлое сообщение от бота, информацией о конкретном канале
    await callback.message.edit_text(
        text=f"Title: «{channel.title}»\nLink: {channel.tg_link}",
        # создаеться кнопка назад, которая возвращет тебя к основному листу
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Back",
                        callback_data="channel_list"
                    )
                ]
            ]
        )
    )

@router.callback_query(ChannelDeleteCBData.filter()) # когда юзер нажал на крестик для удаления определеного канала
async def delete_confirm(callback: types.CallbackQuery, callback_data: ChannelDeleteCBData, channel_repo: ChannelRepository):
    # узнаем какой канал удалить
    channel = await channel_repo.get_channel_by_id(callback_data.channel_id)

    # удостоверяемся что юзер нажал не случайно
    await callback.message.edit_text(
        text=f"Do you really want to delete «{channel.title}»?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Confirm",
                        callback_data=f"confirm_del_{callback_data.channel_id}"
                    ),
                    types.InlineKeyboardButton(
                        text="Back",
                        callback_data="channel_list"
                    )
                ]
            ]
        )
    )

@router.callback_query(F.data.startswith("confirm_del_")) # когда юзер нажал на кнопку Confirm
async def channel_delete(callback: types.CallbackQuery, subscription_repo: UserSubscriptionRepository):
    ch_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    # удаляем канал из User Subscriptions, не затрагивая таблицу "channels"
    await subscription_repo.delete_subscription(user_id=user_id, channel_id=ch_id)
    await callback.answer("Channel has been successfully deleted!")

    new_channels = await subscription_repo.get_sub_channels(user_id)

    # показиваем новий список каналов, если список не пустой
    if new_channels:
        await callback.message.edit_text(
            "Channel List:",
            reply_markup=generate_channel_list_kb(new_channels))

    # а если нету ничего в списке, то просим добавить канал
    else:
        await callback.message.edit_text("Channel list is empty! Add channel first!")