from datetime import datetime
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Database.models.summary import Summary
from Database.models.summary_post import SummaryPost

class SummaryRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_summary(self, channel_id: int, topic: str, content: str, last_included_post_id: int, summary_date: date, created_at: datetime):
        summary = Summary(
            channel_id=channel_id,
            topic=topic,
            content=content,
            last_included_post_id=last_included_post_id,
            summary_date=summary_date,
            created_at=created_at
        )
        self.__session.add(summary)
        await self.__session.commit()

    async def get_summary_by_post_id(self, post_id: int) -> Summary | None:
        statement = select(Summary).where(Summary.last_included_post_id == post_id)
        result = await self.__session.execute(statement)
        return result.scalar()

    async def get_summaries_by_channel_id(self, channel_id: int) -> list[Summary]:
        statement = select(Summary).where(Summary.channel_id == channel_id)
        result = await self.__session.execute(statement)
        return result.scalars().all()

    async def get_summaries_by_post_ids(self, post_ids: list[int]) -> list[Summary]:
        """Повертає унікальний список Summary для списку ID постів."""
        if not post_ids:
            return []

        statement = (
            select(Summary)
            # Приєднуємо таблицю зв'язків SummaryPost
            .join(SummaryPost)
            # Фільтруємо списком постів
            .where(Summary.last_included_post_id.in_(post_ids))
            .distinct()
        )

        result = await self.__session.execute(statement)

        return result.scalars().all()