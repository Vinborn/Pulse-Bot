from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

from Repositories.post import PostRepository
from Repositories.channel import ChannelRepository
from config import config_p

tg_client = TelegramClient('anon', config_p.api_id, config_p.api_hash)

async def join_channel(link: str):
    try:
        await tg_client(JoinChannelRequest(link))
    except ValueError:
        print(f"Failed to join channel {link}")

# получает текст постов из бази
async def fetch_text_from_channel(post_repo: PostRepository, channel_id: str):
    channel_texts = await post_repo.get_content_from_channel_id(channel_id)

    answer = ""
    if channel_texts:
        for text in channel_texts:
            if text:
                answer += f"{text}\n"
        return answer if answer else "No text in latest posts."
    else:
        return "Channel not found!"

# собирает пости из канала и добавляет в базу либо обновляет данние
async def collect_posts_from_channel(channel_repo: ChannelRepository, post_repo: PostRepository, channel_tg_id: int, limit: int=1):
    async for post in tg_client.iter_messages(channel_tg_id, limit=limit):
        await post_repo.create_or_update_post(post.peer_id.channel_id,
                                              post.id,
                                              post.message,
                                              post.date)
        # here is code to add/update channel last message id
        await channel_repo.set_last_message_id(channel_tg_id, post.id)


async def get_channel_title(channel_link: str):
    channel = await tg_client.get_entity(channel_link)
    return channel.title

async def get_channel_id(channel_link: str):
    channel = await tg_client.get_entity(channel_link)
    return channel.id

async def start_scraper():
    await tg_client.start()