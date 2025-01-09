from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import cursor, conn
from keyboards.keyboards import get_tags_keyboard, get_main_menu
from states.state import NoteStates, EditNoteState

router = Router()

# Начальное меню
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="создать заметку"), types.KeyboardButton(text="мои заметки")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="заметки")
    await message.answer(
        f"привет, <b>{message.from_user.full_name}</b>! я твой личный бот-дневник. ты можешь записывать свои заметки и добавлять теги.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

# Хэндлер для кнопки "создать заметку"
@router.message(F.text.lower() == "создать заметку")
async def create_note_start(message: types.Message, state: FSMContext):
    await message.answer("введите текст заметки:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(NoteStates.awaiting_note)



# Сохранение текста заметки
@router.message(NoteStates.awaiting_note)
async def save_note_text(message: types.Message, state: FSMContext):
    await state.update_data(note_text=message.text)
    await message.answer("выберите тег для заметки:", reply_markup=get_tags_keyboard())
    await state.set_state(NoteStates.awaiting_tag)

# Сохранение тега
@router.callback_query(NoteStates.awaiting_tag)
async def save_note_tag(callback: types.CallbackQuery, state: FSMContext):
    tag = callback.data
    data = await state.get_data()
    cursor.execute(

        "INSERT INTO notes (user_id, text, tag) VALUES (?, ?, ?)",
        (callback.from_user.id, data["note_text"], tag)
    )
    conn.commit()
    await callback.message.answer("заметка сохранена!", reply_markup=get_main_menu())
    await state.clear()

# Хэндлер для кнопки "мои заметки"
@router.message(F.text.lower() == "мои заметки")
async def select_tag_for_notes(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT DISTINCT tag FROM notes WHERE user_id = ?", (user_id,))
    tags = [row[0] for row in cursor.fetchall()]

    if not tags:
        await message.answer("у вас пока нет заметок.")
        return

    keyboard = InlineKeyboardBuilder()
    for tag in tags:
        keyboard.add(types.InlineKeyboardButton(text=tag, callback_data=f"view_{tag}"))

    await message.answer("выберите тег для просмотра заметок:", reply_markup=keyboard.as_markup())

# Просмотр заметок по тегу
@router.callback_query(F.data.startswith("view_"))
async def view_notes_by_tag(callback: types.CallbackQuery):
    tag = callback.data.split("_", maxsplit=1)[1]
    user_id = callback.from_user.id
    cursor.execute("SELECT id, text FROM notes WHERE user_id = ? AND tag = ?", (user_id, tag))
    notes = cursor.fetchall()

    if not notes:
        await callback.message.answer("заметок с этим тегом пока нет.")
        return

    for note_id, text in notes:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            types.InlineKeyboardButton(text="Изменить", callback_data=f"edit_{note_id}"),
            types.InlineKeyboardButton(text="Удалить", callback_data=f"delete_{note_id}")
        )
        await callback.message.answer(
            f"📌 {tag}\n\n{text}",
            reply_markup=keyboard.as_markup(),
            parse_mode=ParseMode.HTML
        )

# Удаление заметки
@router.callback_query(F.data.startswith("delete_"))
async def delete_note_callback(callback: types.CallbackQuery):
    note_id = int(callback.data.split("_")[1])
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    await callback.message.edit_text("заметка удалена.")
    await callback.answer()


# Обработка кнопки "Изменить"
@router.callback_query(F.data.startswith("edit_"))
async def edit_note_callback(callback: types.CallbackQuery, state: FSMContext):
    note_id = int(callback.data.split("_")[1])
    await state.update_data(note_id=note_id)
    await callback.message.answer("введите новый текст для заметки:")
    await state.set_state(EditNoteState.awaiting_new_text)

# Сохранение нового текста заметки
@router.message(EditNoteState.awaiting_new_text)
async def save_new_note_text(message: types.Message, state: FSMContext):
    new_text = message.text
    data = await state.get_data()
    note_id = data["note_id"]

    cursor.execute("UPDATE notes SET text = ? WHERE id = ?", (new_text, note_id))
    conn.commit()

    await message.answer("Заметка успешно обновлена!", reply_markup=get_main_menu())
    await state.clear()