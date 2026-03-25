import sys

from telethon import TelegramClient, errors
from telethon.tl.functions.channels import JoinChannelRequest

from Repositories.post import PostRepository
from Repositories.channel import ChannelRepository
from config import config_p

SESSION_NAME = config_p.session_name

tg_client = TelegramClient(session=SESSION_NAME, api_id=config_p.api_id, api_hash=config_p.api_hash)

async def join_channel(link: str):
    try:
        await tg_client(JoinChannelRequest(link))
        return None
    except Exception as e:
        return str(e)

# получает текст постов из бази
async def fetch_content_from_posts(post_repo: PostRepository, post_ids: list[int]) -> str:
    """Збирає текстовий контент зі списку постів, розділяючи мітками [POST ID]"""
    content = ""
    for post_id in post_ids:
        # Отримуємо контент з посту
        text = await post_repo.get_post_content(post_id)

        # Якщо немає тексту, то йдемо до наступного поста
        if text == "media":
            continue

        post_date = (await post_repo.get_datetime(post_id)).date()

        content += f"[POST ID {post_id} {post_date}]\n{text}\n"

    return content

# собирает пости из канала и добавляет в базу либо обновляет данние
async def collect_posts_from_channel(channel_repo: ChannelRepository, post_repo: PostRepository, channel_tg_id: int, limit: int) -> list[int]:
    async for ch_post in tg_client.iter_messages(channel_tg_id, limit=limit):
        if not ch_post.message:
            # Немає тексту значить це медіа (фото, відео, кружочки)
            await post_repo.create_or_update_post(
                channel_id=ch_post.peer_id.channel_id,
                tg_id=ch_post.id,
                content="media",
                created_at=ch_post.date
            )
        else:
            # Пост має текст! (й можливо медіа)
            await post_repo.create_or_update_post(
                channel_id=ch_post.peer_id.channel_id,
                tg_id=ch_post.id,
                content=ch_post.message,
                created_at=ch_post.date
            )
        # встановлюємо id останнього поста
        await channel_repo.set_last_message_id(channel_tg_id, ch_post.id)

    new_posts = await post_repo.get_posts_list(channel_tg_id, limit=limit)
    new_post_ids = [post.tg_id for post in new_posts]
    return new_post_ids

async def get_channel_title(channel_link: str):
    channel = await tg_client.get_entity(channel_link)
    return channel.title

async def get_channel_id(channel_link: str):
    channel = await tg_client.get_entity(channel_link)
    return channel.id

async def start_scraper():
    # Безпечно завершуємо роботу програми при помилці
    # (0 - успіх, 1 - помилка)
    try:
        # connect() просто встановлює TCP-з'єднання, нічого не запитуючи
        await tg_client.connect()

        # Перевіряємо, чи підхопився наш файл сесії
        if not await tg_client.is_user_authorized():
            print(f"Error: {SESSION_NAME}.session is not found or it is invalid.")
            sys.exit(1)

        print("Login successful!")
    except errors.FloodWaitError as e:
        print(f"FluidWaitError! Telegram asks you to wait {e.seconds}s.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)