from aiogram import F, Router, types

from Keyboard.post_collect_limit import post_limit_kb, PostLimitCBData

from Repositories.channel import ChannelRepository
from Repositories.post import PostRepository
from Repositories.subscription import UserSubscriptionRepository
from Repositories.summary import SummaryRepository

from scraper import collect_posts_from_channel, fetch_content_from_posts
from brain import make_digest

router = Router()

@router.message(F.text == "GET PULSE")
async def get_post_limit(message: types.Message, subscription_repo: UserSubscriptionRepository):
    user_id = message.from_user.id
    channels = await subscription_repo.get_sub_channels(user_id)

    if channels:
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
    final_report = ""

    for channel in channels:
        final_report += f"*{channel.title}*:\n"

        # Збираємо пости, кількість яких вказав юзер
        all_ids = await collect_posts_from_channel(channel_repo, post_repo, channel.tg_id, limit=callback_data.limit)

        # Знаходимо пости, які з них нові, а які вже оброблені
        new_ids = await post_repo.filter_unprocessed_posts(channel.tg_id, new_post_ids=all_ids)
        old_ids = [post_id for post_id in all_ids if post_id not in new_ids]

        # Обробляємо СТАРЕ
        if old_ids:
            # Дістаємо всі унікальні дайджести з оброблених постів
            summaries = await summary_repo.get_summaries_by_post_ids(old_ids)

            final_report += f"📜 _(From archive):_\n"
            for summary in summaries:
                final_report += (f"*{summary.topic}*\n"
                                 f"{summary.content}\n\n")

        # Обробляємо НОВЕ
        if new_ids:
            # Є нові пости, тому відправляємо їх до LLM
            # Отримуємо контент по списку нових постів
            raw_content = await fetch_content_from_posts(post_repo=post_repo, post_ids=new_ids)

            # Текстового контенту немає, переходимо до наступного каналу
            if not raw_content:
                continue

            # Отримуємо дайджест по контенту
            digest = await make_digest(channel_title=channel.title, raw_content=raw_content)

            # Обробляємо всі події в дайджесті
            events = digest["events"]
            if events:
                final_report += f"🔥 _Latest news:_\n"

                for event in events:
                    # Додаємо щойно створений дайджест події до повідомлення
                    final_report += (f"*{event["topic"]}*\n"
                                     f"{event["result"]}\n\n")

                # Додаємо всі дайджести всіх подій до бази
                await summary_repo.save_new_summaries(channel_id=channel.tg_id, events=events)

        final_report += "\n"

    # Отвечаем юзеру
    await update.message.edit_text(text=final_report, parse_mode="Markdown")