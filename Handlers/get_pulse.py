from aiogram import F, Router, types

from Keyboard.post_collect_limit import post_limit_kb, PostLimitCBData

from Repositories.channel import ChannelRepository
from Repositories.post import PostRepository
from Repositories.subscription import UserSubscriptionRepository
from Repositories.summary import SummaryRepository
from Repositories.user import UserRepository

from scraper import collect_posts_from_channel, fetch_content_from_posts
from AI.brain import make_digest

router = Router()

@router.message(F.text == "GET PULSE")
async def get_post_limit(message: types.Message, subscription_repo: UserSubscriptionRepository, translator: callable):
    user_id = message.from_user.id
    channels = await subscription_repo.get_sub_channels(user_id)

    if channels:
        await message.answer(
            text=f"👇{translator("get_pulse")["post_limit"]}",
            reply_markup=post_limit_kb(translator)
        )
    else:
        await message.answer(translator("get_pulse")["empty"])

@router.callback_query(PostLimitCBData.filter())
async def get_pulse(
        callback: types.CallbackQuery,
        callback_data: PostLimitCBData,
        channel_repo: ChannelRepository,
        post_repo: PostRepository,
        summary_repo: SummaryRepository,
        subscription_repo: UserSubscriptionRepository,
        user_repo: UserRepository,
        translator: callable
):
    user_id = callback.from_user.id

    user_lang = await user_repo.get_language(user_id)
    channels = await subscription_repo.get_sub_channels(user_id)

    await callback.answer(translator("get_pulse")["process"])
    report_parts = []

    for channel in channels:
        report_parts.append(f"📌  <b>{channel.title}</b>:",)

        # Збираємо пости, кількість яких вказав юзер
        all_ids = await collect_posts_from_channel(channel_repo, post_repo, channel.tg_id, limit=callback_data.limit)

        cache_summaries, new_summaries = await get_or_create_summaries(summary_repo=summary_repo, post_repo=post_repo, channel_id=channel.tg_id, channel_title=channel.title, all_ids=all_ids, user_lang=user_lang)

        # Показуємо юзеру дайджести з БД
        if cache_summaries:
            report_parts.append(f"📜 <i>({translator("get_pulse")["archive"]}):</i>")
            for cache_summary in cache_summaries:
                report_parts.append(f" • <b>{cache_summary.topic}</b>\n"
                                    f"{cache_summary.content}\n")

        # Показуємо юзеру нові дайджести
        if new_summaries:
            report_parts.append(f"🔥 <i>{translator("get_pulse")["latest"]}</i>")
            for new_summary in new_summaries:
                report_parts.append(f" • <b>{new_summary.get("topic")}</b>\n"
                                    f"{new_summary.get("result")}\n")

        # додає доп відступ між дайджестами каналів
        report_parts.append('')

    final_report = "\n".join(report_parts)

    # Додаємо підпис бота
    final_report += f"⚡<i>{translator("get_pulse")["signature"]}</i>"

    # Отвечаем юзеру
    await callback.message.edit_text(text=final_report, parse_mode="HTML")


async def get_or_create_summaries(
        summary_repo: SummaryRepository,
        post_repo: PostRepository,
        channel_id: int,
        channel_title: str,
        all_ids: list[int],
        user_lang: str
):
    """Для кожного поста/групи постів видати дайджест (готовий чи створити новий)"""
    # Дістаємо всі унікальні дайджести з БД
    cache_ids = await summary_repo.get_cache_post_ids(post_ids=all_ids, user_lang=user_lang)
    cache_summaries = await summary_repo.get_summaries_by_post_ids(post_ids=cache_ids, user_lang=user_lang)

    # Знаходимо пости, які з них нові
    new_ids = [new_id for new_id in all_ids if new_id not in cache_ids]

    new_summaries: list[dict[str, str]] = []

    # Обробляємо НОВЕ
    if new_ids:
        # Отримуємо контент по списку id нових постів
        raw_content = await fetch_content_from_posts(
            post_repo=post_repo,
            post_ids=new_ids
        )

        # Контент має текст
        if raw_content:
            # Отримуємо дайджест по контенту
            digest = await make_digest(
                channel_title=channel_title,
                raw_content=raw_content,
                lang=user_lang
            )

            # Обробляємо всі події в дайджесті
            events = digest.get("events", [])

            if events:
                # Додаємо всі дайджести всіх подій до бази
                await summary_repo.save_new_summaries(
                    channel_id=channel_id,
                    user_lang=user_lang,
                    events=events
                )

                new_summaries = events

    # Повертаємо кортеж в якому є старі та нові дайджести
    return cache_summaries, new_summaries