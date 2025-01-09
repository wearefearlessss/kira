# Получение клавиатуры с тегами
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_tags_keyboard():
    tags = ["работа💼", "отдых🏖️", "учёба📓", "дела🧹", "идеи💡", "мысли💭", "важное⭐"]
    keyboard = InlineKeyboardBuilder()

    for i in range(0, len(tags), 2):
        row = tags[i:i + 2]
        keyboard.row(*[types.InlineKeyboardButton(text=tag, callback_data=tag) for tag in row])

    keyboard.add(types.InlineKeyboardButton(text="другое", callback_data="другое"))
    return keyboard.as_markup()

# Главное меню
def get_main_menu():
    kb = [
        [types.KeyboardButton(text="создать заметку"), types.KeyboardButton(text="мои заметки")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)