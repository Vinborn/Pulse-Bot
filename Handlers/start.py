from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from Keyboard.menu import main_menu_kb
from Repositories.user import UserRepository

router = Router()

@router.message(Command("start"))
async def start_bot(message: types.Message, state: FSMContext, user_repo: UserRepository):
    """ЛОГИКА КОМАНДИ СТАРТ"""
    await user_repo.create_or_update_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.language_code
    )
    await state.clear()
    await message.answer(
      f"Привіт! Я — Pulse Bot 🤖.\n"
      f"Я допоможу тобі тримати руку на пульсі головних новин без зайвого шуму.\n"
      f"Просто додай канал, і я почну готувати для тебе дайджест найцікавішого!",
        reply_markup=main_menu_kb()
    )