# states/language_state.py
from aiogram.fsm.state import StatesGroup, State

class LanguageState(StatesGroup):
    choose_language = State()
