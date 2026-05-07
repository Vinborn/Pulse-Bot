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
    final_report = ""

    for channel in channels:
        final_report += f"📌  <b>{channel.title}</b>:\n"

        # Збираємо пости, кількість яких вказав юзер
        all_ids = await collect_posts_from_channel(channel_repo, post_repo, channel.tg_id, limit=callback_data.limit)

        # Знаходимо пости, які з них нові, а які вже оброблені
        new_ids = await post_repo.filter_unprocessed_posts(channel_id=channel.tg_id, all_ids=all_ids)
        cached_ids = [post_id for post_id in all_ids if post_id not in new_ids]

        # Обробляємо СТАРЕ
        if cached_ids:
            # Дістаємо всі унікальні дайджести з оброблених постів
            summaries = await summary_repo.get_summaries_by_post_ids(post_ids=cached_ids, user_lang=user_lang)

            final_report += f"📜 <i>({translator("get_pulse")["archive"]}):</i>\n"
            for summary in summaries:
                final_report += (f" • <b>{summary.topic}</b>\n"
                                 f"{summary.content}\n\n")

        # Обробляємо НОВЕ
        if new_ids:
            # Є нові пости, тому відправляємо їх до LLM
            # Отримуємо контент по списку нових постів
            raw_content = await fetch_content_from_posts(post_repo=post_repo, post_ids=new_ids)

            # Текстового контенту немає, переходимо до наступного каналу
            if not raw_content:
                final_report += "There is no text"
                continue

            # Отримуємо дайджест по контенту
            digest = await make_digest(channel_title=channel.title, raw_content=raw_content, lang=user_lang)

            # Обробляємо всі події в дайджесті
            events = digest["events"]
            if events:
                final_report += f"🔥 <i>{translator("get_pulse")["latest"]}</i>\n"

                for event in events:
                    # Додаємо щойно створений дайджест події до повідомлення
                    final_report += (f" • <b>{event["topic"]}</b>\n"
                                     f"{event["result"]}\n\n")

                # Додаємо всі дайджести всіх подій до бази
                await summary_repo.save_new_summaries(channel_id=channel.tg_id, user_lang=user_lang, events=events)

        final_report += '\n'

    final_report += f"<i>{translator("get_pulse")["signature"]}</i>⚡"

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