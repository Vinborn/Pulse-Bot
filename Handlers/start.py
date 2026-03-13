"""ЛОГИКА КОМАНДИ СТАРТ"""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from Keyboard.menu import main_menu_kb
from Repositories.user import UserRepository

router = Router()

@router.message(Command("start"))
async def start_bot(message: types.Message, state: FSMContext, user_repo: UserRepository): # тип переменной которой ми ожидаем
    await user_repo.create_or_update_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.language_code
    )
    await state.clear()
    await message.answer(
      f"Hi, {message.from_user.full_name}!"
      f"\nI'm a Pulse Bot, what do you need next?",
        reply_markup=main_menu_kb()
    )