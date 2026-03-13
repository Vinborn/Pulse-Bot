"""УПРАВЛЕНИЕ ВСЕЙ ЛОГИКОЙ"""

from aiogram import Dispatcher

from Handlers.start import router as start_router
from Handlers.add import router as add_router
from Handlers.channel_list import router as list_router
from Handlers.get_pulse import router as pulse_router
from Handlers.history import router as history_router

def register_routes(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(add_router)
    dp.include_router(list_router)
    dp.include_router(pulse_router)
    dp.include_router(history_router)
    print("All routes registered")