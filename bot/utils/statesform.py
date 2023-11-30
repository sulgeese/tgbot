from aiogram.fsm.state import StatesGroup, State


class StepsForm(StatesGroup):
    GET_DATE = State()
    GET_TEXT = State()
    WAITING_CONFIRM = State()