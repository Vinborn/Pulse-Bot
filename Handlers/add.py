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
async def add(message: types.Message, state: FSMContext):
    await state.set_state(AddChannel.waiting_for_link)
    await message.answer(
        "Готовий розширити твій інформаційний потік!\n"
        "Надішліть мені посилання на Telegram-канал (наприклад, @channel_name або t.me/link)."
    )

# сработает ТОЛЬКО в состоянии ожидания ссылки
@router.message(AddChannel.waiting_for_link)
async def handle_channel_link(message: types.Message, state: FSMContext, channel_repo: ChannelRepository, subscription_repo: UserSubscriptionRepository):
    """ЛОГИКА ДОБАВЛЕНИЯ КАНАЛА В БАЗУ"""
    channel_match = re.search(CHANNEL_RE, message.text)

    if channel_match:
        link = channel_match.group(0)
        await message.answer(f"Почав обробку каналу...")

        # логика скрапера, надо винести в фоновою задачу
        await join_channel(link)
        title = await get_channel_title(link)
        channel_tg_id = await get_channel_id(link)
        user_id = message.from_user.id

        await channel_repo.create_or_update_channel(channel_id=channel_tg_id, tg_link=link, title=title)

        user_subscribed = await subscription_repo.user_subscribed_to_channel(user_id=user_id, channel_id=channel_tg_id)

        if not user_subscribed:
            await subscription_repo.create_subscription(user_id=user_id, channel_id=channel_tg_id)
            await message.answer("Канал успішно додано!")
        else:
            await message.answer("Канал вже існує!")

    else:
        await message.answer("Такого каналу не існує або він закритий!")

    # сбрасиваем состояние
    await state.clear()