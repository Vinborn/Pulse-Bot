from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Database.models.channel import Channel

class ChannelRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_list(self) -> list[Channel]:
        statement = select(Channel).order_by(Channel.title)
        result = await self.__session.scalars(statement)
        return result.all()

    async def get_channel_by_id(self, channel_id: int) -> Channel:
        statement = select(Channel).where(Channel.tg_id == channel_id)
        return await self.__session.scalar(statement)

    async def create_channel(self, channel_id: int, tg_link: str, title: str):
        channel = Channel(tg_id=channel_id, tg_link=tg_link, title=title)
        self.__session.add(channel)

    async def create_or_update_channel(self, channel_id: int, tg_link: str, title: str):
        channel = await self.get_channel_by_id(channel_id)

        if not channel:
            await self.create_channel(channel_id, tg_link, title)
        else:
            channel.title = title
            channel.link = tg_link

        await self.__session.commit()

    async def set_last_message_id(self, channel_id: int, message_id: int):
        channel = await self.get_channel_by_id(channel_id)
        if not channel.last_message_id:
            channel.last_message_id = message_id
        elif message_id > channel.last_message_id:
            channel.last_message_id = message_id

        await self.__session.commit()