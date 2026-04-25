import re
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from scraper import get_channel_title, get_channel_id, join_channel

from Repositories.subscription import UserSubscriptionRepository
from Repositories.channel import ChannelRepository

from states import AddChannel

router = Router()

# вытянет название канала из "https://t.me/channel_name" или "@channel_name"
CHANNEL_RE = r"(?:https?://t\.me/|@)([a-zA-Z0-9_]{5,})"

@router.message(F.text == "ADD")
async def add(message: types.Message, state: FSMContext, translator: callable):
    await state.set_state(AddChannel.waiting_for_link)
    await message.answer(
        f"↔️ {translator("add")["wait_for_link"]}"
    )

# сработает ТОЛЬКО в состоянии ожидания ссылки
@router.message(AddChannel.waiting_for_link)
async def handle_channel_link(message: types.Message, state: FSMContext, channel_repo: ChannelRepository, subscription_repo: UserSubscriptionRepository, translator: callable):
    """ЛОГИКА ДОБАВЛЕНИЯ КАНАЛА В БАЗУ"""
    # Знаходимо посилання на канал
    channel_match = re.search(CHANNEL_RE, message.text)

    if channel_match:
        link = channel_match.group(0)
        await message.answer(translator("add")["process"])

        join = await join_channel(link)
        if join:
            # Перевіряємо чи можливо зайти на канал
            await message.answer(translator("add")["not_username"])
            await state.clear()
            return

        title = await get_channel_title(link)
        channel_tg_id = await get_channel_id(link)
        user_id = message.from_user.id

        # Додаємо в таблицю каналів цей канал
        await channel_repo.create_or_update_channel(channel_id=channel_tg_id, tg_link=link, title=title)

        # Перевіряємо чи підписан юзер на цей канал
        user_subscribed = await subscription_repo.user_subscribed_to_channel(user_id=user_id, channel_id=channel_tg_id)

        if not user_subscribed:
            await subscription_repo.create_subscription(user_id=user_id, channel_id=channel_tg_id)
            await message.answer(translator("add")["add_success"])
        else:
            await message.answer(translator("add")["exists"])

    else:
        await message.answer(translator("add")["not_exist_or_private"])

    # сбрасиваем состояние
    await state.clear()