from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Database.models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_user_by_tg_id(self, tg_id: int):
        statement = select(User).where(User.tg_id == tg_id)
        return await self.__session.scalar(statement)

    # создаем юзера или обновляем данние
    async def create_or_update_user(self, tg_id: int, username: str, language: str):
        # получаем из бази тг айди изера
        user = await self.get_user_by_tg_id(tg_id)

        # если юзера нету в базе, создаем его
        if not user:
            await self.create_user(tg_id, username, language)
        else:
            user.username = username
            user.language = language

        await self.__session.commit()

    # создаем юзера используя класс User и добавляем его в базу
    async def create_user(self, tg_id: int, username: str, language: str) -> Any:
        user = User(tg_id=tg_id, username=username, language=language)
        self.__session.add(user)