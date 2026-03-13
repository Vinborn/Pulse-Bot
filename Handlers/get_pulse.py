from datetime import datetime

from aiogram import F, Router, types

from Keyboard.post_collect_limit import post_limit_kb, PostLimitCBData

from Repositories.channel import ChannelRepository
from Repositories.post import PostRepository
from Repositories.subscription import UserSubscriptionRepository
from Repositories.summary import SummaryRepository

from scraper import collect_posts_from_channel, fetch_text_from_channel
from brain import summary

router = Router()

@router.message(F.text == "GET PULSE")
async def get_post_limit(message: types.Message, channel_repo: ChannelRepository):
    channels = await channel_repo.get_list()
    channels = channels.all()

    if len(channels) > 0:
        await message.answer(
            text="Select the number of recent posts to analyze:",
            reply_markup=post_limit_kb()
        )
    else:
        await message.answer("No channels found! Please add a channel first.")

@router.callback_query(PostLimitCBData.filter())
async def get_pulse(
        update: types.CallbackQuery,
        callback_data: PostLimitCBData,
        channel_repo: ChannelRepository,
        post_repo: PostRepository,
        summary_repo: SummaryRepository,
        subscription_repo: UserSubscriptionRepository
):
    user_id = update.from_user.id
    channels = await subscription_repo.get_sub_channels(user_id)

    await update.answer("Getting data...")
    output_text = ""
    for channel in channels:
        # Собираем количество постов, которие указал юзер
        await collect_posts_from_channel(channel_repo, post_repo, channel.tg_id, limit=callback_data.limit)

        last_msg_id = channel.last_message_id

        # Проверяем, есть ли уже готовый дайджест в БД
        existing_summary = await summary_repo.get_summary_by_post_id(last_msg_id)

        if existing_summary is not None:
            if existing_summary.last_included_post_id == last_msg_id:
                # Добавляем уже готовий дайджест в сообщение
                output_text += (f"(From archive) **{channel.title}**\n"
                    f"*{existing_summary.topic}*:\n"
                    f"{existing_summary.content}\n\n")
                continue  # Переходим к следующему каналу, не дергая ИИ

        # Если id последнего поста устарело или по id конкретного поста нету дайджеста, то идем обновлять/добавлять данние
        raw_post_text = await fetch_text_from_channel(post_repo, channel.tg_id)
        digest = await summary(channel_title=channel.title, post_text=raw_post_text)

        time = await post_repo.get_datetime_by_tg_id(last_msg_id)

        # Сохраняем в базу
        await summary_repo.create_summary(
            channel_id=channel.tg_id,
            topic=digest["topic"],
            content=digest["result"],
            last_included_post_id=last_msg_id,
            summary_date=time,
            created_at=datetime.now()
        )
        # Добавляем только что созданий дайджест в сообщение
        output_text += (f"**{channel.title}**\n"
            f"*{digest["topic"]}*:\n"
            f"{digest["result"]}\n\n")

    # Отвечаем юзеру
    await update.message.edit_text(text=output_text, parse_mode="Markdown")