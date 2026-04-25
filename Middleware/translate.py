from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, Update, CallbackQuery

from translate_manager import translate_manager

class TranslationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Дізнаємось id користувача
        user_id = -1
        if type(event.message) == Message:
            user_id = event.message.from_user.id
        elif type(event.callback_query) == CallbackQuery:
            user_id = event.callback_query.from_user.id

        # Дізнаємось мову користувача
        user_repo = data['user_repo']
        user_lang = await user_repo.get_language(user_id)

        # Якщо мова користувача немає в списку, тоді ставимо по дефолту 'en'
        if user_lang not in ['ukr', 'en', 'ru']:
            user_lang = 'en'

        def translate(key):
            return translate_manager.get(key, user_lang)

        data['translator'] = translate

        return await handler(event, data)