from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from Repositories.post import PostRepository
from Repositories.summary import SummaryRepository
from Repositories.user import UserRepository
from Repositories.channel import ChannelRepository
from Repositories.subscription import UserSubscriptionRepository

class DatabaseSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker) -> None:
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        async with self.session_maker() as session:
            data["user_repo"] = UserRepository(session)
            data["channel_repo"] = ChannelRepository(session)
            data["post_repo"] = PostRepository(session)
            data["summary_repo"] = SummaryRepository(session)
            data["subscription_repo"] = UserSubscriptionRepository(session)
            return await handler(event, data)