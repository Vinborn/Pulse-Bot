"""КНОПКИ ДЛЯ ГЛАВНОГО МЕНЮ"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb():
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text='GET PULSE'), # кнопка для дайджеста канала/каналов
                KeyboardButton(text='HISTORY') # Кнопка для просмотра всех предидущих дайджестов для всех каналов
            ],
            [KeyboardButton(text='ADD')], # Добавить канал/канали
            [KeyboardButton(text='CHANNEL LIST')] # Управление каналами
        ]
    )