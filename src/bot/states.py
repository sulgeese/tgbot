from aiogram.fsm.state import StatesGroup, State


class StepsForm(StatesGroup):
    GET_TITLE = State()
    GET_DATE = State()
    GET_TEXT = State()
    GET_MENTION = State()
    WAITING_CONFIRM = State()
