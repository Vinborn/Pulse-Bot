from aiogram import Dispatcher

from Middleware.session import DatabaseSessionMiddleware
from Middleware.translate import TranslationMiddleware

def register_middleware(dp: Dispatcher, session_maker):
    dp.update.middleware(DatabaseSessionMiddleware(session_maker))
    dp.update.middleware(TranslationMiddleware())