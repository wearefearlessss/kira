# Класс состояний
from aiogram.fsm.state import StatesGroup, State


class NoteStates(StatesGroup):
    awaiting_note = State()
    awaiting_tag = State()
    awaiting_tag_selection = State()
# Класс состояний для изменения заметки
class EditNoteState(StatesGroup):
    awaiting_new_text = State()


