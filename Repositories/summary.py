from datetime import datetime
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Database.models.summary import Summary
from Database.models.summary_post import SummaryPost
from Database.models.post import Post

class SummaryRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_summary(self, channel_id: int, topic: str, content: str, user_lang: str, last_included_post_id: int, summary_date: date, created_at: datetime):
        summary = Summary(
            channel_id=channel_id,
            topic=topic,
            content=content,
            language=user_lang,
            last_included_post_id=last_included_post_id,
            summary_date=summary_date,
            created_at=created_at
        )
        self.__session.add(summary)
        return summary

    async def get_summary_by_post_id(self, post_id: int, user_lang: str) -> Summary | None:
        statement = select(Summary).where(Summary.last_included_post_id == post_id, Summary.language == user_lang)
        result = await self.__session.execute(statement)
        return result.scalar()

    async def get_summaries_by_channel_id(self, channel_id: int, user_lang: str) -> list[Summary]:
        statement = select(Summary).where(Summary.channel_id == channel_id, Summary.language == user_lang).order_by(Summary.summary_date.desc())
        result = await self.__session.execute(statement)
        return result.scalars().all()

    async def get_summaries_by_post_ids(self, post_ids: list[int], user_lang: str) -> list[Summary]:
        """Повертає унікальний список Summary для списку ID постів."""
        if not post_ids:
            return []

        statement = (
            select(Summary)
            # Приєднуємо таблицю зв'язків SummaryPost
            .join(SummaryPost)
            # Фільтруємо списком постів
            .where(
                Summary.language == user_lang,
                Summary.last_included_post_id.in_(post_ids)
            )
            .distinct()
        )

        result = await self.__session.execute(statement)

        return result.scalars().all()

    async def save_new_summaries(self, channel_id: int, user_lang: str, events: list[dict]):
        """
        Атомарно зберігає нові дайджести та створює зв'язки з усіма відповідними постами.
        """
        all_summaries = []
        for event in events:
            # Беремо дату івента (YYYY-MM-DD)
            try:
                event_date = datetime.strptime(event["event_date"], '%Y-%m-%d')
            except ValueError:
                event_date = datetime.now()

            # Збираємо список int ID постів з івенту
            post_ids = [int(post) for post in event["list"]]
            # Отримуємо останній ID поста що міститься в дайджесті
            last_included_post_id = (max(post_ids))

            # Створюємо об'єкт дайджесту
            summary = await self.create_summary(channel_id=channel_id, topic=event["topic"], content=event["result"], user_lang=user_lang, last_included_post_id=last_included_post_id, summary_date=event_date, created_at=datetime.now())
            # Виконуємо flush, щоб отримати ID дайджесту, не закриваючи транзакцію
            await self.__session.flush()

            # Знаходимо Telegram ID постів у нашій БД
            statement = select(Post.tg_id).where(
                Post.channel_id == channel_id,
                Post.tg_id.in_(post_ids)
            )
            result = await self.__session.execute(statement)
            db_post_ids = result.scalars().all()

            # Створюємо записи зв'язків
            summary_links = [
                SummaryPost(summary_id=summary.id, post_id=p_id)
                for p_id in db_post_ids
            ]

            # Додаємо зв'язки івенту в список всіх зв'язків
            all_summaries.extend(summary_links)
        self.__session.add_all(all_summaries)
        await self.__session.commit()
