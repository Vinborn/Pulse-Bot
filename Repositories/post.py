from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Database.models.post import Post
from Database.models.summary_post import SummaryPost

class PostRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_post_content(self, post_id: int) -> str:
        statement = select(Post.content).where(post_id == Post.tg_id)
        return await self.__session.scalar(statement)

    async def get_post_by_tg_id(self, tg_id: int) -> Post:
        statement = select(Post).where(tg_id == Post.tg_id)
        return await self.__session.scalar(statement)

    async def get_datetime(self, tg_id: int) -> datetime:
        statement = select(Post.created_at).where(Post.tg_id == tg_id)
        result = await self.__session.execute(statement)
        return result.scalar_one_or_none()

    async def create_or_update_post(self, channel_id: int, tg_id: int, content: str, created_at: datetime):
        post = await self.get_post_by_tg_id(tg_id)

        if not post:
            await self.create_post(channel_id, tg_id, content, created_at)
        else:
            post.content = content

        await self.__session.commit()

    async def create_post(self, channel_id: int, tg_id: int, content: str, created_at: datetime):
        post = Post(channel_id=channel_id,
                    tg_id=tg_id,
                    content=content,
                    created_at=created_at)
        self.__session.add(post)

    async def get_posts_list(self, channel_id: int, limit: int) -> list[Post]:
        statement = select(Post).where(channel_id == Post.channel_id).limit(limit).order_by(Post.created_at.desc())
        result = await self.__session.execute(statement)
        return result.scalars().all()