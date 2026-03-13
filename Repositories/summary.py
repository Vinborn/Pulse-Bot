from datetime import datetime
from datetime import date

from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from Database.models.summary import Summary

class SummaryRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_summary_by_post_id(self, post_id: int) -> Summary:
        statement = select(Summary).where(Summary.last_included_post_id == post_id)
        return await self.__session.scalar(statement)

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

    async def get_summaries_by_channel_id(self, channel_id: int) -> ScalarResult[Summary]:
        statement = select(Summary).where(Summary.channel_id == channel_id)
        return await self.__session.scalars(statement)

    # async def get_latest_summary(self, channel_id: int) -> Summary:
    #     statement = (
    #         select(Summary)
    #         .where(Summary.channel_id == channel_id)
    #         .order_by(Summary.summary_date.desc())
    #         .limit(1)
    #     )
    #     return await self.__session.scalar(statement)