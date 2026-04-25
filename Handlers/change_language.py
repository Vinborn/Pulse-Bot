from aiogram import F, Router, types
from Keyboard.change_language import change_language_kb

from Repositories.user import UserRepository

router = Router()

@router.message(F.text == "LANGUAGE")
async def languages(update: types.Message, translator:callable):
    await update.answer(
        f"📜 {translator("settings")["change_language"]}",
        reply_markup=change_language_kb(),
    )

@router.callback_query(F.data.contains("lan_"))
async def change_language(update: types.CallbackQuery, user_repo: UserRepository, translator:callable):
    new_language = update.data.split("_")[1]
    user_id = update.from_user.id

    await user_repo.set_language(tg_id=user_id, new_language=new_language)

    await update.answer(translator("settings")["change_language_success"])