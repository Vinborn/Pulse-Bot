import asyncio
from aiogram import Bot, Dispatcher
from Handlers import register_routes
from Middleware import register_middleware

from scraper import start_scraper
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import config_p

async def main():
    bot = Bot(token=config_p.bot_token) # обращение к тг боту с помощью токена
    dp = Dispatcher() # Dispatcher - Распределяет команди телеграм бота по функциям телеграм сервера (єто как регулировщик на дороге)

    # создаем базу даних
    engine = create_async_engine(url=config_p.db_url)

    # session_maker создает сессии для чтения даних из бази
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # middleware - проміжна програма, що може налаштувавати обробників (handlers) у багатьох точках процесу обробки
    register_middleware(dp, session_maker)
    register_routes(dp)

    await start_scraper()

    await dp.start_polling(bot)

if __name__ == '__main__': # если ми запускаем файл с именем main, то только тогда запускаеться бот
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is stopped!")