from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import and_

from Database.models.subscription import UserSubscription
from Database.models.channel import Channel

class UserSubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_sub_channels(self, user_id: int) -> list[Channel]:
        channels = (
            select(Channel)
            .join(UserSubscription, UserSubscription.channel_id == Channel.tg_id)
            .where(UserSubscription.user_id == user_id)
        )

        result = await self.__session.execute(channels)
        return result.scalars().all()

    async def user_subscribed_to_channel(self, user_id: int, channel_id: int) -> bool:
        check_query = select(UserSubscription).where(
            and_(
                UserSubscription.user_id == user_id,
                UserSubscription.channel_id == channel_id
            )
        )

        check_result = await self.__session.execute(check_query)
        if check_result.scalar_one_or_none():
            return True
        else:
            return False

    async def create_subscription(self, user_id: int, channel_id: int):
        subscription = UserSubscription(user_id=user_id, channel_id=channel_id)
        self.__session.add(subscription)
        await self.__session.commit()

    async def delete_subscription(self, user_id: int, channel_id: int):
        """
        Видаляє запис про підписку конкретного юзера на конкретний канал.
        Таблиця 'channels' залишається незмінною.
        """
        statement = delete(UserSubscription).where(
            and_(
                UserSubscription.user_id == user_id,
                UserSubscription.channel_id == channel_id
            )
        )
        await self.__session.execute(statement)
        await self.__session.commit()