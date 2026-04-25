from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from Keyboard.menu import main_menu_kb
from Repositories.user import UserRepository

router = Router()

@router.message(Command("start"))
async def start_bot(message: types.Message, state: FSMContext, user_repo: UserRepository, translator: callable):
    """ЛОГИКА КОМАНДИ СТАРТ"""
    await user_repo.create_or_update_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        tg_lang=message.from_user.language_code,
        ui_lang=message.from_user.language_code
    )
    await state.clear()
    await message.answer(text=translator("start"), reply_markup=main_menu_kb())